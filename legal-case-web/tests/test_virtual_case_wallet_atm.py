from __future__ import annotations

from app.document_validation import validate_brief_completeness, validate_docx_structure, validate_interview_completeness
from app.documents import brief_text, build_document
from app.rules import required_case_numbers
from app.workflow import apply_action, create_case
from tests.helpers import BANK, intake


def test_virtual_wallet_atm_case_runs_from_facts_to_two_documents():
    summary = (
        "115\u5e7409\u670810\u65e521\u6642\uff0c\u6211\u6700\u5f8c\u770b\u5230\u6211\u7684\u9322\u5305\u662f\u5728\u81fa\u5317\u5e02\u4f69\u5bb9\u5340\u4f69\u5bb9\u8def1\u865f\u7684\u591c\u5e97\u88e1\uff0c"
        "\u6211\u8fd4\u5bb6\u5f8c\u624d\u767c\u73fe\u6211\u7684\u9322\u5305\u4e0d\u898b\u4e86\uff0c\u7136\u5f8c\u5728115\u5e7409\u670821\u65e510\u6642\u5728\u81fa\u5317\u5e02\u8a60\u68e0\u5340\u8a60\u68e0\u8def1\u865f\uff0c"
        "\u63a5\u5230\u9280\u884c\u7684\u7c21\u8a0a\u8aaa\uff0c\u6211\u5728115\u5e7409\u670820\u65e512\u6642\u6709\u4eba\u4f7f\u7528\u6211\u7684\u5361\u7247\u63d0\u9818\u4e00\u7b462\u842c\u5143\u7684\u8cbb\u7528\uff0c"
        "\u4f46\u6211\u4e0d\u662f\u6211\u672c\u4eba\u63d0\u9818\u7684\u3002"
    )
    raw = intake(summary=summary)
    raw["event_time"] = ""
    raw["location"] = ""
    case = create_case(raw, BANK)
    assert "115\u5e7409\u670810\u65e521\u6642" in case["intake"]["event_time"]
    assert "\u81fa\u5317\u5e02\u4f69\u5bb9\u5340\u4f69\u5bb9\u8def1\u865f" in case["intake"]["location"]
    assert {item["id"] for item in case["candidates"]} >= {"fraud", "theft", "embezzlement"}

    case = apply_action(case, "auto_prepare", {}, BANK)
    # 現行流程由系統在 Gate 1 後自動整理候選與問句，承辦人不再逐項重選罪章。
    assert case["state"] == "GATE2_QA"
    assert len(case["questions"]) <= 20
    assert len({question["text"] for question in case["questions"]}) == len(case["questions"])

    case = apply_action(case, "save_profile", {
        "profile": {"name": "\u865b\u64ec\u88ab\u5bb3\u4eba", "national_id": "A123456789", "sex": "\u7537", "education": "\u5927\u5b78"},
        "session": {"start_time": "2026-09-21T10:30", "end_time": "2026-09-21T11:30", "location": "\u6e2c\u8a66\u6240"},
    }, BANK)
    case = apply_action(case, "save_answers", {"answers": {question["id"]: "UNKNOWN" for question in case["questions"]}}, BANK)
    case = apply_action(case, "approve_gate2", {"confirmed": True}, BANK)
    assert case["state"] == "CASE_NUMBERS"
    assert validate_interview_completeness(case, "victim") == []
    interview_artifact = build_document(case, "victim", "interview")
    assert 1 <= interview_artifact.page_count <= 8
    assert validate_docx_structure(interview_artifact.data) == []

    case = apply_action(case, "update_output_context", {"output_context": {
        "jurisdiction": "\u81fa\u5317\u5e02\u8a60\u68e0\u5340\u8a60\u68e0\u8def1\u865f\u8f44\u5340",
        "officer": "\u865b\u64ec\u53d7\u7406\u54e1\u8b66",
        "report_time": "2026-09-21T10:00",
    }}, BANK)
    case = apply_action(case, "save_case_numbers", {"case_numbers": {"proof": "Z123456789", "women_child": "", "case_165": "165-TEST"}, "brief_template": {}}, BANK)
    assert case["state"] == "OUTPUT_READY"
    assert required_case_numbers(case) == ["proof"]
    assert validate_brief_completeness(case, "victim") == []
    text = brief_text(case, "victim")
    assert "\u81fa\u5317\u5e02\u8a60\u68e0\u5340\u8a60\u68e0\u8def1\u865f\u8f44\u5340" in text
    assert "\u865b\u64ec\u53d7\u7406\u54e1\u8b66" in text
    assert "115\u5e749\u670821\u65e510\u664200\u5206" in text
    brief_artifact = build_document(case, "victim", "brief")
    assert validate_docx_structure(brief_artifact.data) == []


def test_ambiguous_theft_or_embezzlement_case_keeps_single_brief_reason_and_factual_summary():
    summary = (
        "民國115年10月20日20時30分，林雅婷在臺北市中正區忠孝西路1號某咖啡店用餐，"
        "將皮夾放在座位旁椅子上，離席約5分鐘前往洗手間，返回後發現皮夾不見。"
        "店員看見一名男子拿起皮夾後離開，監視器無法確認取物時皮夾是否仍在林雅婷可立即控制範圍。"
        "男子後來交回皮夾，稱以為是他人遺失物，但現金少新臺幣1,000元；現有監視器及店員證詞。"
    )
    raw = intake(summary=summary)
    raw["station"] = "○○所"
    case = create_case(raw, BANK)
    case = apply_action(case, "auto_prepare", {}, BANK)

    questions = case["questions"]
    assert 0 < len(questions) <= 20
    assert len({question["text"] for question in questions}) == len(questions)

    case = apply_action(case, "save_profile", {
        "profile": {"name": "林雅婷", "national_id": "A123456789"},
        "session": {
            "start_time": "2026-10-26T09:00",
            "end_time": "2026-10-26T09:30",
            "location": "虛擬派出所",
        },
    }, BANK)
    case = apply_action(case, "save_answers", {
        "answers": {question["id"]: "壓力測試回答" for question in questions},
    }, BANK)
    case = apply_action(case, "approve_gate2", {"confirmed": True}, BANK)
    case = apply_action(case, "update_output_context", {"output_context": {
        "jurisdiction": "臺北市中正區虛擬派出所",
        "officer": "虛擬警員林○○",
        "report_time": "2026-10-26T09:00",
    }}, BANK)
    case = apply_action(case, "save_case_numbers", {
        "case_numbers": {"proof": "V1151020003", "women_child": "", "case_165": ""},
        "brief_template": {},
    }, BANK)

    text = brief_text(case, "victim")
    reason_line = next(line for line in text.splitlines() if line.startswith("一、受理案由："))
    assert reason_line.count("遭") == 1
    assert "、" not in reason_line.split("：", 1)[1]
    summary_block = text.split("五、案情摘要：\n", 1)[1].split("\n六、後續處置：", 1)[0]
    assert "仍應查明" not in summary_block
    assert "候選" not in summary_block
    assert "虛擬派出所報告" in text
    assert "V1151020003" in text
