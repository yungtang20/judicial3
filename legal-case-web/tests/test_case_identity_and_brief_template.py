from app.case_identity import case_display_name, safe_document_stem
from app.documents import brief_text
from tests.helpers import completed_case


def test_saved_case_name_uses_roc_date_subject_offense_and_officer():
    case = completed_case()

    assert case_display_name(case) == "1151010測試代號遭竊盜案(測試員警)"
    assert safe_document_stem(case) == "1151010測試代號遭竊盜案(測試員警)"


def test_saved_case_name_does_not_merge_competing_offenses():
    case = completed_case()
    case["selected_offenses"] = ["theft", "embezzlement"]

    assert "竊盜、侵占" not in case_display_name(case)
    assert "待侵占" in case_display_name(case)


def test_saved_case_name_falls_back_to_saved_victim_profile():
    case = completed_case()
    case["intake"]["victim_identifier"] = ""
    case["profiles"]["victim:default"] = {"name": "林雅婷"}

    assert case_display_name(case) == "1151010林雅婷遭竊盜案(測試員警)"


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


def test_brief_header_uses_station_name_without_location_prefix():
    case = completed_case()
    case["intake"]["station"] = "臺北市中正區虛擬派出所"

    text = brief_text(case, "victim")

    assert text.startswith("虛擬派出所報告\n")
    assert not text.startswith("臺北市中正區虛擬派出所報告")


def test_brief_header_uses_jurisdiction_when_station_is_placeholder():
    case = completed_case()
    case["intake"]["station"] = "○○所"
    case["output_context"]["jurisdiction"] = "臺北市中正區虛擬派出所"

    text = brief_text(case, "victim")

    assert text.startswith("虛擬派出所報告\n")


def test_empty_brief_template_keeps_current_default_content():
    case = completed_case()

    text = brief_text(case, "victim")

    assert "一、受理案由：測試代號遭竊盜案(受理)" in text
    assert "一、受理案由：1151010" not in text
    assert "五、案情摘要：" in text
    assert "六、後續處置：" in text


def test_brief_reason_uses_subject_offense_officer_without_saved_case_date():
    case = completed_case()
    case["selected_offenses"] = ["theft", "embezzlement"]

    text = brief_text(case, "victim")

    assert "一、受理案由：測試代號遭待侵占案(受理)" in text
    assert "一、受理案由：1151010" not in text
