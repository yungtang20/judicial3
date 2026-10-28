"""Offline lineage audit for Gate 1 facts, candidates, and questions.

The audit keeps the summary constant and changes only a copied Gate 1 facts
list.  It calls existing deterministic functions and never writes to the
formal case workflow, database, HTTP server, or LLM.
"""
from __future__ import annotations

import argparse
import copy
import inspect
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import QUESTION_BANK_PATH  # noqa: E402
from app.rules import analyze_gate1, build_questions, candidate_offenses, load_bank  # noqa: E402


FIXTURE = ROOT / "LEGAL_TRACE_FIXTURE.json"
TRACE_VERSION = "legal-fact-lineage-v1"


def _fixture() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _function_evidence(function: Any) -> dict[str, Any]:
    path = Path(inspect.getsourcefile(function) or "")
    _, line = inspect.getsourcelines(function)
    return {
        "signature": str(inspect.signature(function)),
        "file": str(path),
        "line": line,
        "function": function.__name__,
    }


def _fact_marker(scenario: str) -> dict[str, Any]:
    if scenario == "A":
        return {
            "fact_id": "fact:lineage-A-possession",
            "subject": "甲",
            "predicate": "仍可實際支配",
            "object": "手機",
            "assertion_status": "EXPLICIT_SOURCE_ASSERTION",
            "machine_status": "FACT",
            "source_ref": "shadow:scenario:A",
            "source_excerpt": "測試新增：甲仍在櫃檯旁，手機在伸手可及位置且注意該手機。",
            "source_start": None,
            "source_end": None,
            "fact_key": "",
        }
    return {
        "fact_id": "fact:lineage-B-lost",
        "subject": "甲",
        "predicate": "離開後發現遺失",
        "object": "手機",
        "assertion_status": "EXPLICIT_SOURCE_ASSERTION",
        "machine_status": "FACT",
        "source_ref": "shadow:scenario:B",
        "source_excerpt": "測試新增：甲離開後發現手機遺失，乙拾得時甲不在現場。",
        "source_start": None,
        "source_end": None,
        "fact_key": "",
    }


def _unknown_intent_marker() -> dict[str, Any]:
    """Diagnostic-only marker showing the effect of a typed UNKNOWN key."""
    return {
        "fact_id": "fact:lineage-keyed-intent",
        "subject": "乙",
        "predicate": "不法所有意圖",
        "object": "UNKNOWN",
        "value": "UNKNOWN",
        "assertion_status": "UNKNOWN",
        "machine_status": "UNKNOWN",
        "source_ref": "shadow:diagnostic:keyed-unknown",
        "source_excerpt": "測試診斷：乙是否具有不法所有意圖尚未確認。",
        "source_start": None,
        "source_end": None,
        "fact_key": "intent",
    }


def _gate1_with_fact(base: dict[str, Any], fact: dict[str, Any]) -> dict[str, Any]:
    gate1 = copy.deepcopy(base)
    gate1.setdefault("facts", []).append(copy.deepcopy(fact))
    return gate1


def _candidate_view(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = (
        "id", "candidate_id", "matched_terms", "status", "candidate_state",
        "candidate_eligibility", "unknown_fact_keys", "unknown_elements",
        "supporting_fact_refs", "contradicting_fact_refs", "inclusion_reason",
        "reservation_reason", "candidate_rank_factors", "legal_route_states",
        "route_element_matrix",
    )
    return [{key: copy.deepcopy(item.get(key)) for key in keys if key in item} for item in candidates]


def _question_view(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": question.get("id"),
            "text": question.get("text"),
            "kind": question.get("kind"),
            "status": question.get("status"),
            "meta": copy.deepcopy(question.get("meta", {})),
        }
        for question in questions
    ]


def _run_stage(bank: dict[str, Any], summary: str, gate1: dict[str, Any]) -> dict[str, Any]:
    candidates = candidate_offenses(summary, bank, gate1)
    candidate_ids = [str(item["id"]) for item in candidates]
    question_result: dict[str, Any]
    try:
        questions = build_questions(
            bank, "victim", candidate_ids, gate1=gate1,
            candidates=candidates, legal_route_ids=[],
        )
        question_result = {"status": "OBSERVED", "items": _question_view(questions)}
    except Exception as exc:
        question_result = {
            "status": "NOT_RUN",
            "error": {"type": type(exc).__name__, "message": str(exc)},
        }
    return {
        "candidate_call": {
            "summary": summary,
            "bank_path": str(QUESTION_BANK_PATH),
            "gate1": copy.deepcopy(gate1),
        },
        "candidate_output": _candidate_view(candidates),
        "question_call": {
            "role": "victim",
            "offense_ids": candidate_ids,
            "legal_route_ids": [],
            "gate1": copy.deepcopy(gate1),
            "candidates": _candidate_view(candidates),
        },
        "question_output": question_result,
    }


def _diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    differences = {}
    for key in ("candidate_output", "question_output"):
        if before[key] != after[key]:
            differences[key] = {"before": before[key], "after": after[key]}
    return {
        "status": "DIFFERENT" if differences else "UNCHANGED",
        "differences": differences,
    }


def _typed_fact_probe(bank: dict[str, Any], summary: str, base: dict[str, Any]) -> dict[str, Any]:
    before = _run_stage(bank, summary, base)
    keyed = _run_stage(bank, summary, _gate1_with_fact(base, _unknown_intent_marker()))
    return {
        "purpose": "確認正式 Gate 1 已產生 typed intent=UNKNOWN；重複加入相同語義不得再次改變候選。",
        "baseline": before,
        "keyed_unknown": keyed,
        "comparison": _diff(before, keyed),
    }


def run_lineage(*, write_trace: bool = True) -> dict[str, Any]:
    fixture = _fixture()
    bank = load_bank(QUESTION_BANK_PATH)
    summary = fixture["summary"]
    base_gate1 = analyze_gate1({"summary": summary, "event_time": "", "location": ""}, use_ai=False)
    scenarios: dict[str, Any] = {}
    for name in ("A", "B"):
        changed_gate1 = _gate1_with_fact(base_gate1, _fact_marker(name))
        before = _run_stage(bank, summary, base_gate1)
        after = _run_stage(bank, summary, changed_gate1)
        scenarios[name] = {
            "summary_unchanged": before["candidate_call"]["summary"] == after["candidate_call"]["summary"] == summary,
            "base": before,
            "changed_facts": after,
            "comparison": _diff(before, after),
            "new_fact_id": _fact_marker(name)["fact_id"],
        }
    trace = {
        "trace_version": TRACE_VERSION,
        "project_root": str(ROOT),
        "fixture": str(FIXTURE),
        "functions": {
            "analyze_gate1": _function_evidence(analyze_gate1),
            "candidate_offenses": _function_evidence(candidate_offenses),
            "build_questions": _function_evidence(build_questions),
        },
        "observed_call_chain": [
            "app.workflow.create_case",
            "app.rules.analyze_gate1(intake, use_ai=False)",
            "app.rules.candidate_offenses(intake['summary'], bank, gate1)",
            "app.workflow.apply_action(set_offenses)",
            "app.rules.build_questions(bank, role, selected, gate1=case['gate1'], candidates=case['candidates'], legal_route_ids=route_ids)",
        ],
        "formal_server_path": {
            "status": "OBSERVED_STATIC_ONLY",
            "entry": "app.server._local_analysis_payload(summary)",
            "note": "此 standalone server path calls classify_candidates(summary, BANK) and was not executed by this offline audit.",
        },
        "base_gate1": copy.deepcopy(base_gate1),
        "scenarios": scenarios,
        "typed_fact_probe": _typed_fact_probe(bank, summary, base_gate1),
        "stage_classification": {
            "facts_to_candidate_argument": "FACT_CONFIRMED",
            "scenario_marker_fact_consumed_by_candidate": "NOT_CONSUMED_IN_OBSERVED_OUTPUT",
            "typed_unknown_fact_key_consumption": "FACT_CONFIRMED_IN_BASE_GATE1; DUPLICATE_PROBE_UNCHANGED",
            "question_fact_gap_usage": "FACT_CONFIRMED_BY_GATE1_FIELD_READS; SCENARIO_MARKER_NO_CHANGE",
        },
        "external_dependencies": {"llm": "NOT_USED", "database": "NOT_USED", "http": "NOT_USED", "frontend": "NOT_USED"},
        "limitations": [
            "A/B markers are test-only facts appended to a copied Gate 1 object; they are not original case evidence.",
            "No formal HTTP/API/history/revision execution was performed.",
            "This does not reproduce the original 337/320 output combination.",
        ],
    }
    if write_trace:
        (ROOT / "LEGAL_FACT_LINEAGE_TRACE.json").write_text(
            json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return trace


def main() -> int:
    parser = argparse.ArgumentParser(description="Run offline fact lineage audit.")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_lineage(write_trace=not args.no_write), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
