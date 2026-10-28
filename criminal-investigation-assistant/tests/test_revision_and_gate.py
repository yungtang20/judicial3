from __future__ import annotations

from pathlib import Path

import pytest

from app.domain import (
    _route_element_questions,
    _disputed_facts,
    add_attachment_metadata,
    analyze_candidates,
    confirm_answers,
    confirm_gate1,
    complete_gate2,
    make_case,
    required_case_numbers,
    start_suspect,
    update_intake,
    update_gate1_facts,
    update_confirmed_answers,
)
from app.question_bank import QuestionBank
from app.storage import IdempotencyConflict, RevisionStore, digest
from app.workflow import Workflow


def _case(bank: QuestionBank):
    return make_case({
        "event_time": "民國115年10月27日10時",
        "location": "臺北市中正區虛擬路1號",
        "summary": "甲將乙暫放桌面的皮夾拿走，是否仍在乙支配範圍尚待確認。",
        "case_kind": "WITH_VICTIM",
    }, bank)


def test_revision_is_immutable_and_idempotent(tmp_path: Path):
    bank = QuestionBank()
    store = RevisionStore(tmp_path / "cases.db", tmp_path / "audit.db")
    raw = _case(bank)
    created = store.create(raw, command_id="create-1", request_digest=digest(raw["intake"]))
    updated = store.commit_revision(
        created["case_id"], expected_revision=1, command_id="gate1-1",
        request_digest=digest({"action": "CONFIRM_GATE1"}), action="CONFIRM_GATE1",
        mutate=lambda case: confirm_gate1(case, bank),
    )
    repeated = store.commit_revision(
        created["case_id"], expected_revision=1, command_id="gate1-1",
        request_digest=digest({"action": "CONFIRM_GATE1"}), action="CONFIRM_GATE1",
        mutate=lambda case: (_ for _ in ()).throw(AssertionError("must not rerun")),
    )
    assert created["revision"] == 1
    assert updated["revision"] == 2
    assert repeated["revision"] == 2
    assert store.get(created["case_id"], 1)["state"] == "GATE1_REVIEW"
    assert store.get(created["case_id"], 2)["state"] == "GATE2_QA"
    with pytest.raises(IdempotencyConflict):
        store.commit_revision(
            created["case_id"], expected_revision=2, command_id="gate1-1",
            request_digest="different", action="CONFIRM_GATE1", mutate=lambda case: case,
        )


def test_element_gap_storage_keeps_same_text_for_distinct_child_routes(tmp_path: Path):
    bank = QuestionBank()
    store = RevisionStore(tmp_path / "cases.db", tmp_path / "audit.db")
    raw = _case(bank)
    created = store.create(raw, command_id="create-child-gaps", request_digest=digest(raw["intake"]))
    repeated = [gap for gap in created["element_gaps"] if gap["element"] == "未遂或既遂"]
    assert len({gap["child_route_id"] for gap in repeated}) >= 2
    assert store.get(created["case_id"])["revision"] == 1


def test_answer_batch_recomputes_candidates_and_intake_edit_invalidates(tmp_path: Path):
    bank = QuestionBank()
    case = confirm_gate1(_case(bank), bank)
    answers = {item["question_id"]: "這是虛構測試回答。" for item in case["next_question_batch"]}
    answered = confirm_answers(case, {"answers": answers}, bank)
    assert len(answered["answers"]["victim"]) == 5
    assert answered["next_question_batch"]
    statement_facts = [fact for fact in answered["facts"] if fact["status"] == "STATEMENT"]
    assert len(statement_facts) == 5
    assert all(fact["provenance"].startswith("ANSWER:victim:") for fact in statement_facts)
    changed = update_intake(answered, {"summary": "甲保管乙的手機後拒不返還。"}, bank)
    assert changed["state"] == "GATE1_REVIEW"
    assert changed["answers"]["victim"] == {}
    assert changed["approvals"] == {}
    assert any(item["candidate_id"] == "embezzlement" for item in changed["candidates"])


def test_updating_confirmed_answer_invalidates_downstream_and_preserves_statement_provenance():
    bank = QuestionBank()
    case = confirm_gate1(_case(bank), bank)
    batch = case["next_question_batch"]
    case = confirm_answers(case, {"answers": {item["question_id"]: "原回答" for item in batch}}, bank)
    question_id = batch[0]["question_id"]
    case["approvals"] = {"gate2:victim": {"status": "AI_REVIEWED", "basis_digest": "old"}}
    case["case_numbers"] = {"proof_number": "OLD"}
    changed = update_confirmed_answers(case, {"answers": {question_id: "修正回答"}}, bank)
    assert changed["answers"]["victim"][question_id] == "修正回答"
    assert changed["approvals"] == {}
    assert changed["case_numbers"] == {}
    assert changed["state"] == "GATE2_QA"
    fact = next(item for item in changed["facts"] if item["fact_id"] == f"F-ANSWER-VICTIM-{question_id}")
    assert fact["value"] == "修正回答"
    assert fact["status"] == "STATEMENT"


def test_intake_requires_separate_time_place_summary():
    bank = QuestionBank()
    with pytest.raises(ValueError, match="均為必填"):
        make_case({"event_time": "", "location": "", "summary": "只有摘要", "case_kind": "WITH_VICTIM"}, bank)


def test_gate1_fact_correction_is_user_confirmed_and_recomputes_candidate():
    bank = QuestionBank()
    case = _case(bank)
    changed = update_gate1_facts(case, {"facts": {"F-OBJECT-1": "該皮夾原由乙保管，甲未拿走。"}}, bank)
    fact = next(item for item in changed["facts"] if item["fact_id"] == "F-OBJECT-1")
    assert fact["status"] == "USER_CONFIRMED"
    assert fact["provenance"] == "USER:GATE1_CORRECTION"
    assert next(item for item in changed["candidates"] if item["candidate_id"] == "theft")["status"] == "LOWERED"


def test_gate1_has_explicit_fact_matrix_placeholders():
    categories = {fact["category"] for fact in _case(QuestionBank())["facts"]}
    assert {"conduct", "mental_state", "result", "property_or_rights", "causation", "evidence"}.issubset(categories)


def test_gate1_fact_correction_cannot_overwrite_intake_fact():
    bank = QuestionBank()
    case = _case(bank)
    with pytest.raises(ValueError, match="只能修正"):
        update_gate1_facts(case, {"facts": {"F-TIME": "改寫時間"}}, bank)


def test_gate1_same_value_cannot_be_promoted_to_user_confirmed():
    bank = QuestionBank()
    case = _case(bank)
    original = next(item for item in case["facts"] if item["fact_id"] == "F-OBJECT-1")
    with pytest.raises(ValueError, match="沒有可儲存"):
        update_gate1_facts(case, {"facts": {"F-OBJECT-1": original["value"]}}, bank)
    assert original["status"] == "UNKNOWN"


def test_source_pack_drift_fails_closed_until_explicit_rebase():
    bank = QuestionBank()
    workflow = Workflow(bank)
    case = _case(bank)
    case["source_pins"]["question_bank"] = "stale"
    with pytest.raises(ValueError, match="來源版本已變更"):
        workflow.apply(case, "CONFIRM_GATE1", {})
    rebased = workflow.apply(case, "REBASE_SOURCE_PACK", {})
    assert rebased["source_pins"]["question_bank"] == bank.fingerprint
    assert rebased["state"] == "GATE1_REVIEW"
    assert rebased["answers"] == {"victim": {}, "suspect": {}, "witness": {}}


def test_attachment_metadata_invalidates_gates():
    bank = QuestionBank()
    case = _case(bank)
    case["approvals"] = {"gate2:victim": {"status": "AI_REVIEWED", "basis_digest": "old"}}
    changed = add_attachment_metadata(case, {
        "attachment_id": "00000000-0000-4000-8000-000000000001",
        "filename": "evidence.txt",
        "sha256": "a" * 64,
        "size": 10,
        "storage_name": f"{'a' * 64}.bin",
    })
    assert changed["attachments"][0]["filename"] == "evidence.txt"
    assert changed["approvals"] == {}
    assert changed["state"] == "GATE1_REVIEW"


@pytest.mark.parametrize(
    ("summary", "expected"),
    [
        ("甲拿走乙暫放桌面的皮夾。", "theft"),
        ("甲原本替乙保管手機，之後拒不返還。", "embezzlement"),
        ("甲破壞門窗後拿走財物。", "aggravated_theft"),
    ],
)
def test_property_candidates_change_with_fact_pattern(summary: str, expected: str):
    assert expected in {item["candidate_id"] for item in analyze_candidates(summary)}


@pytest.mark.parametrize(
    ("summary", "expected"),
    [
        ("涉嫌內亂罪嫌。", "state_security"),
        ("公務員涉嫌收受賄賂。", "duty"),
        ("行為人抗拒員警執行職務。", "obstruction"),
        ("有人提供利益影響證言。", "judicial_integrity"),
        ("候選人涉嫌賄選。", "voting"),
        ("現場有人聚眾施暴。", "disorder"),
        ("受拘禁人趁隙脫逃。", "escape"),
        ("涉嫌湮滅證據。", "evidence"),
        ("證人涉嫌偽證。", "accusation"),
        ("查獲疑似偽鈔。", "currency"),
        ("涉嫌偽造支票。", "securities"),
        ("使用不實度量衡交易。", "weights_measures"),
        ("在網路散布猥褻物。", "obscenity"),
        ("已有婚姻又涉嫌重婚。", "marriage"),
        ("涉嫌破壞墳墓。", "graves_religion"),
        ("涉嫌囤積必需品。", "agriculture_commerce"),
        ("查獲鴉片。", "opium"),
        ("涉嫌網路賭博。", "gambling"),
        ("涉嫌非法使之流產。", "abortion"),
        ("將無自救力之人棄置。", "abandonment"),
        ("涉嫌人口販運。", "trafficking"),
        ("本件為少年保護事件。", "juvenile"),
        ("被害人表示遭受家庭暴力。", "domestic_violence"),
        ("通報兒童虐待。", "child_protection"),
        ("申訴職場性騷擾。", "gender_equality"),
    ],
)
def test_remaining_parent_routes_have_explicit_safe_trigger(summary: str, expected: str):
    assert expected in {item["candidate_id"] for item in analyze_candidates(summary)}


def test_candidate_rules_cover_every_snapshot_parent_route():
    from app.domain import ROUTE_RULES
    bank = QuestionBank()
    snapshot_parents = {
        record["parent_route_id"] for record in bank.bank["records"]
        if record.get("route_resolution_status") == "SNAPSHOT_CHILD_ROUTE"
    }
    assert {route_id for route_id, _family_id, _keywords in ROUTE_RULES} == snapshot_parents


@pytest.mark.parametrize(
    ("summary", "route_id"),
    [
        ("查獲槍枝與彈藥。", "firearms"),
        ("涉嫌參與犯罪組織。", "organized_crime"),
        ("涉嫌隱匿犯罪所得進行洗錢。", "money_laundering"),
        ("涉嫌收受贓物。", "stolen_goods"),
    ],
)
def test_extension_route_keyword_is_visible_but_fail_closed(summary: str, route_id: str):
    candidate = next(item for item in analyze_candidates(summary) if item["candidate_id"] == route_id)
    assert candidate["status"] == "UNSUPPORTED_ROUTE"
    assert candidate["source_status"] == "BLOCKED_NO_FORMAL_CROSSWALK"


def test_unsupported_route_cannot_complete_gate2():
    bank = QuestionBank()
    case = make_case({
        "event_time": "民國115年10月28日",
        "location": "臺北市測試地點",
        "summary": "查獲槍枝與彈藥。",
        "case_kind": "NO_VICTIM",
        "initial_route_id": "firearms",
    }, bank)
    case["answers"]["suspect"] = {f"Q-{index}": "測試" for index in range(5)}
    with pytest.raises(ValueError, match="禁止產生完整筆錄"):
        complete_gate2(case, bank)


def test_gate2_cannot_finish_while_required_questions_remain():
    bank = QuestionBank()
    case = _case(bank)
    case["answers"]["victim"] = {f"Q-{index}": "測試" for index in range(5)}
    with pytest.raises(ValueError, match="必要問句未完成"):
        complete_gate2(case, bank)


def test_complete_gate2_sets_role_specific_approval_after_all_required_answers():
    bank = QuestionBank()
    case = confirm_gate1(_case(bank), bank)
    for _ in range(30):
        if case.get("gate2_required_remaining") == 0:
            break
        batch = case["next_question_batch"]
        case = confirm_answers(case, {"answers": {item["question_id"]: "不知道" for item in batch}}, bank)
    complete_gate2(case, bank)
    assert "gate2:victim" in case["approvals"]
    assert case["state"] == "CASE_NUMBERS"


def test_candidate_uses_child_route_elements_and_answered_gap_status():
    bank = QuestionBank()
    candidate = next(item for item in analyze_candidates("甲拿走乙的皮夾。", bank) if item["candidate_id"] == "theft")
    assert len(candidate["child_routes"]) == 4
    assert any(gap["element"] == "為自己或第三人不法所有之意圖" for child in candidate["child_routes"] for gap in child["element_gaps"])
    target_gap = next(
        gap for child in candidate["child_routes"] for gap in child["element_gaps"]
        if gap["element"] == "為自己或第三人不法所有之意圖"
    )
    answered = next(item for item in analyze_candidates(
        "甲拿走乙的皮夾。", bank, {target_gap["route_element_key"]},
    ) if item["candidate_id"] == "theft")
    mental_gaps = [gap for child in answered["child_routes"] for gap in child["element_gaps"] if gap["element_type"] == "mental_state"]
    assert mental_gaps
    assert sum(gap["status"] == "ANSWERED_PENDING_REVIEW" for gap in mental_gaps) == 1
    assert any(gap["status"] == "UNKNOWN" for gap in mental_gaps)


def test_each_route_element_gets_a_stable_neutral_supplement_question():
    bank = QuestionBank()
    case = _case(bank)
    confirm_gate1(case, bank)
    route_questions = []
    for _ in range(20):
        batch = case["next_question_batch"]
        if not batch:
            break
        route_questions.extend(item for item in batch if item.get("route_element_keys"))
        case = confirm_answers(case, {"answers": {item["question_id"]: "虛構測試回答" for item in batch}}, bank)
        if route_questions:
            break
    assert route_questions
    question = route_questions[0]
    assert question["question_id"].startswith("R-VICTIM-")
    assert question["text"].count("？") == 1
    assert "罪名成立" not in question["text"]
    assert question["route_element_keys"]
    assert "回答只用於確認或排除候選" in question["why"]


@pytest.mark.parametrize(("summary", "expected_route_id"), [
    ("甲當場辱罵依法執行職務的員警並抗拒盤查。", "obstruction_140_insult_official"),
    ("甲酒駕遭攔查，呼氣酒測超過標準。", "public_danger_185_3_impaired_driving"),
    ("甲趁乙不注意拿走乙的皮夾及手機。", "theft_320_1_movable"),
])
def test_route_element_questions_prioritize_child_route_supported_by_case_facts(summary, expected_route_id):
    bank = QuestionBank()
    case = make_case({
        "event_time": "民國115年10月27日10時",
        "location": "臺北市中正區虛擬路1號",
        "summary": summary,
        "case_kind": "WITH_VICTIM",
    }, bank)
    confirm_gate1(case, bank)
    questions = _route_element_questions(case)
    assert questions
    assert expected_route_id in questions[0]["route_ids"]
    assert questions[0]["route_priority"] > 0
    assert questions[0]["requirement"] == "REQUIRED"


def test_gate2_cannot_finish_before_relevant_child_route_elements_are_answered():
    bank = QuestionBank()
    case = confirm_gate1(_case(bank), bank)
    required_questions = [
        item for item in _route_element_questions(case)
        if item["requirement"] == "REQUIRED"
    ]
    assert required_questions
    static_required = {
        item["question_id"]: "虛構測試回答"
        for item in bank.template_questions("victim") + bank.questions(
            role="victim",
            family_ids=sorted({item["family_id"] for item in case["candidates"]}),
            route_ids=[item["candidate_id"] for item in case["candidates"]],
            active_preconditions={"NONE"},
        )
        if item["requirement"] == "REQUIRED"
    }
    case["answers"]["victim"] = static_required
    with pytest.raises(ValueError, match="必要問句未完成"):
        complete_gate2(case, bank)


def test_confirm_gate1_rebuilds_legacy_candidate_gaps_without_element_keys():
    bank = QuestionBank()
    case = _case(bank)
    for candidate in case["candidates"]:
        for child in candidate.get("child_routes", []):
            for gap in child.get("element_gaps", []):
                gap.pop("route_element_key", None)
    confirm_gate1(case, bank)
    assert case["state"] == "GATE2_QA"
    assert all(
        gap.get("route_element_key")
        for candidate in case["candidates"]
        for child in candidate.get("child_routes", [])
        for gap in child.get("element_gaps", [])
    )


def test_contrary_fact_lowers_candidate_without_erasing_it():
    candidates = analyze_candidates("甲拿走皮夾，但經乙同意取走。")
    theft = next(item for item in candidates if item["candidate_id"] == "theft")
    assert theft["status"] == "LOWERED"
    assert theft["contrary_facts"]


def test_question_schedule_inserts_family_core_before_remaining_company_template():
    bank = QuestionBank()
    case = _case(bank)
    all_questions = []
    for _ in range(10):
        batch = case["next_question_batch"]
        if not batch:
            break
        all_questions.extend(batch)
        case = confirm_answers(case, {"answers": {item["question_id"]: "測試回答" for item in batch}}, bank)
        if any(item["layer"] == "family_skeleton" for item in all_questions) and any(
            item["layer"] == "company_template" and isinstance(item.get("template_binding"), dict)
            and item["template_binding"].get("order", 999) > 3 for item in all_questions
        ):
            break
    family_index = next(i for i, item in enumerate(all_questions) if item["layer"] == "family_skeleton")
    later_template_index = next(
        i for i, item in enumerate(all_questions)
        if item["layer"] == "company_template" and item["template_binding"].get("order", 999) > 3
    )
    assert family_index < later_template_index


def test_cross_role_difference_is_disputed_not_promoted_to_fact():
    case = {
        "answers": {"victim": {"Q-V": "對方拿走皮夾"}, "suspect": {"Q-S": "我沒有拿走皮夾"}},
        "question_batches": [
            {"role": "victim", "answered_question_ids": ["Q-V"], "questions": [{"question_id": "Q-V", "fact_target": "acquisition_method"}]},
            {"role": "suspect", "answered_question_ids": ["Q-S"], "questions": [{"question_id": "Q-S", "fact_target": "acquisition_method"}]},
        ],
    }
    disputes = _disputed_facts(case)
    assert disputes == [{
        "fact_target": "acquisition_method",
        "status": "DISPUTED",
        "victim_statements": ["對方拿走皮夾"],
        "suspect_statements": ["我沒有拿走皮夾"],
        "note": "僅標示雙方陳述不一致，不判定任一方陳述為真。",
    }]


def test_confirm_answers_preserves_disputed_facts_for_follow_up():
    bank = QuestionBank()
    case = _case(bank)
    case["active_role"] = "suspect"
    case["answers"]["victim"] = {"Q-V": "對方拿走皮夾"}
    case["question_batches"] = [{
        "role": "victim",
        "answered_question_ids": ["Q-V"],
        "questions": [{"question_id": "Q-V", "fact_target": "acquisition_method", "element_type": "conduct"}],
    }]
    case["next_question_batch"] = [{
        "question_id": "Q-S", "text": "請說明財物如何移動？", "role": "suspect",
        "family_id": "property_possession_taking", "fact_target": "acquisition_method",
        "element_type": "conduct", "layer": "element_supplement", "requirement": "REQUIRED",
        "legal_review_status": "HUMAN_REVIEW_REQUIRED", "template_binding": "NONE", "why": "測試",
    }]
    changed = confirm_answers(case, {"answers": {"Q-S": "我沒有拿走皮夾"}}, bank)
    assert changed["disputed_facts"][0]["status"] == "DISPUTED"
    assert any("acquisition_method" in fact for item in changed["candidates"] for fact in item["contrary_facts"])


def test_case_number_conditions_and_role_isolation():
    bank = QuestionBank()
    case = make_case({
        "event_time": "民國115年10月27日10時",
        "location": "臺北市虛擬路1號",
        "summary": "被害人AW001001523表示遭假投資詐騙後匯款。",
        "case_kind": "WITH_VICTIM",
    }, bank)
    assert required_case_numbers(case) == {
        "proof_number": True, "women_child_number": True, "case_165_number": True,
    }
    case["answers"]["victim"] = {"T-V001-01": "被害人回答"}
    changed = start_suspect(case, bank)
    assert changed["answers"]["victim"] == {"T-V001-01": "被害人回答"}
    assert changed["answers"]["suspect"] == {}
    assert changed["active_role"] == "suspect"


def test_no_victim_enters_gate5_after_gate1():
    bank = QuestionBank()
    case = make_case({
        "event_time": "民國115年10月27日10時",
        "location": "臺北市虛擬路1號",
        "summary": "警方查獲甲持有毒品。",
        "case_kind": "NO_VICTIM",
        "initial_route_id": "drugs",
    }, bank)
    assert confirm_gate1(case, bank)["state"] == "GATE5_QA"
    selected = next(item for item in case["candidates"] if item["candidate_id"] == "drugs")
    assert selected["selected_by_user"] is True


def test_no_victim_requires_user_selected_initial_route():
    bank = QuestionBank()
    with pytest.raises(ValueError, match="必須由使用者指定"):
        make_case({
            "event_time": "民國115年10月27日10時",
            "location": "臺北市虛擬路1號",
            "summary": "警方查獲不明物品，仍待檢驗。",
            "case_kind": "NO_VICTIM",
        }, bank)


def test_selected_route_is_kept_without_keyword_and_route_change_invalidates():
    bank = QuestionBank()
    case = make_case({
        "event_time": "民國115年10月27日10時",
        "location": "臺北市虛擬路1號",
        "summary": "警方查獲不明物品，仍待檢驗。",
        "case_kind": "NO_VICTIM",
        "initial_route_id": "drugs",
    }, bank)
    assert next(item for item in case["candidates"] if item["candidate_id"] == "drugs")["selected_by_user"]
    case["answers"]["suspect"] = {"Q-1": "舊回答"}
    case["approvals"] = {"gate5:suspect": {"status": "AI_REVIEWED", "basis_digest": "old"}}
    changed = update_intake(case, {"initial_route_id": "gambling"}, bank)
    assert changed["intake"]["initial_route_id"] == "gambling"
    assert changed["answers"]["suspect"] == {}
    assert changed["approvals"] == {}
    assert next(item for item in changed["candidates"] if item["candidate_id"] == "gambling")["selected_by_user"]


def test_procedure_module_activates_only_from_explicit_case_signal():
    bank = QuestionBank()
    plain = make_case({
        "event_time": "民國115年10月27日10時",
        "location": "臺北市虛擬路1號",
        "summary": "甲打傷乙。",
        "case_kind": "WITH_VICTIM",
    }, bank)
    domestic = make_case({
        "event_time": "民國115年10月27日10時",
        "location": "臺北市虛擬路1號",
        "summary": "甲與同居伴侶乙發生衝突，甲打傷乙。",
        "case_kind": "WITH_VICTIM",
    }, bank)
    plain_ids = {item["question_id"] for item in bank.questions(
        role="victim", family_ids=["human_violence"], route_ids=["injury"],
        active_preconditions={"NONE"},
    )}
    assert not any(question_id.startswith("M-DV-") for question_id in plain_ids)
    # Company-template questions are asked first, so verify activation through the bank contract.
    from app.domain import _active_preconditions
    assert "DOMESTIC_RELATIONSHIP_CONFIRMED" in _active_preconditions(domestic)
    assert "DOMESTIC_RELATIONSHIP_CONFIRMED" not in _active_preconditions(plain)
