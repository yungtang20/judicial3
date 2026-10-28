"""Compile the existing common question bank and review-only witness draft."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def compile_common(source: Path, fixture: dict) -> dict:
    source_bytes = source.read_bytes()
    bank = json.loads(source_bytes.decode("utf-8"))
    common = bank.get("common")
    if not isinstance(common, dict):
        raise ValueError("question bank has no common object")

    records = []
    expected_roles = fixture["existing_runtime_roles"]
    if set(common) != set(expected_roles):
        raise ValueError(f"common role drift: expected={expected_roles}, actual={sorted(common)}")
    for role in expected_roles:
        for item in common[role]:
            source_info = item.get("source") or {}
            records.append({
                "id": item["id"],
                "text": item["text"],
                "target_interview_role": role,
                "fact_target": item["purpose"],
                "purpose": item["purpose"],
                "layer": "common",
                "priority": item["priority"],
                "required_or_optional": "REQUIRED" if item["priority"] == 1 else "OPTIONAL",
                "runtime_enabled": True,
                "source_runtime_status": "EXISTING_RUNTIME_COMMON",
                "review_status": source_info.get("status", fixture["review_status"]),
                "provenance": {
                    "source": "data/question_bank.json",
                    "source_label": source_info.get("label")
                }
            })

    for item in fixture["witness_review_only_questions"]:
        records.append({
            "id": item["id"],
            "text": item["text"],
            "target_interview_role": "witness_review_only",
            "fact_target": item["purpose"],
            "purpose": item["purpose"],
            "layer": "common",
            "priority": item["priority"],
            "required_or_optional": "REQUIRED" if item["priority"] == 1 else "OPTIONAL",
            "runtime_enabled": False,
            "source_runtime_status": "DESIGN_ONLY_WITNESS_COMMON",
            "review_status": fixture["review_status"],
            "provenance": {
                "source": "data/question_family_fixtures/common_layer.json",
                "source_label": "USER_FAMILY_DESIGN_DRAFT"
            }
        })

    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate common question ids")

    return {
        "schema_version": "question-common-master-v1-draft",
        "document_status": fixture["document_status"],
        "review_status": fixture["review_status"],
        "runtime_integration_status": "EXISTING_COMMON_ONLY",
        "source": fixture["source"],
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "record_count": len(records),
        "existing_runtime_record_count": sum(record["runtime_enabled"] for record in records),
        "review_only_record_count": sum(not record["runtime_enabled"] for record in records),
        "records": records
    }


def _payload(compiled: dict) -> str:
    return json.dumps(compiled, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile common questions into a long-table draft")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    payload = _payload(compile_common(args.source, fixture))
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != payload:
            raise SystemExit("common question master is missing or stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
