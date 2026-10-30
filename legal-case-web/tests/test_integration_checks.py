"""Tests for integration checks."""

from app.integration_checks import (
    run_pre_document_checks,
    run_pre_analysis_checks,
    has_blocking_issues,
)


def test_pre_document_checks_clean():
    case = {"summary": "被告於某日涉嫌竊取財物", "facts": {}, "jurisdiction": "台北", "officer": "王"}
    issues = run_pre_document_checks(case)
    # Should have no BLOCK issues for clean case
    blocking = [i for i in issues if i.get("severity") == "BLOCK"]
    assert len(blocking) == 0


def test_pre_document_checks_forbidden():
    case = {"summary": "被告自白犯罪成立", "facts": {}, "jurisdiction": "台北", "officer": "王"}
    issues = run_pre_document_checks(case)
    assert has_blocking_issues(issues)


def test_pre_analysis_checks_complete():
    candidates = [{"offense_id": "theft", "elements": [{"pending_facts": [{"fact_id": "f1", "questions": ["q1"]}]}]}]
    questions = [{"question_id": "q1", "target_fact": "f1", "element_ref": "e1", "candidate_ref": "theft"}]
    issues = run_pre_analysis_checks(candidates, questions=questions, unknown_keys=[])
    blocking = [i for i in issues if i.get("severity") == "BLOCK"]
    assert len(blocking) == 0


def test_pre_analysis_checks_missing_alternative():
    candidates = [{"offense_id": "theft"}]
    issues = run_pre_analysis_checks(candidates, alternative_ids=["embezzlement"])
    assert any(i["source"] == "alternative_preservation" for i in issues)


def test_has_blocking_issues():
    assert has_blocking_issues([{"severity": "BLOCK"}]) is True
    assert has_blocking_issues([{"severity": "WARN"}]) is False
    assert has_blocking_issues([]) is False