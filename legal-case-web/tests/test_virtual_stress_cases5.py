"""Virtual case stress test batch 5: additional edge cases and real-world patterns.

Covers: more complex scenarios, boundary cases, and real court case patterns.
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


def test_vc5_01_real_theft_case():
    """Real pattern: convenience store theft."""
    summary = "115年01月15日14時，被告在臺北市信義區便利商店，趁店員不注意時，將架上商品放入包包後離開，未結帳。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "theft" in candidate_ids


def test_vc5_02_real_fraud_case():
    """Real pattern: investment scam."""
    summary = "115年02月01日，被告在投資群組宣稱高報酬，誘使被害人匯款50萬元至指定帳戶，後失聯。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "fraud" in candidate_ids


def test_vc5_03_real_drug_case():
    """Real pattern: drug possession during traffic stop."""
    summary = "115年03月01日23時，警方臨檢時在被告車內發現毒品及吸食器，被告否認持有。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "drugs" in candidate_ids


def test_vc5_04_real_assault_case():
    """Real pattern: bar fight injury."""
    summary = "115年04月01日02時，被告在酒吧與被害人發生口角，持酒瓶毆打被害人頭部，造成撕裂傷。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "injury" in candidate_ids


def test_vc5_05_real_defamation_case():
    """Real pattern: social media defamation."""
    summary = "115年05月01日，被告在Facebook公開發文，誹謗被害人，貼文被轉發百次。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "defamation" in candidate_ids


def test_vc5_06_real_forgery_case():
    """Real pattern: fake document."""
    summary = "115年06月01日，被告偽造被害人簽名，製作本票向第三人行使，騙取現金。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "forgery" in candidate_ids


def test_vc5_07_real_damage_case():
    """Real pattern: property destruction."""
    summary = "115年07月01日，被告因糾紛砸毀被害人汽車擋風玻璃，修復費8萬元。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "damage" in candidate_ids


def test_vc5_08_real_intimidation_case():
    """Real pattern: threat message."""
    summary = "115年08月01日，被告傳送恐嚇訊息給被害人，稱『再不還錢就讓你見不到明天』。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "intimidation" in candidate_ids


def test_vc5_09_real_stalking_case():
    """Real pattern: repeated harassment."""
    summary = "114年10月01日至114年12月15日，被告多次跟蹤被害人上下班，反覆聯絡騷擾，被害人感到恐懼。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "stalking" in candidate_ids


def test_vc5_10_real_public_danger_case():
    """Real pattern: drunk driving."""
    summary = "115年09月01日02時，被告酒後駕車，酒精濃度0.55mg/L，被警方查獲。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "public_danger" in candidate_ids


def test_vc5_11_real_sexual_harassment_case():
    """Real pattern: workplace harassment."""
    summary = "115年10月01日，被告在職場對下屬進行性騷擾，多次傳送不當訊息。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "sexual_harassment" in candidate_ids


def test_vc5_12_real_gambling_case():
    """Real pattern: illegal gambling."""
    summary = "115年11月01日，被告在臺北市萬華區經營地下六合彩賭場。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "gambling" in candidate_ids


def test_vc5_13_real_drug_trafficking_case():
    """Real pattern: drug selling."""
    summary = "115年12月01日，被告販賣毒品給多人，並持有大量毒品。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "drugs" in candidate_ids


def test_vc5_14_real_escape_case():
    """Real pattern: escape from custody."""
    summary = "115年01月15日，被告在法院羈押期間，趁隙脫逃，逃離看守所。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "escape" in candidate_ids


def test_vc5_15_real_property_damage_case():
    """Real pattern: property destruction."""
    summary = "115年02月15日，被告持石頭砸毀被害人汽車擋風玻璃，修復費8萬元。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert "damage" in candidate_ids