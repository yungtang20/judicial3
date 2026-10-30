"""Gate 1 事實契約在正式流程中的傳遞、狀態同步與證據分離。

這些測試只驗證「事實是否被正確建立、保存、傳遞與消費」，不驗證候選罪名
是否正確（五案法律標註仍為 PENDING_HUMAN_REVIEW）。

對應的唯讀稽核腳本：``tools/gate1_fact_contract_audit.py``。
"""

from __future__ import annotations

import copy

import pytest

from app import rules, workflow
from app.rules import FACT_UNKNOWN_LABELS
from tests.helpers import BANK
from tests.test_gate1_fact_lineage_contract import (
    A_RETAINED,
    B_LOST,
    BASE,
    C_HANDOVER,
    D_CONFLICT,
)
from tools.gate1_fact_contract_audit import CASES

TYPED_KEYS = {
    "original_possession",
    "third_party_possession",
    "ownership_knowledge",
    "intent",
    "taking",
    "post_acquisition_conduct",
}


def _case(summary: str) -> dict:
    return workflow.create_case({"summary": summary, "has_victim": True}, BANK)


def _typed(facts: list[dict], key: str | None = None) -> list[dict]:
    return [
        item for item in facts
        if item.get("fact_key") in TYPED_KEYS and (key is None or item.get("fact_key") == key)
    ]


def _unknown_values(facts: list[dict]) -> set[str]:
    return {
        item.get("fact_key") for item in facts
        if item.get("value") == "UNKNOWN" and item.get("fact_key") in TYPED_KEYS
    }


def test_audit_script_cases_match_lineage_fixtures() -> None:
    """稽核腳本與契約測試必須使用同一組五案文字，避免證據與測試漂移。"""
    assert CASES == {
        "BASE": BASE,
        "A_RETAINED": A_RETAINED,
        "B_LOST": B_LOST,
        "C_HANDOVER": C_HANDOVER,
        "D_CONFLICT": D_CONFLICT,
    }


@pytest.mark.parametrize("summary", [BASE, A_RETAINED, B_LOST, C_HANDOVER, D_CONFLICT])
def test_analyze_candidates_hands_case_facts_to_candidate_generator(monkeypatch, summary: str) -> None:
    case = _case(summary)
    expected_keys = _unknown_values(case["gate1"]["facts"])
    captured: dict = {}
    real = rules.candidate_offenses

    def spy(summary_text, bank, gate1=None):
        captured["gate1"] = copy.deepcopy(gate1)
        return real(summary_text, bank, gate1)

    monkeypatch.setattr(workflow, "analyze_candidates_v3", lambda *args, **kwargs: None)
    monkeypatch.setattr(workflow, "candidate_offenses", spy)
    updated = workflow.apply_action(case, "analyze_candidates", {"external_ai_consent": True}, BANK)

    received = captured["gate1"]
    assert received is not None, "analyze_candidates 必須把 Gate 1 傳給 candidate_offenses"
    assert received["facts"] == updated["gate1"]["facts"]
    assert _unknown_values(received["facts"]) == expected_keys

    # 候選端必須以 facts 判斷缺哪些事實，而不是一律列出所有相依欄位。
    for candidate in updated["candidates"]:
        if candidate["id"] == "theft":
            assert set(candidate["unknown_fact_keys"]) == expected_keys & {"original_possession", "intent"}


def test_analyze_candidates_does_not_attach_stale_facts_to_rewritten_summary(monkeypatch) -> None:
    case = _case(D_CONFLICT)
    captured: dict = {}
    real = rules.candidate_offenses

    def spy(summary_text, bank, gate1=None):
        captured["gate1"] = copy.deepcopy(gate1)
        return real(summary_text, bank, gate1)

    monkeypatch.setattr(workflow, "analyze_candidates_v3", lambda *args, **kwargs: None)
    monkeypatch.setattr(workflow, "candidate_offenses", spy)
    workflow.apply_action(
        case,
        "analyze_candidates",
        {"external_ai_consent": True, "summary": D_CONFLICT + "（承辦人另行改寫）"},
        BANK,
    )

    assert captured["gate1"] is None, "摘要已改寫時，span 對不上的 facts 不得傳給下游"


def test_update_gate1_removes_stale_unknown_label_and_keeps_unrelated_unknowns() -> None:
    case = _case(BASE)
    non_typed_unknowns = [
        item for item in case["gate1"]["unknowns"]
        if item not in FACT_UNKNOWN_LABELS.values()
    ]
    assert FACT_UNKNOWN_LABELS["intent"] in case["gate1"]["unknowns"]

    kept = [
        item for item in copy.deepcopy(case["gate1"]["facts"])
        if item.get("fact_key") != "intent"
    ]
    updated = workflow.apply_action(case, "update_gate1", {"gate1": {"facts": kept}}, BANK)
    after = updated["gate1"]

    assert _typed(after["facts"], "intent") == []
    assert FACT_UNKNOWN_LABELS["intent"] not in after["unknowns"]
    # 仍為 UNKNOWN 的 typed 事實必須保留標籤，且不得刪掉承辦人自行填寫的其他未知項。
    assert FACT_UNKNOWN_LABELS["original_possession"] in after["unknowns"]
    assert all(item in after["unknowns"] for item in non_typed_unknowns)
    assert after["unknowns"] == list(dict.fromkeys(after["unknowns"]))


def test_update_gate1_restores_unknown_label_when_unknown_fact_returns() -> None:
    case = _case(BASE)
    intent_fact = _typed(case["gate1"]["facts"], "intent")[0]
    kept = [
        item for item in copy.deepcopy(case["gate1"]["facts"])
        if item.get("fact_key") != "intent"
    ]
    stripped = workflow.apply_action(case, "update_gate1", {"gate1": {"facts": kept}}, BANK)
    assert FACT_UNKNOWN_LABELS["intent"] not in stripped["gate1"]["unknowns"]

    restored = workflow.apply_action(
        stripped,
        "update_gate1",
        {"gate1": {"facts": [*kept, copy.deepcopy(intent_fact)]}},
        BANK,
    )
    facts = _typed(restored["gate1"]["facts"], "intent")
    assert len(facts) == 1
    assert facts[0]["value"] == "UNKNOWN"
    assert FACT_UNKNOWN_LABELS["intent"] in restored["gate1"]["unknowns"]


def test_update_gate1_keeps_unknown_label_for_assertion_class_only_unknown() -> None:
    """客戶端只標 assertion_class=UNKNOWN 時，仍不得被當成已知或否定。"""
    case = _case(BASE)
    kept = [
        item for item in copy.deepcopy(case["gate1"]["facts"])
        if item.get("fact_key") != "intent"
    ]
    intent = copy.deepcopy(_typed(case["gate1"]["facts"], "intent")[0])
    intent["machine_status"] = "FACT"
    intent["assertion_class"] = "UNKNOWN"
    updated = workflow.apply_action(
        case, "update_gate1", {"gate1": {"facts": [*kept, intent]}}, BANK
    )
    assert FACT_UNKNOWN_LABELS["intent"] in updated["gate1"]["unknowns"]


@pytest.mark.parametrize("summary", [BASE, A_RETAINED, B_LOST, C_HANDOVER, D_CONFLICT])
def test_update_gate1_keeps_facts_derived_state_stable_when_facts_do_not_change(summary: str) -> None:
    case = _case(summary)
    keys = (
        "unknowns", "evidence_leads", "verified_evidence", "consent_states",
        "causation", "causal_edges", "legal_characterizations", "contradiction_issues",
    )
    before = {key: copy.deepcopy(case["gate1"].get(key)) for key in keys}
    updated = workflow.apply_action(
        case,
        "update_gate1",
        {"gate1": {"facts": copy.deepcopy(case["gate1"]["facts"])}},
        BANK,
    )
    for key in keys:
        assert updated["gate1"].get(key) == before[key], key


def test_update_gate1_does_not_flatten_denial_and_evidence(monkeypatch) -> None:
    case = _case(D_CONFLICT)
    updated = workflow.apply_action(
        case,
        "update_gate1",
        {"gate1": {"facts": copy.deepcopy(case["gate1"]["facts"])}},
        BANK,
    )
    taking = _typed(updated["gate1"]["facts"], "taking")
    assert len(taking) == 2
    denial = next(item for item in taking if item["assertion_class"] == "DENIED")
    cctv = next(item for item in taking if item["source_type"] == "EVIDENCE")
    assert denial["fact_id"] != cctv["fact_id"]
    issue = updated["gate1"]["contradiction_issues"][0]
    assert set(issue["fact_refs"]) == {denial["fact_id"], cctv["fact_id"]}
    assert issue["resolved_value"] == "UNKNOWN"


def test_formal_flow_passes_facts_into_build_questions_and_unknowns_stay_unknown(monkeypatch) -> None:
    case = _case(D_CONFLICT)
    captured: dict = {}
    real_build = workflow.build_questions

    def spy(*args, **kwargs):
        captured["gate1"] = copy.deepcopy(kwargs.get("gate1"))
        result = real_build(*args, **kwargs)
        for attr in ("question_coverage_by_route", "last_validation", "pruned_questions"):
            if hasattr(real_build, attr):
                setattr(spy, attr, getattr(real_build, attr))
        return result

    monkeypatch.setattr(workflow, "build_questions", spy)
    case = workflow.apply_action(case, "approve_gate1", {"confirmed": True}, BANK)
    case = workflow.apply_action(
        case,
        "set_offenses",
        {
            "offense_ids": ["theft"],
            "legal_route_ids": ["theft_320_1_movable"],
            "route_review_confirmed": True,
            "role": "victim",
        },
        BANK,
    )

    received = captured["gate1"]
    assert received is not None
    assert received["facts"] == case["gate1"]["facts"]
    assert _typed(received["facts"]), "build_questions 必須收到 typed facts"

    # UNKNOWN 不得在問句層被當成已知答案。
    unknown_targets = {
        item["fact_key"] for item in _typed(case["gate1"]["facts"])
        if item["value"] == "UNKNOWN"
    }
    # GATE-009：完整契約要求適用欄位一律留下明確 UNKNOWN，因此改為子集檢查，
    # 但 possession 與 intent 仍必須是 UNKNOWN。
    assert {"original_possession", "intent"} <= unknown_targets
    assert unknown_targets <= {
        "original_possession",
        "third_party_possession",
        "intent",
        "ownership_knowledge",
        "taking",
        "post_acquisition_conduct",
    }
    for question in case["questions"]:
        target = question.get("meta", {}).get("fact_target")
        if target in unknown_targets:
            assert question["meta"].get("known_from_summary") is not True
            assert question.get("status") != "AUTO_FILLED_FROM_SUMMARY"
