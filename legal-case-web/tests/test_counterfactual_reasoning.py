"""Tests for counterfactual reasoning."""

from app.counterfactual_reasoning import (
    evaluate_counterfactual,
    assess_causal_chain,
)


def test_causal_link_exists():
    scenario = evaluate_counterfactual(
        "fact_a", "value_a",
        dependent_outcomes=["outcome1"],
        independent_outcomes=["outcome2"],
    )
    assert scenario.causal_link is True
    assert "outcome1" in scenario.original_outcome


def test_no_causal_link():
    scenario = evaluate_counterfactual(
        "fact_b", "value_b",
        dependent_outcomes=[],
        independent_outcomes=["outcome1"],
    )
    assert scenario.causal_link is False


def test_assess_causal_chain():
    facts = [{"fact_key": "f1", "value": "v1", "dependent_outcomes": ["o1"]}]
    scenarios = assess_causal_chain(facts, "o1")
    assert len(scenarios) == 1
    assert scenarios[0].causal_link is True