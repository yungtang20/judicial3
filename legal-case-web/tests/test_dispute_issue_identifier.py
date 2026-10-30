"""Tests for dispute issue identifier."""

from app.dispute_issue_identifier import (
    identify_dispute_issues,
    summarize_disputes,
)


def test_denied_fact_creates_dispute():
    facts = [{"fact_key": "f1", "status": "DENIED"}]
    issues = identify_dispute_issues(facts)
    assert len(issues) >= 1
    assert any(i.issue_type == "contested_fact" for i in issues)


def test_disputed_fact_creates_dispute():
    facts = [{"fact_key": "f2", "status": "DISPUTED"}]
    issues = identify_dispute_issues(facts)
    assert any(i.issue_type == "contested_fact" for i in issues)


def test_admitted_fact_uncontested():
    facts = [{"fact_key": "f3", "status": "ADMITTED"}]
    issues = identify_dispute_issues(facts)
    assert any(i.issue_type == "legal_question" for i in issues)


def test_summarize_disputes():
    facts = [{"fact_key": "f1", "status": "DENIED"}]
    issues = identify_dispute_issues(facts)
    summary = summarize_disputes(issues)
    assert "高優先爭議" in summary or "無爭議焦點" in summary