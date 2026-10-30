"""Tests for evaluation metrics."""

from app.evaluation_metrics import (
    candidate_recall,
    element_coverage,
    forbidden_conclusion_rate,
    question_fact_coverage,
    question_traceability_rate,
    run_evaluation,
)


def test_candidate_recall_full():
    r = candidate_recall(["theft", "fraud"], ["theft", "fraud", "injury"])
    assert r.value == 1.0
    assert r.passed is True


def test_candidate_recall_partial():
    r = candidate_recall(["theft", "fraud"], ["theft"])
    assert r.value == 0.5
    assert r.passed is False


def test_forbidden_conclusion_rate_clean():
    r = forbidden_conclusion_rate(["被告於某日涉嫌竊取財物"])
    assert r.value == 0.0
    assert r.passed is True


def test_forbidden_conclusion_rate_violation():
    r = forbidden_conclusion_rate(["被告自白犯罪成立"])
    assert r.value == 1.0
    assert r.passed is False


def test_element_coverage_full():
    cands = [{"elements": [{"pending_facts": ["f1"]}]}]
    r = element_coverage(cands)
    assert r.value == 1.0


def test_question_fact_coverage_full():
    r = question_fact_coverage(["k1"], [{"target_fact": "k1"}])
    assert r.value == 1.0


def test_question_traceability_rate_full():
    qs = [{"target_fact": "f1", "element_ref": "e1", "candidate_ref": "theft"}]
    r = question_traceability_rate(qs)
    assert r.value == 1.0


def test_run_evaluation():
    results = run_evaluation(
        expected_candidates=["theft"],
        actual_candidates=["theft"],
        outputs=["clean text"],
        candidates_with_elements=[{"elements": [{"pending_facts": ["f1"]}]}],
        unknown_keys=["k1"],
        questions=[{"target_fact": "k1", "element_ref": "e1", "candidate_ref": "theft"}],
    )
    assert len(results) == 5
    assert all(r.passed for r in results)