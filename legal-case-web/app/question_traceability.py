"""Question-to-fact traceability checker (blueprint Phase 6).

Every question must be traceable:
  Question → Pending Fact → Constitutive Element → Candidate Direction → Fact/Evidence

This module validates that every generated question has the required traceability
links and that no orphan questions exist.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TraceabilityGap:
    question_id: str
    gap_type: str
    description: str
    severity: str = "WARN"


def check_question_traceability(questions: list[dict[str, Any]]) -> list[TraceabilityGap]:
    """Check each question for required traceability links."""
    gaps: list[TraceabilityGap] = []

    for q in questions:
        qid = q.get("question_id", q.get("id", "unknown"))
        # Every question must link to a pending fact
        if not q.get("target_fact") and not q.get("fact_ref"):
            gaps.append(TraceabilityGap(
                question_id=qid,
                gap_type="NO_FACT_LINK",
                description=f"問句 '{qid}' 缺少待證事項連結",
            ))
        # Every question must link to an element
        if not q.get("element_ref") and not q.get("element_id"):
            gaps.append(TraceabilityGap(
                question_id=qid,
                gap_type="NO_ELEMENT_LINK",
                description=f"問句 '{qid}' 缺少構成要件連結",
                severity="WARN",
            ))
        # Every question must link to a candidate
        if not q.get("candidate_ref") and not q.get("offense_id"):
            gaps.append(TraceabilityGap(
                question_id=qid,
                gap_type="NO_CANDIDATE_LINK",
                description=f"問句 '{qid}' 缺少候選方向連結",
                severity="WARN",
            ))

    return gaps


def check_unknown_coverage(
    unknown_fact_keys: list[str],
    questions: list[dict[str, Any]],
) -> list[TraceabilityGap]:
    """Check that all UNKNOWN facts are covered by at least one question."""
    gaps: list[TraceabilityGap] = []
    covered_keys = set()
    for q in questions:
        target = q.get("target_fact") or q.get("fact_ref")
        if target:
            covered_keys.add(target)

    for key in unknown_fact_keys:
        if key not in covered_keys:
            gaps.append(TraceabilityGap(
                question_id="",
                gap_type="UNKNOWN_UNCOVERED",
                description=f"未知事項 '{key}' 未被任何問句覆蓋",
                severity="BLOCK",
            ))
    return gaps


def summarize_traceability(gaps: list[TraceabilityGap]) -> str:
    if not gaps:
        return "問句追溯性檢查通過"
    lines = [f"[{g.severity}] {g.description}" for g in gaps]
    return "\n".join(lines)