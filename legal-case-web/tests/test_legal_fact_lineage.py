from __future__ import annotations

from tools.legal_fact_lineage import run_lineage


def test_same_summary_single_fact_changes_are_traced_without_candidate_change() -> None:
    trace = run_lineage(write_trace=False)
    for name in ("A", "B"):
        scenario = trace["scenarios"][name]
        assert scenario["summary_unchanged"] is True
        assert scenario["new_fact_id"] in {
            fact["fact_id"] for fact in scenario["changed_facts"]["candidate_call"]["gate1"]["facts"]
        }
        assert scenario["comparison"]["status"] == "UNCHANGED"


def test_candidate_receives_typed_unknown_from_formal_gate1_without_probe() -> None:
    trace = run_lineage(write_trace=False)
    probe = trace["typed_fact_probe"]
    assert probe["comparison"]["status"] == "UNCHANGED"
    assert "intent" in probe["baseline"]["candidate_output"][0]["unknown_fact_keys"]
    assert probe["keyed_unknown"]["candidate_output"][0]["unknown_fact_keys"] == probe["baseline"]["candidate_output"][0]["unknown_fact_keys"]


def test_lineage_does_not_use_external_services() -> None:
    trace = run_lineage(write_trace=False)
    assert trace["external_dependencies"] == {
        "llm": "NOT_USED",
        "database": "NOT_USED",
        "http": "NOT_USED",
        "frontend": "NOT_USED",
    }
