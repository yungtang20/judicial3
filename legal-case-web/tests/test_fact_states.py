"""Tests for fact state machine."""

from app.fact_states import (
    FactState,
    ManagedFact,
    check_admission_corroboration,
    find_denial_contradictions,
)


def test_valid_transition_asserted_to_denied():
    f = ManagedFact(fact_key="k1", value="v", state=FactState.ASSERTED)
    assert f.transition_to(FactState.DENIED, "suspect denied") is True
    assert f.state == FactState.DENIED


def test_denial_can_transition_to_admitted():
    f = ManagedFact(fact_key="k1", value="v", state=FactState.DENIED)
    assert f.transition_to(FactState.ADMITTED, "suspect later admitted") is True


def test_transition_history_recorded():
    f = ManagedFact(fact_key="k1", value="v", state=FactState.ASSERTED)
    f.transition_to(FactState.DENIED, "denied")
    assert len(f.transitions) == 1
    assert f.transitions[0].from_state == "ASSERTED"
    assert f.transitions[0].to_state == "DENIED"


def test_admission_without_corroboration_detected():
    f = ManagedFact(fact_key="k1", value="v", state=FactState.ADMITTED)
    issues = check_admission_corroboration([f])
    assert len(issues) == 1
    assert issues[0]["issue"] == "ADMISSION_WITHOUT_CORROBORATION"


def test_admission_with_corroboration_ok():
    f = ManagedFact(fact_key="k1", value="v", state=FactState.ADMITTED, corroborating_evidence=["ev1"])
    issues = check_admission_corroboration([f])
    assert len(issues) == 0


def test_denial_with_evidence_contradiction():
    f = ManagedFact(fact_key="k1", value="v", state=FactState.DENIED, source_refs=["ev1"])
    contradictions = find_denial_contradictions([f])
    assert len(contradictions) == 1
    assert contradictions[0]["issue"] == "DENIAL_WITH_EVIDENCE"


def test_denial_without_evidence_no_contradiction():
    f = ManagedFact(fact_key="k1", value="v", state=FactState.DENIED)
    contradictions = find_denial_contradictions([f])
    assert len(contradictions) == 0


def test_roundtrip_serialization():
    f = ManagedFact(fact_key="k1", value="v", state=FactState.ASSERTED, source_refs=["s1"])
    f.transition_to(FactState.DENIED, "denied")
    d = f.to_dict()
    f2 = ManagedFact.from_dict(d)
    assert f2.state == FactState.DENIED
    assert len(f2.transitions) == 1