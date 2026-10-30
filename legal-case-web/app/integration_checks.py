"""Integration checks: ties together all expert-strategy modules for use in workflow.

Provides a single entry point for running all safety checks before a document
is generated or a case state transitions.  Fail-closed: any BLOCK-severity
issue prevents the action.
"""

from __future__ import annotations

from typing import Any

from .forbidden_conclusions import scan_forbidden_conclusions
from .fact_states import check_admission_corroboration, find_denial_contradictions
from .confession_checklist import ConfessionChecklist
from .candidate_completeness import check_candidate_completeness, has_blocking_gaps
from .question_traceability import check_question_traceability, check_unknown_coverage
from .document_format_validator import validate_document, has_blocking_failure


def run_pre_document_checks(case: dict[str, Any]) -> list[dict[str, Any]]:
    """Run all safety checks before document generation.

    Returns list of issues (empty = all OK).  Any BLOCK-severity issue
    should prevent document generation.
    """
    issues: list[dict[str, Any]] = []

    # 1. Forbidden conclusions in summary/facts
    summary = str(case.get("summary", ""))
    facts = case.get("facts", {})
    fact_text = " ".join(str(v) for v in (facts.values() if isinstance(facts, dict) else []))
    combined = f"{summary} {fact_text}"
    violations = scan_forbidden_conclusions(combined)
    for v in violations:
        issues.append({"source": "forbidden_conclusions", "severity": v["severity"],
                       "description": v["description"]})

    # 2. Admission corroboration
    # Convert case facts to ManagedFact-like dicts for checking
    managed_facts = []
    if isinstance(facts, dict):
        for key, val in facts.items():
            if isinstance(val, dict) and val.get("state") == "ADMITTED":
                managed_facts.append({"fact_key": key, "state": "ADMITTED",
                                     "corroborating_evidence": val.get("corroborating_evidence", []),
                                     "source_refs": val.get("source_refs", [])})
    from .fact_states import ManagedFact
    mf_list = [ManagedFact.from_dict(f) for f in managed_facts]
    for issue in check_admission_corroboration(mf_list):
        issues.append({"source": "admission_corroboration", "severity": "BLOCK", **issue})

    # 3. Denial contradictions
    mf_list2 = []
    if isinstance(facts, dict):
        for key, val in facts.items():
            if isinstance(val, dict) and val.get("state") == "DENIED":
                mf_list2.append({"fact_key": key, "state": "DENIED",
                                 "source_refs": val.get("source_refs", [])})
    mf_list2 = [ManagedFact.from_dict(f) for f in mf_list2]
    for issue in find_denial_contradictions(mf_list2):
        issues.append({"source": "denial_contradiction", "severity": "WARN", **issue})

    # 4. Confession checklist
    checklist_data = case.get("confession_checklist")
    if checklist_data:
        cl = ConfessionChecklist.from_dict(checklist_data)
        if not cl.is_complete():
            issues.append({"source": "confession_checklist", "severity": "BLOCK",
                           "description": f"自白補強清單未完成：{', '.join(cl.missing_labels())}"})

    # 5. Document format
    checks = validate_document(case, brief_text=case.get("brief_text", ""),
                               page_count=case.get("page_count"))
    for c in checks:
        if not c.passed:
            issues.append({"source": "document_format", "severity": c.severity,
                           "description": c.message})

    return issues


def run_pre_analysis_checks(
    candidates: list[dict[str, Any]],
    alternative_ids: list[str] | None = None,
    questions: list[dict[str, Any]] | None = None,
    unknown_keys: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Run all safety checks before analysis output."""
    issues: list[dict[str, Any]] = []

    # 1. Candidate completeness
    gaps = check_candidate_completeness(candidates)
    for g in gaps:
        issues.append({"source": "candidate_completeness", "severity": g.severity,
                       "description": g.description})

    # 2. Alternative preservation
    if alternative_ids:
        alt_gaps = check_candidate_completeness([])  # placeholder
        from .candidate_completeness import check_alternative_preservation
        alt_gaps = check_alternative_preservation(candidates, alternative_ids)
        for g in alt_gaps:
            issues.append({"source": "alternative_preservation", "severity": g.severity,
                           "description": g.description})

    # 3. Question traceability
    if questions:
        q_gaps = check_question_traceability(questions)
        for g in q_gaps:
            issues.append({"source": "question_traceability", "severity": g.severity,
                           "description": g.description})

    # 4. Unknown coverage
    if unknown_keys and questions:
        u_gaps = check_unknown_coverage(unknown_keys, questions)
        for g in u_gaps:
            issues.append({"source": "unknown_coverage", "severity": g.severity,
                           "description": g.description})

    return issues


def has_blocking_issues(issues: list[dict[str, Any]]) -> bool:
    return any(i.get("severity") == "BLOCK" for i in issues)