"""Virtual case stress test batch 3: remaining crime types.

Covers: liberty (unlawful detention), obstruction of official duty,
judicial integrity, voting, disorder, currency (counterfeiting),
securities (forgery of securities), weights/measures, marriage (bigamy),
graves/religion, agriculture/commerce, opium, trafficking, juvenile,
child protection, gender equality, abortion, abandonment.
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


def test_vc3_01_liberty():
    """Unlawful detention: restricting freedom."""
    summary = "115年01月10日，被告將被害人鎖在房間內，限制其行動自由，長達3小時。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_02_obstruction_official():
    """Obstruction of official duty."""
    summary = "115年02月05日，被告在警方執行查封時，推擠員警並阻撓查封作業。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_03_judicial_integrity():
    """Obstruction of justice: witness retaliation."""
    summary = "115年03月01日，被告因不滿證人作證，對證人進行報復威脅。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_04_voting():
    """Vote buying."""
    summary = "115年04月01日，被告以每票500元買票，要求選民投票給特定候選人。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_05_disorder():
    """Disorder: unlawful assembly."""
    summary = "115年05月01日，被告聚眾50人，在公共場所煽惑他人違法，造成社會秩序混亂。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_06_currency():
    """Counterfeiting: fake money."""
    summary = "115年06月01日，被告製造偽鈔，並在市場使用。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_07_securities():
    """Forgery of securities."""
    summary = "115年07月01日，被告偽造股票憑證，向他人行使。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_08_weights_measures():
    """Weights and measures fraud."""
    summary = "115年08月01日，被告使用不準確的磅秤，短斤少兩販賣商品。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_09_marriage():
    """Bigamy."""
    summary = "115年09月01日，被告重婚，與他人登記結婚。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_10_graves():
    """Desecration of graves."""
    summary = "115年10月01日，被告挖開墳墓，竊取陪葬品。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_11_agriculture():
    """Agriculture/commerce offense."""
    summary = "115年11月01日，被告在商品上使用虛偽標記，欺騙消費者。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_12_opium():
    """Opium: poppy cultivation."""
    summary = "115年12月01日，警方在被告農地發現罌粟種植。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_13_gambling():
    """Gambling: operating illegal casino."""
    summary = "115年01月15日，被告在臺北市萬華區經營地下賭場，接受下注。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_14_abortion():
    """Abortion: illegal termination."""
    summary = "115年02月15日，被告未經合法程序，協助他人墮胎。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_15_abandonment():
    """Abandonment: abandoning dependent."""
    summary = "115年03月15日，被告遺棄無自救力之老人，使其陷入危險。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_16_trafficking():
    """Human trafficking."""
    summary = "115年04月15日，被告以債務約束方式，強迫被害人勞動。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_17_child_protection():
    """Child protection: child abuse."""
    summary = "115年05月15日，被告對其子女施以兒童虐待。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_18_gender_equality():
    """Gender equality: workplace sexual harassment."""
    summary = "115年06月15日，被告在職場對下屬進行性騷擾，多次傳送不當訊息。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_19_juvenile():
    """Juvenile case."""
    summary = "115年07月15日，16歲少年被告竊取超商商品。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc3_20_obscenity():
    """Obscenity: distributing obscene materials."""
    summary = "115年08月15日，被告在網路散布猥褻影像。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1