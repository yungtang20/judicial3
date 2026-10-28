from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = ROOT / "data" / "runtime"
TEMPLATE_ROOT = ROOT / "data" / "templates"
ALLOWED_FILES = {"question_bank.json", "source_manifest.json", "route_coverage.json"}


class QuestionBankError(RuntimeError):
    pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class QuestionBank:
    def __init__(self, runtime_root: Path = RUNTIME_ROOT):
        self.runtime_root = runtime_root.resolve()
        if self.runtime_root.name != "runtime" or self.runtime_root.parent.name != "data":
            raise QuestionBankError("runtime root must be data/runtime")
        files = {path.name for path in self.runtime_root.iterdir() if path.is_file()}
        unexpected = files - ALLOWED_FILES
        if unexpected:
            raise QuestionBankError(f"unexpected runtime data files: {sorted(unexpected)}")
        self.bank = self._load("question_bank.json")
        self.sources = self._load("source_manifest.json")
        self.coverage = self._load("route_coverage.json")
        self.template_questions_data = self._load_template_questions()
        fingerprints = {
            self.bank.get("build_fingerprint"),
            self.sources.get("build_fingerprint"),
            self.coverage.get("build_fingerprint"),
        }
        if len(fingerprints) != 1 or None in fingerprints:
            raise QuestionBankError("runtime artifacts have mismatched build fingerprints")

    def _load(self, name: str) -> dict[str, Any]:
        if name not in ALLOWED_FILES:
            raise QuestionBankError("file is not allow-listed")
        path = (self.runtime_root / name).resolve()
        if path.parent != self.runtime_root:
            raise QuestionBankError("runtime path escape")
        return json.loads(path.read_text(encoding="utf-8"))

    def _load_template_questions(self) -> dict[str, Any]:
        manifest_path = TEMPLATE_ROOT / "manifest.json"
        questions_path = TEMPLATE_ROOT / "questions.json"
        if not manifest_path.exists() or not questions_path.exists():
            return {"questions": []}
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        raw = questions_path.read_bytes()
        if manifest.get("question_bindings_sha256") != _sha(raw):
            raise QuestionBankError("company template question bindings hash mismatch")
        return json.loads(raw)

    @property
    def fingerprint(self) -> str:
        return str(self.bank["build_fingerprint"])

    @property
    def template_fingerprint(self) -> str:
        path = TEMPLATE_ROOT / "questions.json"
        return _sha(path.read_bytes()) if path.exists() else "UNAVAILABLE"

    def families(self) -> list[dict[str, Any]]:
        return list(self.bank["families"])

    def child_routes(self, parent_route_id: str) -> list[dict[str, Any]]:
        routes: dict[str, dict[str, Any]] = {}
        for record in self.bank["records"]:
            if record.get("parent_route_id") != parent_route_id:
                continue
            route_id = record["legal_target_route_id"]
            if route_id == parent_route_id and record.get("route_resolution_status", "").startswith("BLOCKED"):
                continue
            routes.setdefault(route_id, {
                "route_id": route_id,
                "name": record.get("route_name", route_id),
                "route_kind": record.get("route_kind", "UNKNOWN"),
                "route_resolution_status": record.get("route_resolution_status", "UNKNOWN"),
                "law_name": record.get("law_name", "UNKNOWN"),
                "article_no": record.get("article_no", "UNKNOWN"),
                "law_pcode": record.get("law_pcode", "UNKNOWN"),
                "law_last_amended": record.get("law_last_amended", "UNKNOWN_REQUIRES_OFFICIAL_VERIFICATION"),
                "law_effective_date": record.get("law_effective_date", "UNKNOWN_REQUIRES_OFFICIAL_VERIFICATION"),
                "law_source_url": record.get("law_source_url", ""),
                "law_version_checked_at": record.get("law_version_checked_at", "UNKNOWN"),
                "article_verification_status": record.get("article_verification_status", "NOT_YET_EXACTLY_VERIFIED"),
                "article_verified_at": record.get("article_verified_at", "UNKNOWN"),
                "source_version": str(record.get("source_sha256", "UNKNOWN"))[:16],
                "fact_elements": list(record.get("route_fact_elements", [])),
                "correction_status": record.get("route_correction_status", "UNCHANGED_SNAPSHOT"),
                "correction_reason": record.get("route_correction_reason", ""),
                "constitutional_status": record.get("constitutional_status", "NOT_APPLICABLE"),
                "constitutional_decision": record.get("constitutional_decision", ""),
                "constitutional_source_url": record.get("constitutional_source_url", ""),
                "review_status": record.get("route_review_status", "HUMAN_REVIEW_REQUIRED"),
            })
        return [routes[key] for key in sorted(routes)]

    def questions(
        self,
        *,
        role: str,
        family_ids: list[str] | None = None,
        route_ids: list[str] | None = None,
        active_preconditions: set[str] | None = None,
        include_warning_status: bool = True,
    ) -> list[dict[str, Any]]:
        statuses = {"APPROVED_FOR_RUNTIME"}
        if include_warning_status:
            statuses.add("AVAILABLE_WITH_WARNING")
        families = set(family_ids or [])
        routes = set(route_ids or [])
        conditions = set(active_preconditions or {"NONE"})
        conditions.add("NONE")
        result = []
        seen: set[str] = set()
        for record in self.bank["records"]:
            if record["role"] != role or record["runtime_status"] not in statuses:
                continue
            if families and record["family_id"] not in families and record["family_id"] != "common_procedure":
                continue
            route = record["legal_target_route_id"]
            if routes and route not in routes and record.get("parent_route_id") not in routes and route != "ALL":
                continue
            if record.get("precondition_id", "NONE") not in conditions:
                continue
            if record["question_id"] in seen:
                continue
            seen.add(record["question_id"])
            result.append(record)
        return result

    def template_questions(self, role: str) -> list[dict[str, Any]]:
        return [
            dict(item) for item in self.template_questions_data.get("questions", [])
            if item.get("role") == role and item.get("runtime_status") == "AVAILABLE_WITH_WARNING"
        ]

    def artifact_hashes(self) -> dict[str, str]:
        return {
            name: _sha((self.runtime_root / name).read_bytes())
            for name in sorted(ALLOWED_FILES)
        }
