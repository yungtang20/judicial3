"""Validate the offline Taiwan citation and case-trace fixtures.

Run from legal-case-web:
    python tools/validate_citation_contract.py

No formal workflow, database, LLM, MCP, HTTP or cloud service is used.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.citation_contract import citation_contract_is_valid, parse_citations  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]


def load_json(name: str) -> dict:
    with (ROOT / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def validate() -> dict[str, object]:
    citation_fixture = load_json("LEGAL_CITATION_FIXTURE.json")
    citation_count = 0
    for case in citation_fixture["cases"]:
        parsed = parse_citations(case["input"], source_ref=f"fixture:{case['id']}")
        actual = [
            {key: item.to_dict().get(key) for key in (
                "law_name", "article_number", "article_subnumber", "paragraph_number",
                "item_number", "subitem_number", "parse_status",
            )}
            for item in parsed
        ]
        assert actual == case["expected"], case["id"]
        assert all(citation_contract_is_valid(item.to_dict()) for item in parsed)
        citation_count += len(parsed)

    trace = load_json("LEGAL_TRACE_FIXTURE.json")
    assert trace["fixture_only"] is True
    assert trace["applied_legal_basis"] == []
    assert all(item["readiness_status"] == "NEEDS_FACTS" for item in trace["candidates"])
    assert all(item["fact_gap"] for item in trace["questions"])
    return {
        "citation_cases": len(citation_fixture["cases"]),
        "citation_mentions": citation_count,
        "trace_case_id": trace["case_id"],
        "candidate_count": len(trace["candidates"]),
        "llm": trace["analysis_contract"]["llm"],
        "database": trace["analysis_contract"]["database"],
    }


if __name__ == "__main__":
    try:
        print(json.dumps({"status": "PASS", **validate()}, ensure_ascii=False, indent=2))
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
