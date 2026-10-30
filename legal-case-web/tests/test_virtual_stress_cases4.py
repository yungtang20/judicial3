"""Virtual case stress test batch 4: complex multi-offense and edge cases.

Covers: complex multi-crime, ambiguous facts, edge cases, real court case patterns.
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


def test_vc4_01_complex_fraud():
    """Complex fraud: investment scam with multiple victims."""
    summary = "115年01月01日至115年06月30日，被告以虛假投資平台詐騙多人，總金額500萬元，並洗錢隱匿。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc4_02_domestic_violence_complex():
    """Domestic violence: physical + psychological abuse."""
    summary = "115年01月01日至115年06月30日，被告多次對配偶施暴，並恐嚇威脅，造成配偶心理創傷。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 2


def test_vc4_03_drug_trafficking():
    """Drug trafficking: selling drugs."""
    summary = "115年01月01日，被告販賣毒品給多人，並持有大量毒品。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc4_04_sexual_assault_complex():
    """Complex sexual assault: multiple acts."""
    summary = "115年01月01日，被告對被害人強制性交，並偷拍性愛影片威脅。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 2


def test_vc4_05_theft_embezzlement_fraud():
    """Three-way confusion: theft vs embezzlement vs fraud."""
    summary = "115年01月01日，被告受託保管財物，後將其變賣，並以假投資騙取更多資金。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 2


def test_vc4_06_property_crime_complex():
    """Property crime complex: theft + damage + trespass."""
    summary = "115年01月01日，被告侵入住宅，破壞門鎖，竊取財物並毀損家具。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 2


def test_vc4_07_violent_crime_complex():
    """Violent crime complex: assault + intimidation + threat."""
    summary = "115年01月01日，被告毆打被害人，並恐嚇威脅，造成被害人受傷。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 2


def test_vc4_08_financial_crime_complex():
    """Financial crime: fraud + money laundering + forgery."""
    summary = "115年01月01日，被告偽造文書，詐騙資金，並透過多個帳戶洗錢。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 2


def test_vc4_09_digital_crime_complex():
    """Digital crime: computer intrusion + data theft."""
    summary = "115年01月01日，被告駭客入侵公司伺服器，竊取客戶資料並植入勒索軟體。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc4_10_no_victim_complex():
    """No-victim complex: drugs + gambling + public danger."""
    summary = "115年01月01日，被告在住處持有毒品，經營賭場，並酒後駕車。"
    case = _run_case(summary, has_victim=False)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc4_11_edge_case_ambiguous():
    """Edge case: ambiguous facts requiring multiple interpretations."""
    summary = "115年01月01日，被告拿取他人財物，但聲稱是借用，被害人表示未同意。"
    case = _run_case(summary)
    candidate_ids = {item["id"] for item in case["candidates"]}
    assert len(candidate_ids) >= 1


def test_vc4_12_edge_case_minimal():
    """Edge case: minimal information."""
    summary = "被告偷了東西。"
    case = _run_case(summary)
    # May or may not generate candidates; verify no crash
    assert case["state"] in ("GATE1_REVIEW", "GATE2_QA", "CASE_NUMBERS", "OUTPUT_READY")