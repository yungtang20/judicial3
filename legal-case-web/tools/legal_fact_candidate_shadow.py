"""Offline, read-only shadow replay for facts and candidate generation.

This module deliberately calls the existing deterministic rule functions.  It
does not call an LLM, database, HTTP service, or alter the production flow.
"""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import QUESTION_BANK_PATH  # noqa: E402
from app.rules import analyze_gate1, build_questions, candidate_offenses, load_bank  # noqa: E402


FIXTURE_PATH = PROJECT_ROOT / "LEGAL_TRACE_FIXTURE.json"
TRACE_VERSION = "legal-fact-candidate-shadow-v1"


def _git(command: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *command], cwd=PROJECT_ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", check=False,
        )
    except OSError as exc:
        return f"NOT_AVAILABLE: {type(exc).__name__}: {exc}"
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    return stdout if result.returncode == 0 else (
        f"NOT_AVAILABLE(exit={result.returncode}): {stderr}"
    )


def _load_fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _standard_facts(fixture: dict[str, Any], scenario: str) -> list[dict[str, Any]]:
    facts = copy.deepcopy(fixture["facts"])
    if scenario == "A":
        facts.append({
            "fact_id": "fact:shadow-a-possession",
            "subject": "甲",
            "predicate": "仍可實際支配",
            "object": "手機",
            "assertion_class": "ASSERTED",
            "verification_status": "UNVERIFIED",
            "source_ref": "fixture:scenario:A",
        })
    elif scenario == "B":
        facts.append({
            "fact_id": "fact:shadow-b-lost",
            "subject": "甲",
            "predicate": "離開後發現遺失",
            "object": "手機",
            "assertion_class": "ASSERTED",
            "verification_status": "UNVERIFIED",
            "source_ref": "fixture:scenario:B",
        })
        facts.append({
            "fact_id": "fact:shadow-b-not-present",
            "subject": "甲",
            "predicate": "拿取時不在場",
            "object": "UNKNOWN",
            "assertion_class": "UNKNOWN",
            "verification_status": "UNKNOWN",
            "source_ref": "fixture:scenario:B",
        })
    return facts


def _standard_gate1(fixture: dict[str, Any], scenario: str) -> dict[str, Any]:
    facts = _standard_facts(fixture, scenario)
    return {
        "summary": fixture["summary"],
        "source_summary": fixture["summary"],
        "facts": facts,
        "unknowns": [
            {"fact_id": fact["fact_id"], "value": fact.get("object", "UNKNOWN")}
            for fact in facts if fact.get("assertion_class") == "UNKNOWN"
        ],
        "segmentation_source": "shadow_adapter:LEGAL_TRACE_FIXTURE.json",
        "adapter_status": "OBSERVED_STANDARDIZED_FIXTURE; NOT_PRODUCTION_FACT_MODEL",
        "adapter_unmapped_fields": ["fact_key", "action", "possession_state", "knowledge_or_intent"],
    }


def _current_gate1(summary: str) -> dict[str, Any]:
    return analyze_gate1({"summary": summary, "event_time": "", "location": ""}, use_ai=False)


def _candidate_snapshot(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fields = (
        "id", "candidate_id", "name", "matched_terms", "status", "candidate_state",
        "candidate_eligibility", "candidate_rank_factors", "unknown_elements",
        "unknown_fact_keys", "missing", "supporting_fact_refs", "contradicting_fact_refs",
        "selection_origin", "legal_route_states", "route_type", "inclusion_reason",
    )
    return [{key: copy.deepcopy(item.get(key)) for key in fields if key in item} for item in items]


def _questions(bank: dict[str, Any], gate1: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    offense_ids = [str(item.get("id")) for item in candidates if item.get("id")]
    try:
        result = build_questions(
            bank, "victim", offense_ids, gate1=gate1, candidates=candidates,
            legal_route_ids=[],
        )
        return {"status": "OBSERVED", "items": result}
    except Exception as exc:  # shadow diagnostics must retain the failure
        return {
            "status": "NOT_RUN",
            "error": {"type": type(exc).__name__, "message": str(exc)},
        }


def _run_path(bank: dict[str, Any], fixture: dict[str, Any], summary: str, path: str, scenario: str) -> dict[str, Any]:
    if path == "CURRENT_FACTS":
        gate1 = _current_gate1(summary)
        adapter = {"status": "NOT_USED", "source": "app.rules.analyze_gate1(use_ai=False)"}
    else:
        gate1 = _standard_gate1(fixture, scenario)
        adapter = {
            "status": "OBSERVED",
            "source": "LEGAL_TRACE_FIXTURE.json",
            "note": "獨立適配器保留 UNKNOWN；未填入正式 fact_key 或推測狀態。",
        }
    candidates = candidate_offenses(summary, bank, gate1)
    snapshot = _candidate_snapshot(candidates)
    return {
        "path": path,
        "summary": summary,
        "facts": copy.deepcopy(gate1.get("facts", [])),
        "unknowns": copy.deepcopy(gate1.get("unknowns", [])),
        "fact_source": gate1.get("segmentation_source", "NOT_OBSERVED"),
        "fact_adapter": adapter,
        "stages": {
            "fact_extraction": "OBSERVED",
            "initial_candidate_generation": "OBSERVED",
            "element_assessment": "OBSERVED" if any("unknown_elements" in x for x in snapshot) else "NOT_OBSERVED",
            "ranking": "OBSERVED" if any("candidate_rank_factors" in x for x in snapshot) else "NOT_OBSERVED",
            "parent_child_route": "OBSERVED" if any("legal_route_states" in x for x in snapshot) else "NOT_OBSERVED",
            "question_generation": "NOT_RUN",
        },
        "initial_candidates": snapshot,
        "questions": _questions(bank, gate1, candidates),
        "formal_runtime_calls": {"llm": "NOT_USED", "database": "NOT_USED", "http": "NOT_USED"},
    }


def _first_difference(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    comparisons = (
        ("summary", left.get("summary"), right.get("summary")),
        ("facts", left.get("facts"), right.get("facts")),
        ("unknowns", left.get("unknowns"), right.get("unknowns")),
        ("initial_candidates", left.get("initial_candidates"), right.get("initial_candidates")),
        ("questions", left.get("questions"), right.get("questions")),
    )
    for stage, left_value, right_value in comparisons:
        if left_value != right_value:
            return {"stage": stage, "left": left_value, "right": right_value, "status": "OBSERVED"}
    return {"stage": "NONE", "status": "NO_DIFFERENCE_OBSERVED"}


def run_shadow(*, write_trace: bool = True) -> dict[str, Any]:
    fixture = _load_fixture()
    bank = load_bank(QUESTION_BANK_PATH)
    base = fixture["summary"]
    summaries = {
        "BASELINE": base,
        "A": base + " 甲仍在櫃檯旁，手機在甲伸手可及的位置，乙拿取時看見甲正在注意該手機。",
        "B": base + " 甲離開店內後才發現手機遺失；乙拾得時甲不在場；乙是否具有不法所有意圖仍未知。",
    }
    scenarios: dict[str, Any] = {}
    for name, summary in summaries.items():
        current = _run_path(bank, fixture, summary, "CURRENT_FACTS", name)
        standard = _run_path(bank, fixture, summary, "STANDARDIZED_FACTS", name)
        scenarios[name] = {
            "current_facts": current,
            "standardized_facts": standard,
            "first_difference": _first_difference(current, standard),
        }
    trace = {
        "trace_version": TRACE_VERSION,
        "project_root": str(PROJECT_ROOT),
        "fixture": str(FIXTURE_PATH),
        "git_head": _git(["rev-parse", "HEAD"]),
        "git_status": _git(["status", "--short"]),
        "entrypoints": {
            "fact_extraction": "app.rules.analyze_gate1(use_ai=False)",
            "candidate_generation": "app.rules.candidate_offenses(summary, bank, gate1)",
            "question_generation": "app.rules.build_questions(...)",
        },
        "scenarios": scenarios,
        "limitations": [
            "No LLM, database, HTTP, frontend, historical revision, or production runtime was called.",
            "STANDARDIZED_FACTS is an independent adapter and is not evidence of formal runtime behavior.",
            "Candidate differences are observations; this tool does not declare a root cause.",
        ],
    }
    if write_trace:
        (PROJECT_ROOT / "LEGAL_FACT_CANDIDATE_SHADOW_TRACE.json").write_text(
            json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return trace


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the offline legal fact/candidate shadow replay.")
    parser.add_argument("--no-write", action="store_true", help="Do not write the JSON trace artifact.")
    args = parser.parse_args()
    trace = run_shadow(write_trace=not args.no_write)
    print(json.dumps(trace, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
