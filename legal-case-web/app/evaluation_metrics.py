"""Evaluation metrics for integration testing (blueprint Phase 8).

Metrics:
  1. candidate_recall: rate of expected candidates that were actually proposed
  2. forbidden_conclusion_rate: rate of outputs containing forbidden conclusions
  3. element_coverage: rate of constitutive elements with linked pending facts
  4. question_fact_coverage: rate of UNKNOWN facts covered by questions
  5. question_traceability_rate: rate of questions with full traceability links
  6. document_format_pass_rate: rate of documents passing format checks
  7. version_invalidation_accuracy: rate of correct STALE propagation
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class EvaluationResult:
    metric_name: str
    value: float
    threshold: float
    passed: bool
    details: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def candidate_recall(expected: list[str], actual: list[str]) -> EvaluationResult:
    """Rate of expected candidates that were actually proposed."""
    if not expected:
        return EvaluationResult("candidate_recall", 1.0, 0.8, True, "no expected candidates")
    hits = sum(1 for e in expected if e in actual)
    value = hits / len(expected)
    return EvaluationResult(
        "candidate_recall", value, 0.8, value >= 0.8,
        f"{hits}/{len(expected)} expected candidates found",
    )


def forbidden_conclusion_rate(outputs: list[str]) -> EvaluationResult:
    """Rate of outputs containing forbidden conclusions (lower is better)."""
    if not outputs:
        return EvaluationResult("forbidden_conclusion_rate", 0.0, 0.0, True, "no outputs")
    from .forbidden_conclusions import scan_forbidden_conclusions
    violations = sum(1 for o in outputs if scan_forbidden_conclusions(o))
    value = violations / len(outputs)
    return EvaluationResult(
        "forbidden_conclusion_rate", value, 0.0, value == 0.0,
        f"{violations}/{len(outputs)} outputs contain forbidden conclusions",
    )


def element_coverage(candidates: list[dict[str, Any]]) -> EvaluationResult:
    """Rate of constitutive elements with linked pending facts."""
    total_elements = 0
    covered_elements = 0
    for cand in candidates:
        for elem in cand.get("elements", []):
            total_elements += 1
            if elem.get("pending_facts") or elem.get("facts"):
                covered_elements += 1
    if total_elements == 0:
        return EvaluationResult("element_coverage", 0.0, 0.8, False, "no elements")
    value = covered_elements / total_elements
    return EvaluationResult(
        "element_coverage", value, 0.8, value >= 0.8,
        f"{covered_elements}/{total_elements} elements have pending facts",
    )


def question_fact_coverage(unknown_keys: list[str], questions: list[dict[str, Any]]) -> EvaluationResult:
    """Rate of UNKNOWN facts covered by questions."""
    if not unknown_keys:
        return EvaluationResult("question_fact_coverage", 1.0, 0.9, True, "no unknown facts")
    covered = set()
    for q in questions:
        target = q.get("target_fact") or q.get("fact_ref")
        if target:
            covered.add(target)
    hits = sum(1 for k in unknown_keys if k in covered)
    value = hits / len(unknown_keys)
    return EvaluationResult(
        "question_fact_coverage", value, 0.9, value >= 0.9,
        f"{hits}/{len(unknown_keys)} unknown facts covered",
    )


def question_traceability_rate(questions: list[dict[str, Any]]) -> EvaluationResult:
    """Rate of questions with full traceability (fact + element + candidate)."""
    if not questions:
        return EvaluationResult("question_traceability_rate", 1.0, 0.9, True, "no questions")
    full = 0
    for q in questions:
        has_fact = bool(q.get("target_fact") or q.get("fact_ref"))
        has_elem = bool(q.get("element_ref") or q.get("element_id"))
        has_cand = bool(q.get("candidate_ref") or q.get("offense_id"))
        if has_fact and has_elem and has_cand:
            full += 1
    value = full / len(questions)
    return EvaluationResult(
        "question_traceability_rate", value, 0.9, value >= 0.9,
        f"{full}/{len(questions)} questions fully traceable",
    )


def run_evaluation(
    expected_candidates: list[str],
    actual_candidates: list[str],
    outputs: list[str],
    candidates_with_elements: list[dict[str, Any]],
    unknown_keys: list[str],
    questions: list[dict[str, Any]],
) -> list[EvaluationResult]:
    """Run all evaluation metrics and return results."""
    return [
        candidate_recall(expected_candidates, actual_candidates),
        forbidden_conclusion_rate(outputs),
        element_coverage(candidates_with_elements),
        question_fact_coverage(unknown_keys, questions),
        question_traceability_rate(questions),
    ]