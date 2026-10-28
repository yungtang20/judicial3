from __future__ import annotations

from tools.legal_fact_candidate_shadow import run_shadow


def test_shadow_replay_is_deterministic_and_offline() -> None:
    first = run_shadow(write_trace=False)
    second = run_shadow(write_trace=False)
    assert first == second
    for scenario in first["scenarios"].values():
        assert scenario["current_facts"]["formal_runtime_calls"] == {
            "llm": "NOT_USED", "database": "NOT_USED", "http": "NOT_USED"
        }


def test_shadow_adapter_preserves_unknown_facts() -> None:
    trace = run_shadow(write_trace=False)
    for scenario in trace["scenarios"].values():
        facts = scenario["standardized_facts"]["facts"]
        unknown = [fact for fact in facts if fact.get("assertion_class") == "UNKNOWN"]
        assert unknown
        assert all(fact.get("object") == "UNKNOWN" for fact in unknown)


def test_counterfactual_facts_are_retained_in_trace() -> None:
    trace = run_shadow(write_trace=False)
    facts_a = trace["scenarios"]["A"]["standardized_facts"]["facts"]
    facts_b = trace["scenarios"]["B"]["standardized_facts"]["facts"]
    assert any(fact["fact_id"] == "fact:shadow-a-possession" for fact in facts_a)
    assert any(fact["fact_id"] == "fact:shadow-b-lost" for fact in facts_b)
