"""Tests for abductive reasoning."""

from app.abductive_reasoning import (
    generate_hypotheses,
    Hypothesis,
)


def test_generate_hypotheses():
    result = generate_hypotheses("unknown_fact", ["fact_a", "fact_b"])
    assert len(result.hypotheses) >= 1
    assert result.best_hypothesis != ""


def test_hypothesis_assessment():
    h = Hypothesis(
        hypothesis_id="h1",
        description="test",
        supporting_facts=["f1", "f2"],
        contradicting_facts=[],
    )
    assert h.assess() == "HIGH"


def test_hypothesis_low_plausibility():
    h = Hypothesis(
        hypothesis_id="h2",
        description="test",
        supporting_facts=[],
        contradicting_facts=["f1"],
    )
    assert h.assess() == "LOW"


def test_generate_no_known_facts():
    result = generate_hypotheses("unknown_fact", [])
    assert len(result.hypotheses) >= 1