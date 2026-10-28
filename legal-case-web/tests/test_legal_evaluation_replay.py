from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import QUESTION_BANK_PATH
from app.rules import analyze_gate1, candidate_offenses, load_bank
from tools.legal_evaluation_replay import (
    FIXTURE_PATH,
    _unknown_metrics,
    candidate_metrics,
    canonical_hash,
    load_fixture,
    run_evaluation,
    validate_source_spans,
)


def test_fixture_is_conditionally_reviewed_independent_gold_with_exact_spans() -> None:
    fixture = load_fixture()
    assert fixture["status"] == "INITIAL_REGRESSION_BASELINE_WITH_CONDITIONS"
    assert fixture["gold_reviewer"] == "PENDING_FORMAL_LEGAL_REVIEW_AFTER_USER_GUIDANCE"
    assert len(fixture["cases"]) == 5
    for case in fixture["cases"]:
        assert validate_source_spans(case) == []
        assert case["gold_facts"]
        assert all(fact["fact_key"] for fact in case["gold_facts"])


@pytest.mark.parametrize(
    ("actual", "gold", "k", "recall", "precision", "hard_fail"),
    [
        ([], {"required": ["theft"], "acceptable": [], "prohibited": []}, 3, 0.0, None, False),
        (["theft"], {"required": ["theft"], "acceptable": [], "prohibited": []}, 1, 1.0, 1.0, False),
        (["embezzlement"], {"required": [], "acceptable": ["embezzlement"], "prohibited": []}, 3, None, 1.0, False),
        (["forgery", "theft"], {"required": ["theft"], "acceptable": [], "prohibited": ["forgery"]}, 1, 0.0, 0.0, True),
    ],
)
def test_candidate_metrics_boundaries(actual, gold, k, recall, precision, hard_fail) -> None:
    result = candidate_metrics(actual, gold, k)
    assert result["recall_at_k"] == recall
    assert result["precision_at_k"] == precision
    assert result["hard_fail"] is hard_fail


def test_wrong_candidate_mutation_fails_without_changing_gold_hash() -> None:
    fixture = load_fixture()
    case = fixture["cases"][0]
    before = canonical_hash(case)
    result = candidate_metrics(["fraud"], case["gold_candidates"], fixture["k"])
    assert result["recall_at_k"] == 0.0
    assert set(result["missing_required"]) == {"theft", "embezzlement"}
    assert canonical_hash(case) == before


def test_source_span_mutation_is_rejected() -> None:
    case = copy.deepcopy(load_fixture()["cases"][0])
    case["gold_facts"][0]["source"]["end"] += 1
    assert {item["code"] for item in validate_source_spans(case)} == {"SOURCE_SPAN_TEXT_MISMATCH"}


def test_unknown_promotion_is_a_hard_failure() -> None:
    gold = [{"fact_id": "u1", "fact_key": "intent", "assertion_class": "UNKNOWN",
             "source": {"start": 0, "end": 4}}]
    runtime = [{"fact_id": "r1", "fact_key": "intent", "machine_status": "FACT", "value": "有意圖",
                "source_start": 0, "source_end": 4}]
    result = _unknown_metrics(gold, runtime)
    assert result["rate"] == 0.0
    assert result["hard_fail"] is True


def test_citation_only_perturbation_does_not_change_candidates() -> None:
    fixture = load_fixture()
    summary = fixture["cases"][0]["raw_summary"]
    bank = load_bank(QUESTION_BANK_PATH)

    def ids(text: str) -> list[str]:
        gate1 = analyze_gate1({"summary": text, "event_time": "", "location": ""}, use_ai=False)
        return [item["id"] for item in candidate_offenses(text, bank, gate1)]

    assert ids(summary) == ids(summary + "本案與刑法第337條無關。")


def test_replay_uses_actual_runtime_and_preserves_target_unknowns() -> None:
    trace = run_evaluation(repetitions=2)
    assert trace["separation_controls"]["gold_facts_passed_to_candidate_runtime"] is False
    assert trace["separation_controls"]["question_lane"] == "independent gold-selected parent/route"
    assert trace["determinism"]["status"] == "PASS"
    assert all(not case["hard_findings"] for case in trace["cases"])
    assert all(case["stages"]["unknown"]["rate"] == 1.0 for case in trace["cases"])
    by_id = {case["case_id"]: case for case in trace["cases"]}
    assert by_id["phone-lost"]["first_divergence_stage"] != "FACT"
    assert by_id["phone-denial-cctv-conflict"]["first_divergence_stage"] != "FACT"
    assert trace["overall"] == "PARTIAL_PASS"


def test_fixture_file_is_not_modified_by_evaluation() -> None:
    before = hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()
    run_evaluation(repetitions=1)
    after = hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()
    assert after == before


def test_fresh_process_semantic_hash_is_stable_across_hash_seeds() -> None:
    hashes = []
    for seed in ("1", "7919"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = seed
        code = (
            "from tools.legal_evaluation_replay import run_evaluation; "
            "print(run_evaluation(repetitions=1)['determinism']['semantic_hashes'][0])"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], cwd=ROOT, env=env,
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
        )
        hashes.append(result.stdout.strip())
    assert len(set(hashes)) == 1
