"""GATE-009：財產取走案件的 typed fact 完整性契約。

這些案例刻意使用一般自然語言，不依賴「未知」「未確認」「待確認」等提示詞，
以確認 UNKNOWN 是由情境與契約產生，而不是由摘要文字被動觸發。
"""

from __future__ import annotations

import copy

from app import workflow
from app.analysis_contract import decorate_facts
from app.rules import FACT_UNKNOWN_LABELS, analyze_gate1
from tests.helpers import BANK, intake


# 一般自然語言：沒有「意圖未知」等提示詞。
PLAIN_TAKING = "甲把行動電話放在便利商店櫃檯旁，乙拿走該行動電話後離開。"
# 拾得後帶離，但沒有交代店員／店家是否接手。
PICKUP_AND_REMOVE = "乙在店內拾得手機後將手機帶離，甲表示手機為其所有。"
# 所有人離開後才發現遺失。
LOST_AFTER_LEAVING = (
    "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁；"
    "甲離開店內後才發現手機遺失。"
    "乙承認拾得手機時甲不在現場，並將手機帶離。"
)
# 否認與外部證據並存。
DENIAL_AND_CCTV = (
    "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁。"
    "乙先否認曾將手機帶離店內；監視器資料顯示乙拿著手機離開。"
)

REQUIRED_KEYS = (
    "original_possession",
    "third_party_possession",
    "intent",
    "ownership_knowledge",
    "taking",
    "post_acquisition_conduct",
)


def _gate1(summary: str) -> dict:
    gate1 = analyze_gate1(
        {"summary": summary, "event_time": "UNKNOWN", "location": "UNKNOWN"},
        use_ai=False,
    )
    # 契約欄位（fact_key_status／provenance）由 Gate 1 邊界統一套用。
    gate1["facts"] = decorate_facts(gate1["facts"])
    return gate1


def _typed(gate1: dict, key: str) -> list[dict]:
    return [item for item in gate1["facts"] if item.get("fact_key") == key]


def _by_key(gate1: dict) -> dict[str, dict]:
    return {
        item["fact_key"]: item
        for item in gate1["facts"]
        if item.get("fact_key") in REQUIRED_KEYS
    }


def _case(summary: str) -> dict:
    return workflow.create_case(intake(summary=summary), BANK)


def test_plain_natural_language_creates_intent_unknown_without_prompt_words() -> None:
    assert "未知" not in PLAIN_TAKING
    assert "未確認" not in PLAIN_TAKING

    gate1 = _gate1(PLAIN_TAKING)
    facts = _by_key(gate1)

    for key in REQUIRED_KEYS:
        assert key in facts, f"{key} 不得因摘要未提及而省略"

    # 摘要明示「乙拿走」，因此 taking 是來源陳述（不是已查證的事實）。
    assert facts["taking"]["value"] == "TAKING_OR_REMOVAL_REPORTED"
    assert facts["taking"]["assertion_class"] == "ASSERTED"
    assert facts["taking"]["verification_status"] == "UNVERIFIED"

    # 其餘適用但資料不足的欄位一律明確 UNKNOWN。
    for key in set(REQUIRED_KEYS) - {"taking"}:
        assert facts[key]["value"] == "UNKNOWN"
        assert facts[key]["assertion_class"] == "UNKNOWN"
        assert facts[key]["verification_status"] == "UNKNOWN"
        assert facts[key]["machine_status"] == "UNKNOWN"
        assert facts[key]["fact_key_status"] == "CLASSIFIED"
        assert facts[key]["provenance"]["source_ref"] == "intake.summary"

    # 契約補齊的 UNKNOWN 必須同步投影到 unknowns 標籤。
    for key in set(REQUIRED_KEYS) - {"taking"}:
        assert FACT_UNKNOWN_LABELS[key] in gate1["unknowns"]


def test_pickup_and_removal_keeps_third_party_possession_explicit() -> None:
    gate1 = _gate1(PICKUP_AND_REMOVE)
    third_party = _typed(gate1, "third_party_possession")
    assert [item["value"] for item in third_party] == ["UNKNOWN"]
    assert third_party[0]["assertion_class"] == "UNKNOWN"
    # 「在店內拾得」表示店員／店家可能接續管領，因此欄位必須存在。
    assert FACT_UNKNOWN_LABELS["third_party_possession"] in gate1["unknowns"]


def test_owner_leaving_does_not_assert_complete_loss_of_possession() -> None:
    gate1 = _gate1(LOST_AFTER_LEAVING)

    original = _typed(gate1, "original_possession")
    assert [item["value"] for item in original] == ["UNKNOWN"]
    assert all(item["assertion_class"] == "UNKNOWN" for item in original)

    # 原始描述仍是可追溯的來源陳述；推論狀態另存且標示未驗證。
    event = _typed(gate1, "possession_event")[0]
    inference = _typed(gate1, "possession_inference")[0]
    assert event["source_excerpt"] in LOST_AFTER_LEAVING
    assert inference["assertion_class"] == "INFERRED"
    assert inference["source_type"] == "SYSTEM_INFERENCE"
    assert inference["machine_status"] == "INFERENCE"
    assert inference["inference_review"] == "HUMAN_REVIEW_REQUIRED"

    # 第三人管領同樣不得由「甲不在現場」推定。
    assert [item["value"] for item in _typed(gate1, "third_party_possession")] == ["UNKNOWN"]


def test_denial_and_evidence_stay_separate_and_contradiction_is_traceable() -> None:
    gate1 = _gate1(DENIAL_AND_CCTV)
    taking = _typed(gate1, "taking")
    assert len(taking) == 2
    denial = next(item for item in taking if item["assertion_class"] == "DENIED")
    cctv = next(item for item in taking if item["source_type"] == "EVIDENCE")
    assert denial["fact_status"] == "當事人陳述"
    assert cctv["fact_status"] == "證據線索"
    assert denial["fact_id"] != cctv["fact_id"]

    issue = gate1["contradiction_issues"][0]
    assert issue["status"] == "CONFLICT_REQUIRES_HUMAN_REVIEW"
    assert set(issue["fact_refs"]) == {denial["fact_id"], cctv["fact_id"]}
    # 系統不自行判定何者為真。
    assert issue["resolved_value"] == "UNKNOWN"
    assert denial["verification_status"] == "UNVERIFIED"
    assert cctv["verification_status"] == "UNVERIFIED"


def test_events_only_update_matches_create_case_contract() -> None:
    base = _case("有人未經同意拿走店內物品。")
    base = workflow.apply_action(base, "approve_gate1", {"confirmed": True}, BANK)
    updated = workflow.apply_action(
        base, "update_gate1", {"gate1": {"events": [LOST_AFTER_LEAVING]}}, BANK
    )
    direct = _case(LOST_AFTER_LEAVING)

    def rows(case: dict) -> list[tuple]:
        return [
            (
                item.get("fact_key"),
                item.get("value"),
                item.get("assertion_class"),
                item.get("source_type"),
                item.get("verification_status"),
                item.get("fact_key_status"),
                bool(item.get("provenance")),
            )
            for item in case["gate1"]["facts"]
        ]

    assert rows(updated) == rows(direct)
    assert updated["gate1"]["unknowns"] == direct["gate1"]["unknowns"]
    assert updated["gate1"]["contradiction_issues"] == direct["gate1"]["contradiction_issues"]
    assert all(item.get("provenance") for item in updated["gate1"]["facts"])
    assert all(
        item["fact_key_status"] == "CLASSIFIED"
        for item in updated["gate1"]["facts"]
        if item.get("fact_key")
    )


def test_facts_update_and_deletion_resync_unknown_labels_and_contradictions() -> None:
    case = _case(DENIAL_AND_CCTV)

    # 刪除否認事實：矛盾必須消失，且不得留下指向已刪除事實的紀錄。
    retained = [
        item
        for item in case["gate1"]["facts"]
        if not (item.get("fact_key") == "taking" and item.get("assertion_class") == "DENIED")
    ]
    removed = workflow.apply_action(case, "update_gate1", {"gate1": {"facts": retained}}, BANK)
    assert removed["gate1"]["contradiction_issues"] == []
    remaining_ids = {item["fact_id"] for item in removed["gate1"]["facts"]}
    for issue in removed["gate1"]["contradiction_issues"]:
        assert set(issue["fact_refs"]) <= remaining_ids

    # 把 intent 由 UNKNOWN 改為明示陳述：UNKNOWN 標籤必須同步移除。
    facts = copy.deepcopy(removed["gate1"]["facts"])
    intent = next(item for item in facts if item.get("fact_key") == "intent")
    intent.update({
        "value": "INTENT_ALLEGED_BY_SUMMARY",
        "assertion_class": "ASSERTED",
        "assertion_status": "EXPLICIT_SOURCE_ASSERTION",
        "fact_status": "當事人陳述",
        "machine_status": "FACT",
        "source_excerpt": "甲表示乙拿走手機後離開。",
    })
    updated = workflow.apply_action(case, "update_gate1", {"gate1": {"facts": facts}}, BANK)
    assert FACT_UNKNOWN_LABELS["intent"] not in updated["gate1"]["unknowns"]
    assert FACT_UNKNOWN_LABELS["original_possession"] in updated["gate1"]["unknowns"]

    # 再改回 UNKNOWN：標籤必須回復且只出現一次。
    restored_facts = copy.deepcopy(updated["gate1"]["facts"])
    restored_intent = next(item for item in restored_facts if item.get("fact_key") == "intent")
    restored_intent.update({
        "value": "UNKNOWN",
        "assertion_class": "UNKNOWN",
        "assertion_status": "UNKNOWN",
        "fact_status": "未知",
        "source_excerpt": "",
        "machine_status": "UNKNOWN",
    })
    restored = workflow.apply_action(
        case, "update_gate1", {"gate1": {"facts": restored_facts}}, BANK
    )
    assert restored["gate1"]["unknowns"].count(FACT_UNKNOWN_LABELS["intent"]) == 1


def test_gate1_to_questions_flow_still_receives_the_same_facts() -> None:
    case = _case(PLAIN_TAKING)
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

    facts = _by_key(case["gate1"])
    assert set(REQUIRED_KEYS) <= set(facts)
    assert facts["intent"]["value"] == "UNKNOWN"
    assert case["questions"], "Gate 1 之後仍須產生問句"

    unknown_targets = {key for key, item in facts.items() if item["value"] == "UNKNOWN"}
    for question in case["questions"]:
        target = question.get("meta", {}).get("fact_target")
        if target in unknown_targets:
            assert question["meta"].get("known_from_summary") is not True
            assert question.get("status") != "AUTO_FILLED_FROM_SUMMARY"

    # 候選仍只是候選，不得因本契約補齊而變成已核定答案。
    for candidate in case.get("candidates", []):
        assert candidate.get("candidate_review_status") != "APPROVED"
