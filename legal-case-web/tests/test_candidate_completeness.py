"""Tests for candidate offense completeness checker."""

from app.candidate_completeness import (
    check_alternative_preservation,
    check_candidate_completeness,
    has_blocking_gaps,
    summarize_gaps,
)


def test_complete_candidate():
    candidates = [
        {"offense_id": "theft", "elements": [
            {"element_id": "e1", "pending_facts": [
                {"fact_id": "f1", "questions": ["q1"]},
            ]},
        ]},
    ]
    gaps = check_candidate_completeness(candidates)
    assert gaps == []


def test_no_candidates():
    gaps = check_candidate_completeness([])
    assert len(gaps) == 1
    assert gaps[0].gap_type == "NO_CANDIDATES"


def test_missing_elements():
    candidates = [{"offense_id": "theft", "elements": []}]
    gaps = check_candidate_completeness(candidates)
    assert any(g.gap_type == "NO_ELEMENTS" for g in gaps)


def test_missing_pending_facts():
    candidates = [{"offense_id": "theft", "elements": [{"element_id": "e1", "pending_facts": []}]}]
    gaps = check_candidate_completeness(candidates)
    assert any(g.gap_type == "NO_PENDING_FACTS" for g in gaps)


def test_alternative_preservation():
    candidates = [{"offense_id": "theft"}]
    gaps = check_alternative_preservation(candidates, alternative_ids=["embezzlement"])
    assert len(gaps) == 1
    assert gaps[0].gap_type == "ALTERNATIVE_DROPPED"


def test_alternative_preserved():
    candidates = [{"offense_id": "theft"}, {"offense_id": "embezzlement"}]
    gaps = check_alternative_preservation(candidates, alternative_ids=["embezzlement"])
    assert gaps == []


def test_has_blocking_gaps():
    gaps = check_candidate_completeness([])
    # NO_CANDIDATES is WARN, not BLOCK
    assert has_blocking_gaps(gaps) is False


def test_summarize_no_gaps():
    assert summarize_gaps([]) == "候選完整性檢查通過"