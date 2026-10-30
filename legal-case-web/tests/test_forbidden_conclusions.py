"""Tests for forbidden conclusion scanner."""

from app.forbidden_conclusions import (
    assert_no_forbidden_conclusions,
    has_blocking_violation,
    scan_forbidden_conclusions,
)


def test_clean_text_no_violations():
    text = "被告於民國113年1月1日，在台北市某處，涉嫌竊取被害人財物。"
    assert scan_forbidden_conclusions(text) == []


def test_auto_convict_self_confession():
    text = "被告自白犯罪成立，應予起訴。"
    violations = scan_forbidden_conclusions(text)
    assert len(violations) > 0
    assert any(v["category"] == "AUTO_CONVICT" for v in violations)


def test_keyword_to_crime():
    text = "被告竊取財物，構成竊盜罪。"
    violations = scan_forbidden_conclusions(text)
    assert len(violations) > 0
    assert any(v["category"] == "KEYWORD_TO_CRIME" for v in violations)


def test_denial_equals_exclusion():
    text = "被告否認，排除犯罪可能。"
    violations = scan_forbidden_conclusions(text)
    assert len(violations) > 0
    assert any(v["category"] == "DENIAL_EQUALS_EXCLUSION" for v in violations)


def test_confession_without_corroboration():
    text = "自白即可認定犯罪，直接移送。"
    violations = scan_forbidden_conclusions(text)
    assert len(violations) > 0
    assert any(v["category"] == "CONFESSION_WITHOUT_CORROBORATION" for v in violations)


def test_has_blocking_violation_true():
    assert has_blocking_violation("被告自白犯罪成立") is True


def test_has_blocking_violation_false():
    assert has_blocking_violation("被告於某日涉嫌竊取財物，尚待調查。") is False


def test_assert_no_forbidden_conclusions_raises():
    import pytest
    with pytest.raises(ValueError, match="FORBIDDEN_CONCLUSION"):
        assert_no_forbidden_conclusions("被告自白犯罪成立")


def test_assert_no_forbidden_conclusions_ok():
    assert_no_forbidden_conclusions("被告於某日涉嫌竊取財物，尚待調查。")