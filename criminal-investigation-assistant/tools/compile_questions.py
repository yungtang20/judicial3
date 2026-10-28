"""Deterministically compile allow-listed Markdown question sources to JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "question_sources"
RUNTIME_ROOT = ROOT / "data" / "runtime"
MANIFEST_PATH = SOURCE_ROOT / "families.manifest.json"
BANK_PATH = RUNTIME_ROOT / "question_bank.json"
SOURCE_LOCK_PATH = RUNTIME_ROOT / "source_manifest.json"
COVERAGE_PATH = RUNTIME_ROOT / "route_coverage.json"
ROUTE_SNAPSHOT_PATH = ROOT / "legal_sources" / "routes.snapshot.json"
ROUTE_LOCK_PATH = ROOT / "legal_sources" / "routes.snapshot.lock.json"
EXTENSION_ROUTES_PATH = ROOT / "legal_sources" / "extension_routes.json"
LAW_VERSIONS_PATH = ROOT / "legal_sources" / "law_versions.json"
ARTICLE_VERIFICATIONS_PATH = ROOT / "legal_sources" / "article_verifications.json"
ROUTE_CORRECTIONS_PATH = ROOT / "legal_sources" / "route_corrections.json"
CONSTITUTIONAL_VERIFICATIONS_PATH = ROOT / "legal_sources" / "constitutional_route_verifications.json"

EXPECTED_COLUMNS = [
    "question_id", "role", "text", "fact_target", "element_type", "layer",
    "requirement", "routes", "preconditions", "prohibitions", "source",
    "version", "editorial_status", "method_review_status",
    "legal_review_status", "runtime_status", "page_cost", "template_binding",
]
ROLES = {"victim", "suspect", "witness"}
LAYERS = {"procedure", "family_skeleton", "element_supplement", "conditional_module"}
REQUIREMENTS = {"REQUIRED", "CONDITIONAL", "OPTIONAL"}
RUNTIME_STATUSES = {"AVAILABLE_WITH_WARNING", "APPROVED_FOR_RUNTIME", "DISABLED"}
FORBIDDEN_AUDIT_PARTS = {"audit", "review", "evidence"}
LEADING_PATTERNS = [
    re.compile(pattern) for pattern in (
        r"你是不是.*所以", r"你明知.*仍", r"你就是", r"顯然", r"已經構成",
        r"確實犯了", r"承認.*犯罪",
    )
]


class CompileError(ValueError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _normalized(raw: bytes) -> bytes:
    text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return unicodedata.normalize("NFC", text).encode("utf-8")


def _safe_source(path_text: str) -> Path:
    relative = Path(path_text)
    if relative.is_absolute() or ".." in relative.parts:
        raise CompileError(f"unsafe source path: {path_text}")
    if FORBIDDEN_AUDIT_PARTS.intersection({part.lower() for part in relative.parts}):
        raise CompileError(f"audit/review source is forbidden: {path_text}")
    resolved = (SOURCE_ROOT / relative).resolve()
    if SOURCE_ROOT.resolve() not in resolved.parents:
        raise CompileError(f"source escapes question_sources: {path_text}")
    return resolved


def _metadata(lines: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in lines:
        match = re.match(r"^- ([a-z_]+): `([^`]*)`$", line.strip())
        if match:
            result[match.group(1)] = match.group(2)
    return result


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _split(value: str) -> list[str]:
    if value in {"", "NONE"}:
        return ["NONE"]
    return [item.strip() for item in value.split(",") if item.strip()]


def _validate_question(row: dict[str, str], source_path: str, line_no: int) -> None:
    if row["role"] not in ROLES:
        raise CompileError(f"{source_path}:{line_no}: invalid role")
    if row["layer"] not in LAYERS or row["requirement"] not in REQUIREMENTS:
        raise CompileError(f"{source_path}:{line_no}: invalid layer/requirement")
    if row["runtime_status"] not in RUNTIME_STATUSES:
        raise CompileError(f"{source_path}:{line_no}: invalid runtime_status")
    if not row["text"].endswith(("？", "。")):
        raise CompileError(f"{source_path}:{line_no}: question punctuation required")
    if row["text"].count("？") > 1 or row["text"].count("?") > 1:
        raise CompileError(f"{source_path}:{line_no}: compound question")
    if any(pattern.search(row["text"]) for pattern in LEADING_PATTERNS):
        raise CompileError(f"{source_path}:{line_no}: leading or guilt-assuming wording")
    try:
        page_cost = int(row["page_cost"])
    except ValueError as exc:
        raise CompileError(f"{source_path}:{line_no}: invalid page_cost") from exc
    if page_cost < 1 or page_cost > 10:
        raise CompileError(f"{source_path}:{line_no}: page_cost out of range")


def _parse_source(path_text: str, expected_family: str) -> tuple[dict, list[dict], dict]:
    source = _safe_source(path_text)
    raw = source.read_bytes()
    normalized = _normalized(raw)
    lines = normalized.decode("utf-8").splitlines()
    metadata = _metadata(lines)
    if metadata.get("family_id") != expected_family:
        raise CompileError(f"{path_text}: family_id mismatch")
    try:
        heading_index = next(i for i, line in enumerate(lines) if line.startswith("| question_id |"))
    except StopIteration as exc:
        raise CompileError(f"{path_text}: missing question table") from exc
    columns = _cells(lines[heading_index])
    if columns != EXPECTED_COLUMNS:
        raise CompileError(f"{path_text}: unexpected columns {columns}")
    records: list[dict] = []
    for index in range(heading_index + 2, len(lines)):
        line = lines[index]
        if not line.startswith("|"):
            break
        cells = _cells(line)
        if len(cells) != len(EXPECTED_COLUMNS):
            raise CompileError(f"{path_text}:{index + 1}: expected {len(EXPECTED_COLUMNS)} cells")
        row = dict(zip(EXPECTED_COLUMNS, cells, strict=True))
        _validate_question(row, path_text, index + 1)
        routes = _split(row.pop("routes"))
        preconditions = _split(row.pop("preconditions"))
        prohibitions = _split(row.pop("prohibitions"))
        content_sha = _sha(_canonical({key: row[key] for key in sorted(row) if key != "source"}))
        for route in routes:
            for precondition in preconditions:
                records.append({
                    **row,
                    "family_id": expected_family,
                    "legal_target_route_id": route,
                    "precondition_id": precondition,
                    "prohibition_ids": prohibitions,
                    "source_path": path_text,
                    "source_line": index + 1,
                    "source_sha256": _sha(raw),
                    "normalized_source_sha256": _sha(normalized),
                    "content_sha256": content_sha,
                    "page_cost": int(row["page_cost"]),
                })
    if not records:
        raise CompileError(f"{path_text}: no questions")
    source_info = {
        "path": path_text,
        "kind": "QUESTION_SOURCE",
        "raw_sha256": _sha(raw),
        "normalized_sha256": _sha(normalized),
        "question_rows": len({record["question_id"] for record in records}),
        "allowed_use": "RUNTIME_QUESTION_BANK",
        "sensitivity": "NO_CASE_DATA",
        "authority": "INTERNAL_DESIGN",
        "ingestion_status": "ALLOWLISTED",
    }
    return metadata, records, source_info


def compile_all() -> tuple[bytes, bytes, bytes]:
    manifest_raw = MANIFEST_PATH.read_bytes()
    manifest = json.loads(manifest_raw)
    families = manifest.get("families", [])
    if len(families) != 15 or len({f["family_id"] for f in families}) != 15:
        raise CompileError("families manifest must contain exactly 15 unique families")
    route_snapshot_raw = ROUTE_SNAPSHOT_PATH.read_bytes()
    route_snapshot = json.loads(route_snapshot_raw)
    route_lock = json.loads(ROUTE_LOCK_PATH.read_text(encoding="utf-8"))
    if route_lock.get("snapshot_sha256") != _sha(route_snapshot_raw):
        raise CompileError("legal route snapshot hash mismatch")
    route_index = {route["id"]: route for route in route_snapshot.get("routes", [])}
    if len(route_index) != 44 or sum(len(route.get("child_routes", [])) for route in route_index.values()) != 310:
        raise CompileError("legal route snapshot must contain 44 parents and 310 children")
    extension_raw = EXTENSION_ROUTES_PATH.read_bytes()
    extension_data = json.loads(extension_raw)
    extension_index = {route["id"]: route for route in extension_data.get("routes", [])}
    law_versions_raw = LAW_VERSIONS_PATH.read_bytes()
    law_versions_data = json.loads(law_versions_raw)
    law_versions = {record["law_name"]: record for record in law_versions_data.get("records", [])}
    snapshot_laws = {
        child["law_name"]
        for route in route_index.values()
        for child in route.get("child_routes", [])
    }
    if set(law_versions) != snapshot_laws:
        raise CompileError("official law version manifest must cover every snapshot law exactly")
    if any(record.get("status") != "現行法規" for record in law_versions.values()):
        raise CompileError("law version manifest contains a non-current law")
    article_verifications_raw = ARTICLE_VERIFICATIONS_PATH.read_bytes()
    article_verifications = json.loads(article_verifications_raw)
    if article_verifications.get("route_snapshot_sha256") != _sha(route_snapshot_raw):
        raise CompileError("article verification does not match the route snapshot")
    if article_verifications.get("verification_status") != "ALL_SNAPSHOT_CITATIONS_OFFICIAL_CURRENT_ARTICLE_EXISTS":
        raise CompileError("article verification manifest has an invalid status")
    verification_proofs = {proof["law_name"]: proof for proof in article_verifications.get("proofs", [])}
    if set(verification_proofs) != snapshot_laws:
        raise CompileError("article verification proofs must cover every snapshot law exactly")
    for law_name, proof in verification_proofs.items():
        actual_count = sum(
            1 for route in route_index.values() for child in route.get("child_routes", [])
            if child["law_name"] == law_name
        )
        if proof.get("verified_child_route_count") != actual_count:
            raise CompileError(f"article verification child count mismatch: {law_name}")
        if proof.get("missing_count") != 0 or proof.get("returned_article_count", 0) < 1:
            raise CompileError(f"article verification has missing or empty results: {law_name}")
        if not proof.get("query_batches"):
            raise CompileError(f"article verification lacks query trace: {law_name}")
        if proof.get("pcode") != law_versions[law_name]["pcode"]:
            raise CompileError(f"article verification pcode mismatch: {law_name}")
    route_corrections_raw = ROUTE_CORRECTIONS_PATH.read_bytes()
    route_corrections_data = json.loads(route_corrections_raw)
    route_corrections = {item["route_id"]: item for item in route_corrections_data.get("corrections", [])}
    all_children = {
        child["id"]: child for route in route_index.values() for child in route.get("child_routes", [])
    }
    if len(route_corrections) != len(route_corrections_data.get("corrections", [])):
        raise CompileError("duplicate route correction")
    for route_id, correction in route_corrections.items():
        original = all_children.get(route_id)
        if original is None:
            raise CompileError(f"route correction references an unknown child: {route_id}")
        if correction["law_name"] != original["law_name"] or correction["article_no"] != original["article_no"]:
            raise CompileError(f"route correction law citation mismatch: {route_id}")
        if not correction.get("reason") or not correction.get("fact_elements"):
            raise CompileError(f"route correction lacks evidence or elements: {route_id}")
    constitutional_raw = CONSTITUTIONAL_VERIFICATIONS_PATH.read_bytes()
    constitutional_data = json.loads(constitutional_raw)
    constitutional_routes = {
        item["route_id"]: item for item in constitutional_data.get("records", [])
        if item.get("route_id")
    }
    for route_id, verification in constitutional_routes.items():
        child = all_children.get(route_id)
        if child is None or child["article_no"] != verification["article_no"]:
            raise CompileError(f"constitutional verification route mismatch: {route_id}")
        effective_elements = route_corrections.get(route_id, child).get("fact_elements", [])
        for fragment in verification.get("required_fact_fragments", []):
            if not any(fragment in element for element in effective_elements):
                raise CompileError(f"constitutional narrowing missing from route: {route_id}: {fragment}")
    excluded_routes = {
        excluded["id"]: excluded
        for parent in route_index.values()
        for excluded in parent.get("excluded_routes", [])
    }
    for verification in constitutional_data.get("records", []):
        excluded_id = verification.get("excluded_route_id")
        if not excluded_id:
            continue
        excluded = excluded_routes.get(excluded_id)
        if excluded is None or excluded.get("status") != verification.get("status"):
            raise CompileError(f"constitutional exclusion mismatch: {excluded_id}")
    declared_routes = {route for family in families for route in family.get("routes", [])}
    if declared_routes != set(route_index) | set(extension_index):
        raise CompileError(
            f"family route coverage mismatch: missing={sorted((set(route_index)|set(extension_index))-declared_routes)}, "
            f"extra={sorted(declared_routes-(set(route_index)|set(extension_index)))}"
        )
    records: list[dict] = []
    sources: list[dict] = []
    family_summaries: list[dict] = []
    ids: set[tuple[str, str]] = set()
    for family in families:
        metadata, compiled, source_info = _parse_source(family["file"], family["family_id"])
        family_summaries.append({
            "family_id": family["family_id"],
            "label": family["label"],
            "routes": family["routes"],
            "version": metadata.get("version", "UNKNOWN"),
            "question_count": len({item["question_id"] for item in compiled}),
            "legal_review_status": metadata.get("legal_review_status", "UNKNOWN"),
            "runtime_status": metadata.get("runtime_status", "DISABLED"),
        })
        for item in compiled:
            parent_route = item["legal_target_route_id"]
            expanded: list[dict] = []
            if parent_route in route_index:
                parent = route_index[parent_route]
                for child in parent.get("child_routes", []):
                    law_version = law_versions[child["law_name"]]
                    correction = route_corrections.get(child["id"])
                    expanded.append({
                        **item,
                        "parent_route_id": parent_route,
                        "legal_target_route_id": child["id"],
                        "route_kind": child.get("route_kind", "UNKNOWN"),
                        "law_name": child.get("law_name", "UNKNOWN"),
                        "article_no": child.get("article_no", "UNKNOWN"),
                        "law_pcode": law_version["pcode"],
                        "law_last_amended": law_version["last_amended"],
                        "law_effective_date": law_version["effective_date"],
                        "law_source_url": law_version["source_url"],
                        "law_version_checked_at": law_versions_data["checked_at"],
                        "article_verification_status": "OFFICIAL_CURRENT_ARTICLE_EXISTS",
                        "article_verified_at": article_verifications["checked_at"],
                        "route_name": child.get("name", child["id"]),
                        "route_fact_elements": (
                            correction["fact_elements"] if correction else child.get("fact_elements", [])
                        ),
                        "route_correction_status": "OFFICIAL_ARTICLE_CORRECTED" if correction else "UNCHANGED_SNAPSHOT",
                        "route_correction_reason": correction["reason"] if correction else "",
                        "constitutional_status": (
                            constitutional_routes.get(child["id"], {}).get("status", "NOT_APPLICABLE")
                        ),
                        "constitutional_decision": (
                            constitutional_routes.get(child["id"], {}).get("decision", "")
                        ),
                        "constitutional_source_url": (
                            constitutional_routes.get(child["id"], {}).get("source_url", "")
                        ),
                        "route_review_status": child.get("review_status", "HUMAN_REVIEW_REQUIRED"),
                        "route_resolution_status": "SNAPSHOT_CHILD_ROUTE",
                    })
            elif parent_route in extension_index:
                extension = extension_index[parent_route]
                expanded.append({
                    **item,
                    "parent_route_id": parent_route,
                    "legal_target_route_id": parent_route,
                    "route_kind": "extension_blocked",
                    "law_name": "UNKNOWN",
                    "article_no": "UNKNOWN",
                    "route_name": extension["label"],
                    "route_fact_elements": [],
                    "route_review_status": extension["legal_review_status"],
                    "route_resolution_status": extension["status"],
                    "runtime_status": "DISABLED",
                })
            else:
                raise CompileError(f"unmapped family parent route: {parent_route}")
            for expanded_item in expanded:
                key = (expanded_item["question_id"], expanded_item["legal_target_route_id"])
                if key in ids:
                    raise CompileError(f"duplicate normalized row: {key}")
                ids.add(key)
                records.append(expanded_item)
        sources.append(source_info)
    for path_text in manifest.get("procedure_sources", []):
        metadata, compiled, source_info = _parse_source(path_text, "common_procedure")
        records.extend({**item, "parent_route_id": "ALL", "route_kind": "procedure", "route_resolution_status": "COMMON_PROCEDURE"} for item in compiled)
        sources.append(source_info)
    sources.extend([
        {
            "path": "legal_sources/routes.snapshot.json",
            "kind": "LEGAL_ROUTE_SNAPSHOT",
            "raw_sha256": _sha(route_snapshot_raw),
            "normalized_sha256": _sha(_normalized(route_snapshot_raw)),
            "question_rows": 0,
            "allowed_use": "STRUCTURAL_ROUTE_MAPPING",
            "sensitivity": "NO_CASE_DATA",
            "authority": "IMPORTED_REVIEW_SNAPSHOT",
            "ingestion_status": "ALLOWLISTED",
        },
        {
            "path": "legal_sources/extension_routes.json",
            "kind": "BLOCKED_EXTENSION_ROUTES",
            "raw_sha256": _sha(extension_raw),
            "normalized_sha256": _sha(_normalized(extension_raw)),
            "question_rows": 0,
            "allowed_use": "BLOCKED_ROUTE_VISIBILITY",
            "sensitivity": "NO_CASE_DATA",
            "authority": "INTERNAL_DESIGN",
            "ingestion_status": "ALLOWLISTED",
        },
        {
            "path": "legal_sources/law_versions.json",
            "kind": "OFFICIAL_LAW_VERSION_MANIFEST",
            "raw_sha256": _sha(law_versions_raw),
            "normalized_sha256": _sha(_normalized(law_versions_raw)),
            "question_rows": 0,
            "allowed_use": "CURRENT_LAW_VERSION_PIN",
            "sensitivity": "NO_CASE_DATA",
            "authority": "OFFICIAL_LAW_MOJ",
            "ingestion_status": "ALLOWLISTED",
        },
        {
            "path": "legal_sources/article_verifications.json",
            "kind": "OFFICIAL_ARTICLE_VERIFICATION_MANIFEST",
            "raw_sha256": _sha(article_verifications_raw),
            "normalized_sha256": _sha(_normalized(article_verifications_raw)),
            "question_rows": 0,
            "allowed_use": "CURRENT_ARTICLE_EXISTENCE_VERIFICATION",
            "sensitivity": "NO_CASE_DATA",
            "authority": "OFFICIAL_LAW_MOJ",
            "ingestion_status": "ALLOWLISTED",
        },
        {
            "path": "legal_sources/route_corrections.json",
            "kind": "OFFICIAL_ARTICLE_ROUTE_CORRECTIONS",
            "raw_sha256": _sha(route_corrections_raw),
            "normalized_sha256": _sha(_normalized(route_corrections_raw)),
            "question_rows": 0,
            "allowed_use": "ROUTE_FACT_ELEMENT_CORRECTION_OVERLAY",
            "sensitivity": "NO_CASE_DATA",
            "authority": "OFFICIAL_LAW_MOJ_WITH_AI_REVIEW",
            "ingestion_status": "ALLOWLISTED",
        },
        {
            "path": "legal_sources/constitutional_route_verifications.json",
            "kind": "CONSTITUTIONAL_ROUTE_VERIFICATIONS",
            "raw_sha256": _sha(constitutional_raw),
            "normalized_sha256": _sha(_normalized(constitutional_raw)),
            "question_rows": 0,
            "allowed_use": "ROUTE_NARROWING_AND_EXCLUSION",
            "sensitivity": "NO_CASE_DATA",
            "authority": "CONSTITUTIONAL_COURT_OFFICIAL",
            "ingestion_status": "ALLOWLISTED",
        },
    ])
    records.sort(key=lambda item: (
        item["family_id"], item["question_id"], item["role"],
        item["legal_target_route_id"], item["precondition_id"],
    ))
    compiler_sha = _sha(Path(__file__).read_bytes())
    closure = {
        "compiler_sha256": compiler_sha,
        "families_manifest_sha256": _sha(manifest_raw),
        "route_snapshot_sha256": _sha(route_snapshot_raw),
        "extension_routes_sha256": _sha(extension_raw),
        "law_versions_sha256": _sha(law_versions_raw),
        "article_verifications_sha256": _sha(article_verifications_raw),
        "route_corrections_sha256": _sha(route_corrections_raw),
        "constitutional_verifications_sha256": _sha(constitutional_raw),
        "sources": [{"path": s["path"], "raw_sha256": s["raw_sha256"]} for s in sources],
    }
    build_fingerprint = _sha(_canonical(closure))
    bank = {
        "schema_version": "question-bank/v1",
        "build_fingerprint": build_fingerprint,
        "disclaimer": "CANDIDATES_AND_QUESTIONS_ARE_NOT_LEGAL_CONCLUSIONS",
        "family_count": len(family_summaries),
        "concept_count": len({item["question_id"] for item in records}),
        "normalized_record_count": len(records),
        "families": family_summaries,
        "records": records,
    }
    source_lock = {
        "schema_version": "source-lock/v1",
        "build_fingerprint": build_fingerprint,
        "compiler_sha256": compiler_sha,
        "families_manifest_sha256": _sha(manifest_raw),
        "route_snapshot_sha256": _sha(route_snapshot_raw),
        "extension_routes_sha256": _sha(extension_raw),
        "law_versions_sha256": _sha(law_versions_raw),
        "article_verifications_sha256": _sha(article_verifications_raw),
        "route_corrections_sha256": _sha(route_corrections_raw),
        "constitutional_verifications_sha256": _sha(constitutional_raw),
        "sources": sorted(sources, key=lambda item: item["path"]),
    }
    route_rows: dict[tuple[str, str], dict] = {}
    for item in records:
        route = item["legal_target_route_id"]
        if route == "ALL":
            continue
        key = (route, item["role"])
        entry = route_rows.setdefault(key, {
            "route_id": route,
            "parent_route_id": item.get("parent_route_id", route),
            "role": item["role"],
            "fact_targets": set(),
            "question_ids": set(),
            "coverage_status": "BLOCKED" if item.get("route_resolution_status", "").startswith("BLOCKED") else "QUESTIONS_DRAFT",
            "legal_review_status": "HUMAN_REVIEW_REQUIRED",
            "route_kind": item.get("route_kind", "UNKNOWN"),
            "route_resolution_status": item.get("route_resolution_status", "UNKNOWN"),
        })
        entry["fact_targets"].add(item["fact_target"])
        entry["question_ids"].add(item["question_id"])
    coverage_records = []
    for entry in route_rows.values():
        coverage_records.append({
            **entry,
            "fact_targets": sorted(entry["fact_targets"]),
            "question_ids": sorted(entry["question_ids"]),
        })
    coverage_records.sort(key=lambda item: (item["route_id"], item["role"]))
    coverage = {
        "schema_version": "route-coverage/v1",
        "build_fingerprint": build_fingerprint,
        "meaning": "Structural draft coverage only; not legal approval",
        "snapshot_parent_count": 44,
        "snapshot_child_count": 310,
        "blocked_extension_count": len(extension_index),
        "records": coverage_records,
    }
    return _canonical(bank), _canonical(source_lock), _canonical(coverage)


def _write_or_check(path: Path, content: bytes, check: bool) -> bool:
    if check:
        return path.exists() and path.read_bytes() == content
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        bank, source_lock, coverage = compile_all()
        outcomes = [
            _write_or_check(BANK_PATH, bank, args.check),
            _write_or_check(SOURCE_LOCK_PATH, source_lock, args.check),
            _write_or_check(COVERAGE_PATH, coverage, args.check),
        ]
        if not all(outcomes):
            print("compiled artifacts are missing or stale", file=sys.stderr)
            return 1
        print(json.dumps({
            "status": "PASS",
            "check_only": args.check,
            "question_bank_sha256": _sha(bank),
            "source_manifest_sha256": _sha(source_lock),
            "route_coverage_sha256": _sha(coverage),
        }, ensure_ascii=False, sort_keys=True))
        return 0
    except (CompileError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"compile failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
