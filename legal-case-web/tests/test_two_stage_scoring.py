"""Tests for two-stage scoring."""

from app.two_stage_scoring import (
    smart_truncate,
    should_proceed_to_full_pass,
    two_stage_summary,
    SCREENING_BUDGET,
    FULL_PASS_BUDGET,
)


def test_smart_truncate_short_text():
    text = "short text"
    result, truncated = smart_truncate(text, 100)
    assert result == text
    assert truncated is False


def test_smart_truncate_long_text():
    text = "a" * 5000
    result, truncated = smart_truncate(text, 1000)
    assert truncated is True
    assert len(result) <= 1000


def test_smart_truncate_with_keywords():
    text = "prefix " + "KEYWORD" + " suffix " * 100
    result, truncated = smart_truncate(text, 200, keywords=["KEYWORD"])
    assert "KEYWORD" in result
    assert truncated is True


def test_should_proceed():
    assert should_proceed_to_full_pass(5) is True
    assert should_proceed_to_full_pass(0) is False


def test_two_stage_summary():
    summary = two_stage_summary(100, 30)
    assert summary["total"] == 100
    assert summary["screening_passed"] == 30
    assert summary["full_pass_skipped"] == 70
    assert summary["savings_pct"] == 70.0


def test_budgets():
    assert SCREENING_BUDGET == 3000
    assert FULL_PASS_BUDGET == 12000