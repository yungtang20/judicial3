"""Integration checks: ties together all expert-strategy modules for use in workflow.

Provides a single entry point for running all safety checks before a document
is generated or a case state transitions.  Fail-closed: any BLOCK-severity
issue prevents the action.
"""

from __future__ import annotations

from typing import Any

from .abductive_reasoning import generate_hypotheses
from .candidate_completeness import check_alternative_preservation, check_candidate_completeness
from .confession_checklist import ConfessionChecklist
from .dispute_issue_identifier import identify_dispute_issues
from .document_format_validator import validate_document, has_blocking_failure
from .fact_states import ManagedFact, check_admission_corroboration, find_denial_contradictions
from .forbidden_conclusions import scan_forbidden_conclusions
from .question_traceability import check_question_traceability, check_unknown_coverage
from .quality_gate import run_quality_gate


def run_pre_document_checks(case: dict[str, Any], kind: str = "brief") -> list[dict[str, Any]]:
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
    managed_facts = []
    if isinstance(facts, dict):
        for key, val in facts.items():
            if isinstance(val, dict) and val.get("state") == "ADMITTED":
                managed_facts.append({"fact_key": key, "state": "ADMITTED",
                                      "corroborating_evidence": val.get("corroborating_evidence", []),
                                      "source_refs": val.get("source_refs", [])})
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

    # 5. Document format (only check required fields for brief documents)
    required_fields = ["jurisdiction", "officer"] if kind == "brief" else []
    checks = validate_document(case, brief_text=case.get("brief_text", ""),
                               page_count=case.get("page_count"),
                               required_fields=required_fields)
    for c in checks:
        if not c.passed:
            issues.append({"source": "document_format", "severity": c.severity,
                           "description": c.message})

    return issues


def _fact_records(facts: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Normalize facts into quality_gate-compatible dicts (defensive)."""
    if not facts:
        return []
    out: list[dict[str, Any]] = []
    for f in facts:
        if not isinstance(f, dict):
            continue
        out.append({
            "fact_key": str(f.get("fact_key") or f.get("id") or ""),
            "element_ref": f.get("element_ref", ""),
            "source_ref": f.get("source_ref", ""),
            "source_excerpt": f.get("source_excerpt", ""),
            "value": str(f.get("value") or f.get("fact_key") or ""),
        })
    return out


def run_pre_analysis_checks(
    candidates: list[dict[str, Any]],
    alternative_ids: list[str] | None = None,
    questions: list[dict[str, Any]] | None = None,
    unknown_keys: list[str] | None = None,
    facts: list[dict[str, Any]] | None = None,
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

    # 5. Legal-Skills-Chinese reasoning assist (non-blocking, WARN only).
    #    quality_gate: every required element must be covered by traceable facts.
    #    dispute_issues: contested/denied facts surface as review focus.
    #    abductive: generate hypotheses for unknown facts to guide questioning.
    if facts is not None:
        norm_facts = _fact_records(facts)

        # quality gate over candidate elements
        elements: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for cand in candidates:
            if not isinstance(cand, dict):
                continue
            for el in cand.get("elements", []):
                if not isinstance(el, dict):
                    continue
                eid = str(el.get("element_id") or el.get("id") or "")
                if not eid or eid in seen_ids:
                    continue
                seen_ids.add(eid)
                elements.append({"element_id": eid, "required": bool(el.get("required"))})
        if elements:
            qres = run_quality_gate(elements, norm_facts)
            if not qres.passed:
                for missing in qres.missing_elements:
                    issues.append({"source": "quality_gate", "severity": "WARN",
                                   "description": f"構成要件 '{missing}' 缺少對應事實（需人工補證）"})
                for untraceable in qres.untraceable_facts:
                    issues.append({"source": "quality_gate", "severity": "WARN",
                                   "description": f"事實 '{untraceable}' 缺少來源追溯（證據鏈未完整）"})

        # disputes from contested facts
        parties = ["suspect", "victim"]
        for di in identify_dispute_issues(norm_facts, parties):
            sev = "WARN" if di.priority == "HIGH" else "INFO"
            issues.append({"source": "dispute_issues", "severity": sev,
                           "description": di.description,
                           "issue_type": di.issue_type, "priority": di.priority})

        # abductive hypotheses for unknown facts (assistive only)
        if unknown_keys:
            known_values = [fr["value"] for fr in norm_facts if fr["value"]]
            for uk in unknown_keys[:5]:
                hyp = generate_hypotheses(uk, known_values)
                issues.append({"source": "abductive_reasoning", "severity": "INFO",
                               "description": f"未知事實 '{uk}' 的推論假說：{hyp.best_hypothesis}",
                               "unknown_fact": uk,
                               "hypotheses": hyp.hypotheses})

    return issues


def has_blocking_issues(issues: list[dict[str, Any]]) -> bool:
    return any(i.get("severity") == "BLOCK" for i in issues)
