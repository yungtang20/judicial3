from app.case_identity import case_display_name, safe_document_stem
from app.documents import brief_text
from tests.helpers import completed_case


def test_saved_case_name_uses_roc_date_subject_offense_and_officer():
    case = completed_case()

    assert case_display_name(case) == "1151010測試代號遭竊盜案(測試員警)"
    assert safe_document_stem(case) == "1151010測試代號遭竊盜案(測試員警)"


def test_brief_template_overrides_only_configurable_labels():
    case = completed_case()
    case["brief_template"] = {
        "case_reason": "一、受理案由：自訂案件名稱(受理)",
        "summary_label": "五、自訂案情",
        "followup_label": "六、自訂後續處置",
    }

    text = brief_text(case, "victim")

    assert "一、受理案由：自訂案件名稱(受理)" in text
    assert "五、自訂案情：" in text
    assert "六、自訂後續處置：" in text
    assert "（二）本案管轄：測試管轄" in text
    assert "（三）處理員警：警員 測試員警。" in text


def test_empty_brief_template_keeps_current_default_content():
    case = completed_case()

    text = brief_text(case, "victim")

    assert "一、受理案由：1151010測試代號遭竊盜案(測試員警)(受理)" in text
    assert "五、案情摘要：" in text
    assert "六、後續處置：" in text
