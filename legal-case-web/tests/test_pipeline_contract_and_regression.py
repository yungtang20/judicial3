from __future__ import annotations

import pytest

from app.workflow import apply_action, create_case
from tests.helpers import BANK


BASE = (
    "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁；"
    "目前未確認甲是否仍能實際支配手機。乙承認拿取手機離開，"
    "表示自己以為手機是他人遺留、不要的物品；尚未確認乙是否具有不法所有意圖，"
    "手機目前尚未尋獲。"
)


def _case(extra: str = "") -> dict:
    return create_case({"summary": BASE + extra, "has_victim": True}, BANK)


def test_case_contract_is_additive_and_keeps_unknowns_unresolved():
    case = _case()

    assert case["case_id"]
    assert case["gate1"]["facts"]
    for fact in case["gate1"]["facts"]:
        assert {"source_type", "assertion_class", "verification_status", "fact_key_status", "provenance"} <= fact.keys()
        assert fact["assertion_class"] in {"ASSERTED", "ADMITTED", "DENIED", "INFERRED", "UNKNOWN"}
        assert fact["fact_key_status"] == ("CLASSIFIED" if fact.get("fact_key") else "UNCLASSIFIED")

    for candidate in case["candidates"]:
        assert {"candidate_status", "readiness_status", "candidate_review_status", "route_status", "fact_refs"} <= candidate.keys()
        assert candidate["candidate_review_status"] == "PENDING"
        assert candidate["readiness_status"] == "NEEDS_FACTS"
        assert candidate["candidate_status"] != "REJECTED"
        assert candidate["candidate_status"] != "PRIMARY" or not candidate.get("unknown_fact_keys")


@pytest.mark.parametrize(
    ("label", "extra", "expected_phrase"),
    [
        ("A", "甲仍在櫃檯旁，手機在其伸手可及的位置，乙拿取時看見甲注意該手機。", "伸手可及"),
        ("B", "甲離開店內後才發現手機遺失；乙拾得時甲不在場，沒有證據顯示乙知道所有人是誰。", "遺失"),
        ("C", "乙拿取手機後立即交給店員，表示希望尋找失主。", "交給店員"),
        ("D", "乙先否認曾將手機帶離店內，但監視器顯示乙拿著手機離開。", "監視器"),
    ],
)
def test_scenario_fact_changes_are_traceable_without_legal_conclusion(label: str, extra: str, expected_phrase: str):
    case = _case(extra)
    source_text = "；".join(str(item.get("source_excerpt", "")) for item in case["gate1"]["facts"])
    assert expected_phrase in source_text, label
    assert all(item.get("candidate_review_status") != "APPROVED" for item in case["candidates"])
    assert all(item.get("candidate_status") != "REJECTED" for item in case["candidates"])
    if label == "D":
        assert "否認" in source_text
        assert "監視器" in source_text


def test_question_contract_points_to_fact_gap_and_preserves_legacy_metadata():
    prepared = apply_action(_case(), "auto_prepare", {}, BANK)
    assert prepared["questions"]
    for question in prepared["questions"]:
        contract = question["contract"]
        assert contract["question_id"] == question["id"]
        assert contract["gap_id"]
        assert contract["follow_up_condition"]
        assert "fact_target" in question["meta"]
        assert "legal_targets" in question["meta"]


def test_explicit_admitted_and_denied_statuses_are_not_rewritten():
    case = _case()
    updated = apply_action(
        case,
        "update_gate1",
        {
            "gate1": {
                "facts": [
                    {
                        "fact_id": "fact:admitted",
                        "fact_key": "taking_action",
                        "value": "乙承認拿取手機",
                        "source_ref": "suspect.statement.1",
                        "source_excerpt": "乙承認拿取手機。",
                        "fact_status": "當事人陳述",
                        "machine_status": "FACT",
                        "assertion_class": "ADMITTED",
                    },
                    {
                        "fact_id": "fact:denied",
                        "fact_key": "intent",
                        "value": "不法所有意圖未知",
                        "source_ref": "suspect.statement.2",
                        "source_excerpt": "乙否認有不法所有意圖。",
                        "fact_status": "當事人陳述",
                        "machine_status": "DISPUTED",
                        "assertion_class": "DENIED",
                    },
                ]
            }
        },
        BANK,
    )
    facts = updated["gate1"]["facts"]
    assert [item["assertion_class"] for item in facts] == ["ADMITTED", "DENIED"]
    assert all(item["fact_key_status"] == "CLASSIFIED" for item in facts)
