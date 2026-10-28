from __future__ import annotations

import copy

import pytest

from app import workflow
from app.rules import analyze_gate1
from tests.helpers import BANK


BASE = (
    "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁。"
    "乙承認拿取手機離開，表示自己以為手機是他人遺留、不要的物品。"
    "目前未確認手機是否仍在甲的持有範圍、乙對手機所有權的認知及乙是否具有不法所有意圖。"
    "手機尚未尋獲。"
)
A_RETAINED = (
    "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁。"
    "甲仍在櫃檯旁，手機在甲伸手可及的位置；乙拿取時看見甲正在注意該手機。"
    "乙承認拿取手機離開；乙是否具有不法所有意圖仍未知。"
)
B_LOST = (
    "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁；甲離開店內後才發現手機遺失。"
    "乙承認拾得手機時甲不在現場，並將手機帶離；乙是否具有不法所有意圖仍未知。"
)
C_HANDOVER = (
    "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁。"
    "乙拿起手機後立即交給店員，並表示希望尋找失主。"
    "乙拿取、交付的時間與經過、店員證述及乙是否具有不法所有意圖仍待核對。"
)
D_CONFLICT = (
    "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁。"
    "乙先否認曾將手機帶離店內；監視器資料顯示乙拿著手機離開。"
    "手機當時是否仍在甲的持有範圍、乙的認知及不法所有意圖仍待確認。"
)


def _gate1(summary: str) -> dict:
    return analyze_gate1(
        {"summary": summary, "event_time": "UNKNOWN", "location": "UNKNOWN"},
        use_ai=False,
    )


def _facts(gate1: dict, key: str) -> list[dict]:
    return [item for item in gate1["facts"] if item.get("fact_key") == key]


def _assert_exact_source(summary: str, fact: dict) -> None:
    assert isinstance(fact["source_start"], int)
    assert isinstance(fact["source_end"], int)
    assert summary[fact["source_start"]:fact["source_end"]] == fact["source_excerpt"]


def test_baseline_preserves_typed_unknown_possession_and_intent() -> None:
    gate1 = _gate1(BASE)
    for key in ("original_possession", "intent"):
        fact = _facts(gate1, key)[0]
        assert fact["value"] == "UNKNOWN"
        assert fact["machine_status"] == "UNKNOWN"
        assert fact["assertion_class"] == "UNKNOWN"
        assert fact["verification_status"] == "UNKNOWN"
        assert fact["source_type"] == "PARTY_STATEMENT"
        _assert_exact_source(BASE, fact)


def test_a_retained_possession_is_an_unverified_statement_not_objective_truth() -> None:
    fact = _facts(_gate1(A_RETAINED), "original_possession")[0]
    assert fact["value"] == "POSSESSION_RETAINED"
    assert fact["assertion_class"] == "ASSERTED"
    assert fact["verification_status"] == "UNVERIFIED"
    assert fact["source_type"] == "PARTY_STATEMENT"
    _assert_exact_source(A_RETAINED, fact)


def test_b_lost_state_does_not_invent_store_or_third_party_control_fact() -> None:
    gate1 = _gate1(B_LOST)
    possession = _facts(gate1, "original_possession")[0]
    assert possession["value"] == "LOST_OR_OUT_OF_POSSESSION"
    assert possession["assertion_class"] == "ASSERTED"
    assert possession["verification_status"] == "UNVERIFIED"
    assert _facts(gate1, "third_party_possession") == []


def test_c_handover_is_separate_from_unknown_intent() -> None:
    gate1 = _gate1(C_HANDOVER)
    handover = _facts(gate1, "post_acquisition_conduct")[0]
    intent = _facts(gate1, "intent")[0]
    assert handover["value"] == "IMMEDIATE_HANDOVER_TO_STORE_STAFF"
    assert handover["assertion_class"] == "ASSERTED"
    assert handover["verification_status"] == "UNVERIFIED"
    assert intent["value"] == "UNKNOWN"
    assert intent["assertion_class"] == "UNKNOWN"


def test_d_denial_and_cctv_are_separate_and_linked_without_resolving_truth() -> None:
    gate1 = _gate1(D_CONFLICT)
    taking = _facts(gate1, "taking")
    assert len(taking) == 2
    denial = next(item for item in taking if item["assertion_class"] == "DENIED")
    cctv = next(item for item in taking if item["source_type"] == "EVIDENCE")
    assert denial["source_type"] == "PARTY_STATEMENT"
    assert denial["verification_status"] == "UNVERIFIED"
    assert cctv["assertion_class"] == "ASSERTED"
    assert cctv["verification_status"] == "UNVERIFIED"
    assert denial["fact_id"] != cctv["fact_id"]
    _assert_exact_source(D_CONFLICT, denial)
    _assert_exact_source(D_CONFLICT, cctv)

    assert len(gate1["contradiction_issues"]) == 1
    issue = gate1["contradiction_issues"][0]
    assert issue["fact_key"] == "taking"
    assert issue["status"] == "CONFLICT_REQUIRES_HUMAN_REVIEW"
    assert set(issue["fact_refs"]) == {denial["fact_id"], cctv["fact_id"]}
    assert issue["denial_fact_ids"] == [denial["fact_id"]]
    assert issue["contrary_fact_ids"] == [cctv["fact_id"]]
    assert issue["subject"] == "乙"
    assert issue["object"] == "手機"
    assert issue["resolved_value"] == "UNKNOWN"


def test_create_case_passes_typed_facts_to_candidate_generator(monkeypatch) -> None:
    observed: dict = {}

    def spy(summary: str, bank: dict, gate1: dict | None = None):
        observed["gate1"] = copy.deepcopy(gate1)
        return []

    monkeypatch.setattr(workflow, "candidate_offenses", spy)
    case = workflow.create_case({"summary": D_CONFLICT, "has_victim": True}, BANK)

    passed = observed["gate1"]
    assert _facts(passed, "original_possession")[0]["value"] == "UNKNOWN"
    assert _facts(passed, "intent")[0]["value"] == "UNKNOWN"
    assert len(_facts(passed, "taking")) == 2
    assert len(passed["contradiction_issues"]) == 1
    assert case["gate1"]["facts"] == passed["facts"]


def test_update_gate1_recomputes_contradiction_links_from_cleaned_facts() -> None:
    case = workflow.create_case({"summary": D_CONFLICT, "has_victim": True}, BANK)
    forged = {"issue_id": "client-forged", "fact_refs": ["missing"]}
    updated = workflow.apply_action(
        case,
        "update_gate1",
        {"gate1": {"facts": case["gate1"]["facts"], "contradiction_issues": [forged]}},
        BANK,
    )
    issue = updated["gate1"]["contradiction_issues"][0]
    assert issue["issue_id"] != "client-forged"
    assert issue["status"] == "CONFLICT_REQUIRES_HUMAN_REVIEW"
    assert len(issue["fact_refs"]) == 2
    assert set(issue["fact_refs"]) <= {item["fact_id"] for item in updated["gate1"]["facts"]}


def test_update_gate1_removing_one_side_clears_conflict() -> None:
    case = workflow.create_case({"summary": D_CONFLICT, "has_victim": True}, BANK)
    retained = [
        item for item in case["gate1"]["facts"]
        if not (item.get("fact_key") == "taking" and item.get("assertion_class") == "DENIED")
    ]
    updated = workflow.apply_action(case, "update_gate1", {"gate1": {"facts": retained}}, BANK)
    assert updated["gate1"]["contradiction_issues"] == []


@pytest.mark.parametrize(
    "summary",
    [
        "甲稱乙承認拿取手機離開。",
        "若乙承認拿取手機離開，應再核對時間。",
        "乙是否承認拿取手機離開仍待詢問。",
        "乙否認曾承認拿取手機離開。",
        "甲表示監視器資料顯示乙拿著手機離開。",
    ],
)
def test_lineage_microgrammar_rejects_quotes_hypotheses_questions_and_nested_denial(summary: str) -> None:
    assert _facts(_gate1(summary), "taking") == []


def test_typed_fact_ids_are_stable_and_no_duplicate_contract_fact_is_emitted() -> None:
    first = _gate1(D_CONFLICT)
    second = _gate1(D_CONFLICT)
    first_ids = [item["fact_id"] for item in first["facts"]]
    second_ids = [item["fact_id"] for item in second["facts"]]
    assert first_ids == second_ids
    contract_rows = [
        (item.get("fact_key"), item.get("source_start"), item.get("source_end"), item.get("value"))
        for item in first["facts"] if item.get("fact_key") in {"taking", "original_possession", "intent"}
    ]
    assert len(contract_rows) == len(set(contract_rows))
