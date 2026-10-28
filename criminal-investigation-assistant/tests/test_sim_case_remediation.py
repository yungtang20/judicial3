from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.domain import confirm_answers, confirm_gate1, make_case, update_gate1_facts
from app.question_bank import QuestionBank
from app.storage import RevisionStore, digest


SIM_SUMMARY = "被害人AW001001523遭假投資詐騙，透過LINE與對方聯繫，使用手機、帳號及密碼，依指示匯款兩筆。"
PHONE_SUMMARY = "甲將手機放在便利商店櫃檯旁，乙拿起手機離開。甲表示手機是自己的；乙稱以為手機是別人遺留、不要的物品。手機當時是否仍在甲的持有範圍、乙的認知及其不法所有意圖均未確認。"


def test_sim_fraud_does_not_promote_object_words_to_other_routes():
    bank = QuestionBank()
    case = make_case({
        "event_time": "民國115年10月28日10時",
        "location": "臺北市虛擬地點",
        "summary": SIM_SUMMARY,
        "case_kind": "WITH_VICTIM",
    }, bank)
    confirmed = confirm_gate1(case, bank)
    assert [(item["candidate_id"], item["status"]) for item in confirmed["candidates"]] == [
        ("fraud", "CANDIDATE"),
    ]
    assert confirmed["gate2_required_remaining"] < 60
    assert all(
        route_id not in {"theft", "computer"}
        for question in confirmed["next_question_batch"]
        for route_id in question.get("route_ids", [])
    )


def test_intake_keeps_reported_people_behaviors_payments_and_evidence_separate():
    bank = QuestionBank()
    case = make_case({
        "event_time": "民國115年10月20日",
        "location": "線上社群平台",
        "summary": "報案人林○○表示，對方自稱「陳先生」透過社群平台聯繫，傳送商品照片及訂單資訊，要求先匯款，報案人分兩筆匯款。",
        "case_kind": "WITH_VICTIM",
    }, bank)
    assert [party["display_name"] for party in case["parties"]] == ["林○○", "陳先生"]
    assert len(case["behavior_events"]) >= 1
    assert len(case["payment_events"]) == 2
    assert all(payment["status"] == "REPORTED" for payment in case["payment_events"])
    assert len(case["evidence_items"]) >= 2


def test_revision_schema_has_normalized_case_evidence_and_immutable_history(tmp_path: Path):
    store = RevisionStore(tmp_path / "case.db", tmp_path / "audit.db")
    bank = QuestionBank()
    case = make_case({
        "event_time": "民國115年10月28日10時",
        "location": "臺北市虛擬地點",
        "summary": SIM_SUMMARY,
        "case_kind": "WITH_VICTIM",
    }, bank)
    created = store.create(case, command_id="sim-create", request_digest=digest(case["intake"]))
    with sqlite3.connect(store.path) as db:
        db.execute("PRAGMA foreign_keys=ON")
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"case_party", "behavior_event", "payment_event", "evidence_item", "fact_assertion", "fact_evidence_link", "interview_session"}.issubset(tables)
        assert list(db.execute("PRAGMA foreign_key_list(case_party)"))
        assert list(db.execute("PRAGMA index_list(case_fact)"))
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO case_fact VALUES(?,?,?,?,?,?,?,?)",
                (created["case_id"], 999, "ORPHAN", "event", "x", "TEST", "UNKNOWN", 0.0),
            )
        with pytest.raises(sqlite3.DatabaseError, match="immutable"):
            db.execute(
                "UPDATE case_revision SET state='CORRUPTED' WHERE case_id=? AND revision=1",
                (created["case_id"],),
            )


def _phone_case(bank: QuestionBank):
    return make_case({
        "event_time": "民國115年10月25日19時",
        "location": "臺中市便利商店",
        "summary": PHONE_SUMMARY,
        "case_kind": "WITH_VICTIM",
    }, bank)


def test_phone_case_keeps_theft_and_lost_property_unresolved_until_possession_fact():
    bank = QuestionBank()
    case = update_gate1_facts(
        _phone_case(bank),
        {"facts": {"F-CONDUCT": "手機當時的持有狀態尚待確認。"}},
        bank,
    )
    candidates = {item["candidate_id"]: item for item in case["candidates"]}
    assert {"theft", "embezzlement"}.issubset(candidates)
    assert candidates["theft"]["candidate_role"] == "UNRESOLVED"
    assert candidates["embezzlement"]["candidate_role"] == "UNRESOLVED"
    assert "POSSESSION_STATE" in candidates["theft"]["core_issue_ids"]
    assert "LOST_OR_OUT_OF_POSSESSION" in candidates["embezzlement"]["core_issue_ids"]


def test_phone_case_counterfactual_a_and_b_change_order_without_verdict():
    bank = QuestionBank()
    a = update_gate1_facts(
        _phone_case(bank),
        {"facts": {"F-CONDUCT": "甲一直坐在櫃檯旁，手機放在甲伸手即可取回的位置，乙拿取時看見甲正在注意該手機。"}},
        bank,
    )
    b = update_gate1_facts(
        _phone_case(bank),
        {"facts": {"F-CONDUCT": "甲離開店內一段時間後才發現手機遺失；乙拾得時甲不在現場。"}},
        bank,
    )
    assert a["candidates"][0]["candidate_id"] == "theft"
    assert b["candidates"][0]["candidate_id"] == "embezzlement"
    assert all(item["candidate_role"] != "REJECTED" for item in a["candidates"] + b["candidates"])


def test_phone_case_counterfactual_c_lowers_intent_signal_but_keeps_candidate():
    bank = QuestionBank()
    case = confirm_gate1(_phone_case(bank), bank)
    answers = {item["question_id"]: "乙拿起手機後立即交給店員，表示希望協助尋找失主。" for item in case["next_question_batch"]}
    changed = confirm_answers(case, {"answers": answers}, bank)
    assert changed["fact_assertions"]
    assert any(item["assertion_status"] == "ASSERTED" for item in changed["fact_assertions"])
    embezzlement = next(item for item in changed["candidates"] if item["candidate_id"] == "embezzlement")
    assert any("降低不法所有意圖" in item for item in embezzlement["contrary_facts"])


def test_phone_case_counterfactual_d_preserves_conflicting_assertions_and_issue():
    bank = QuestionBank()
    case = _phone_case(bank)
    case["active_role"] = "suspect"
    case["answers"]["victim"] = {"Q-V": "乙拿著手機離開店內"}
    case["question_batches"] = [{
        "role": "victim", "answered_question_ids": ["Q-V"],
        "questions": [{"question_id": "Q-V", "fact_target": "acquisition_method"}],
    }]
    case["next_question_batch"] = [{
        "question_id": "Q-S", "text": "你如何處理手機？", "role": "suspect",
        "family_id": "property_possession_taking", "fact_target": "acquisition_method",
        "element_type": "conduct", "layer": "element_supplement", "requirement": "REQUIRED",
        "legal_review_status": "HUMAN_REVIEW_REQUIRED", "template_binding": "NONE", "why": "核對",
    }]
    changed = confirm_answers(case, {"answers": {"Q-S": "我沒有把手機帶離店內"}}, bank)
    assert changed["contradiction_issues"][0]["issue_id"] == "ROLE_CONTRADICTION:acquisition_method"
    assert len(changed["fact_assertions"]) == 1
    assert changed["answers"]["victim"]["Q-V"] == "乙拿著手機離開店內"
