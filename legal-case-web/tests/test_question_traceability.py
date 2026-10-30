"""Tests for question traceability checker."""

from app.question_traceability import (
    check_question_traceability,
    check_unknown_coverage,
    summarize_traceability,
)


def test_fully_traceable_question():
    questions = [
        {"question_id": "q1", "target_fact": "f1", "element_ref": "e1", "candidate_ref": "theft"},
    ]
    gaps = check_question_traceability(questions)
    assert gaps == []


def test_missing_fact_link():
    questions = [
        {"question_id": "q1", "element_ref": "e1", "candidate_ref": "theft"},
    ]
    gaps = check_question_traceability(questions)
    assert any(g.gap_type == "NO_FACT_LINK" for g in gaps)


def test_unknown_coverage_complete():
    questions = [{"question_id": "q1", "target_fact": "unknown_time"}]
    gaps = check_unknown_coverage(["unknown_time"], questions)
    assert gaps == []


def test_unknown_uncovered():
    questions = [{"question_id": "q1", "target_fact": "other_fact"}]
    gaps = check_unknown_coverage(["unknown_time"], questions)
    assert len(gaps) == 1
    assert gaps[0].gap_type == "UNKNOWN_UNCOVERED"


def test_summarize_no_gaps():
    assert summarize_traceability([]) == "問句追溯性檢查通過"