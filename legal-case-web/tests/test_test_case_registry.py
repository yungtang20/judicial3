"""Tests for test case registry."""

from app.test_case_registry import (
    STANDARD_SCENARIOS,
    get_scenario,
    get_scenarios_by_type,
    all_scenario_ids,
)


def test_standard_scenarios_count():
    assert len(STANDARD_SCENARIOS) >= 10


def test_get_scenario_exists():
    tc = get_scenario("TC-001")
    assert tc is not None
    assert tc.scenario_type == "SINGLE_CRIME"


def test_get_scenario_not_found():
    assert get_scenario("TC-999") is None


def test_get_scenarios_by_type():
    scenarios = get_scenarios_by_type("DENIAL_CASE")
    assert len(scenarios) == 1
    assert scenarios[0].scenario_id == "TC-003"


def test_all_scenario_ids():
    ids = all_scenario_ids()
    assert "TC-001" in ids
    assert len(ids) == len(STANDARD_SCENARIOS)


def test_scenario_has_forbidden_conclusions():
    tc = get_scenario("TC-001")
    assert len(tc.forbidden_conclusions) > 0


def test_scenario_has_expected_candidates():
    tc = get_scenario("TC-002")
    assert "theft" in tc.expected_candidates
    assert "embezzlement" in tc.expected_candidates


def test_scenario_preserves_alternatives():
    tc = get_scenario("TC-002")
    assert "theft" in tc.must_preserve_alternatives
    assert "embezzlement" in tc.must_preserve_alternatives