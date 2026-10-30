"""Tests for quality gate."""

from app.quality_gate import run_quality_gate


def test_quality_gate_pass():
    elements = [{"element_id": "e1"}, {"element_id": "e2"}]
    facts = [
        {"fact_key": "f1", "element_ref": "e1", "source_ref": "s1"},
        {"fact_key": "f2", "element_ref": "e2", "source_ref": "s2"},
    ]
    result = run_quality_gate(elements, facts)
    assert result.passed is True


def test_quality_gate_missing_element():
    elements = [{"element_id": "e1"}, {"element_id": "e2"}]
    facts = [{"fact_key": "f1", "element_ref": "e1", "source_ref": "s1"}]
    result = run_quality_gate(elements, facts)
    assert result.passed is False
    assert "e2" in result.missing_elements


def test_quality_gate_untraceable_fact():
    elements = [{"element_id": "e1"}]
    facts = [{"fact_key": "f1", "element_ref": "e1"}]
    result = run_quality_gate(elements, facts)
    assert result.passed is False
    assert "f1" in result.untraceable_facts


def test_quality_gate_empty_elements():
    result = run_quality_gate([], [])
    assert result.passed is False