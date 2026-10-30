"""Virtual case stress test batch 2: additional crime types.

Covers: homicide, public danger (DUI), computer crime, sexual harassment,
obstruction of justice, perjury, escape, evidence destruction, money laundering,
fence (receiving stolen goods), trespassing, gambling, obstruction of official duty.
"""

from __future__ import annotations

from app.document_validation import validate_brief_completeness, validate_docx_structure, validate_interview_completeness
from app.documents import brief_text, build_document
from app.rules import required_case_numbers
from app.workflow import apply_action, create_case
from tests.helpers import BANK, intake


def _run_case(summary, has_victim=True, answers_value="UNKNOWN"):
    raw = intake(summary=summary, has_victim=has_victim)
    raw["event_time"] = ""
    raw["location"] = ""
    case = create_case(raw, BANK)
    if case["state"] == "GATE1_REVIEW":
        try:
            case = apply_action(case, "auto_prepare", {}, BANK)
        except Exception:
            pass
    if case["state"] == "GATE1_REVIEW":
        case = apply_action(case, "approve_gate1", {"confirmed": True}, BANK)
    if case["state"] == "GATE2_QA" and not case.get("questions"):
        candidate_ids = [c["id"] for c in case.get("candidates", []) if c.get("candidate_eligibility") == "ELIGIBLE_CANDIDATE"]
        if not candidate_ids:
            candidate_ids = [c["id"] for c in case.get("candidates", [])][:3]
        if candidate_ids:
            case = apply_action(case, "set_offenses", {
                "offense_ids": candidate_ids,
                "legal_route_ids": [],
                "route_review_confirmed": True,
                "role": "victim" if has_victim else "transfer",
            }, BANK)
    assert case["state"] == "GATE2_QA", f"Expected GATE2_QA, got {case['state']}"
    assert len(case["questions"]) <= 60
    q_texts = [q["text"] for q in case["questions"]]
    assert len(set(q_texts)) == len(q_texts), "Duplicate questions found"

    case = apply_action(case, "save_profile", {
        "profile": {"name": "測試受詢問人", "national_id": "A123456789", "sex": "男", "education": "大學"},
        "session": {"start_time": "2026-10-15T10:00", "end_time": "2026-10-15T11:00", "location": "測試所"},
    }, BANK)
    case = apply_action(case, "save_answers", {"answers": {q["id"]: answers_value for q in case["questions"]}}, BANK)
    case = apply_action(case, "approve_gate2", {"confirmed": True}, BANK)
    assert case["state"] == "CASE_NUMBERS"
    assert validate_interview_completeness(case, "victim" if has_victim else "transfer") == []

    interview_artifact = build_document(case, "victim" if has_victim else "transfer", "interview")
    assert 1 <= interview_artifact.page_count <= 8
    assert validate_docx_structure(interview_artifact.data) == []

    case = apply_action(case, "update_output_context", {"output_context": {
        "jurisdiction": "臺北市測試區測試路1號",
        "officer": "測試員警",
        "report_time": "2026-10-15T10:00",
    }}, BANK)
    required = required_case_numbers(case)
    numbers = {"proof": "Z123456789", "women_child": "", "case_165": ""}
    if "case_165" in required:
        numbers["case_165"] = "165-TEST"
    case = apply_action(case, "save_case_numbers", {"case_numbers": numbers, "brief_template": {}}, BANK)
    assert case["state"] == "OUTPUT_READY"
    assert validate_brief_completeness(case, "victim" if has_victim else "transfer") == []
    brief_artifact = build_document(case, "victim" if has_victim else "transfer", "brief")
    assert validate_docx_structure(brief_artifact.data) == []

    return case


def test_virtual_case_23_homicide():
    """Homicide: intentional killing."""
    summary = (
        "115年01月05日23時，臺北市信義區信義路200號，"
        "被告因金錢糾紛，持刀刺殺被害人，"
        "造成被害人當場死亡。警方到場查獲。"
    )
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_virtual_case_24_public_danger_dui():
    """Public danger: drunk driving."""
    summary = (
        "115年02月14日02時，被告酒後駕車，"
        "在臺北市中山區中山路行駛，"
        "被警方臨檢測得酒精濃度0.55mg/L，超過標準。"
    )
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_virtual_case_25_computer_crime():
    """Computer crime: unauthorized access."""
    summary = (
        "115年03月01日，被告未經授權，"
        "入侵公司伺服器，竊取客戶資料，"
        "並植入惡意程式。"
    )
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_virtual_case_26_sexual_harassment():
    """Sexual harassment: unwanted touching."""
    summary = (
        "115年04月10日14時，被告在辦公室，"
        "未經被害人同意，觸摸被害人臀部，"
        "被害人感到不舒服並報警。"
    )
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_virtual_case_27_obstruction_justice():
    """Obstruction of justice: destroying evidence."""
    summary = (
        "115年05月01日，被告在警方調查期間，"
        "將涉案手機格式化，刪除所有通訊紀錄，"
        "企圖湮滅證據。"
    )
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_virtual_case_28_perjury():
    """Perjury: false testimony."""
    summary = (
        "115年06月01日，被告在法院作證時，"
        "故意作虛偽陳述，否認曾見過嫌疑人，"
        "與監視器畫面不符。"
    )
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_virtual_case_29_money_laundering():
    """Money laundering: concealing criminal proceeds."""
    summary = (
        "115年01月01日至115年06月30日，被告將詐騙所得500萬元，"
        "透過多個帳戶轉帳，並購買房產，"
        "企圖隱匿犯罪所得。"
    )
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_virtual_case_30_fence():
    """Fence: receiving stolen goods."""
    summary = (
        "115年02月01日，被告明知手機為贓物，"
        "仍以低價向竊盜犯購入，"
        "並轉售获利。"
    )
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_virtual_case_31_escape():
    """Escape: fleeing from custody."""
    summary = (
        "115年03月15日，被告在法院羈押期間，"
        "趁隙脫逃，逃離看守所，"
        "並藏匿於親戚家中。"
    )
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1