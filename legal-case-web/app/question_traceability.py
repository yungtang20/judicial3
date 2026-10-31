"""Question-to-fact bidirectional traceability (blueprint Phase 6 + stage2).

Chain:
  Legal candidate → Element → Pending fact → Evidence → Gap → Question → Answer → Re-eval

Every question should know why it exists and what it affects downstream.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TraceabilityGap:
    question_id: str
    gap_type: str
    description: str
    severity: str = "WARN"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QuestionTrace:
    """Full forward links for one question."""

    question_id: str
    target_fact: str = ""
    element_id: str = ""
    candidate_ref: str = ""
    hypothesis_ids: list[str] = field(default_factory=list)
    existing_evidence_ids: list[str] = field(default_factory=list)
    evidence_gap: str = ""
    discriminates_hypotheses: list[str] = field(default_factory=list)
    downstream_effects: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_trace_from_question(q: dict[str, Any]) -> QuestionTrace:
    qid = str(q.get("question_id") or q.get("id") or "unknown")
    return QuestionTrace(
        question_id=qid,
        target_fact=str(q.get("target_fact") or q.get("fact_ref") or ""),
        element_id=str(q.get("element_ref") or q.get("element_id") or ""),
        candidate_ref=str(q.get("candidate_ref") or q.get("offense_id") or ""),
        hypothesis_ids=list(q.get("hypothesis_ids") or []),
        existing_evidence_ids=list(q.get("existing_evidence_ids") or []),
        evidence_gap=str(q.get("evidence_gap") or ""),
        discriminates_hypotheses=list(
            q.get("discriminates_hypotheses") or q.get("hypothesis_ids") or []
        ),
        downstream_effects=list(q.get("downstream_effects") or []),
    )


def check_question_traceability(questions: list[dict[str, Any]]) -> list[TraceabilityGap]:
    """Check each question for required traceability links."""
    gaps: list[TraceabilityGap] = []

    for q in questions:
        qid = q.get("question_id", q.get("id", "unknown"))
        if not q.get("target_fact") and not q.get("fact_ref"):
            gaps.append(
                TraceabilityGap(
                    question_id=str(qid),
                    gap_type="NO_FACT_LINK",
                    description=f"問句 '{qid}' 缺少待證事項連結",
                )
            )
        if not q.get("element_ref") and not q.get("element_id"):
            gaps.append(
                TraceabilityGap(
                    question_id=str(qid),
                    gap_type="NO_ELEMENT_LINK",
                    description=f"問句 '{qid}' 缺少構成要件連結",
                    severity="WARN",
                )
            )
        if not q.get("candidate_ref") and not q.get("offense_id"):
            gaps.append(
                TraceabilityGap(
                    question_id=str(qid),
                    gap_type="NO_CANDIDATE_LINK",
                    description=f"問句 '{qid}' 缺少候選方向連結",
                    severity="WARN",
                )
            )
        # Stage2: prefer explicit hypothesis discrimination when multi-hypothesis active
        if q.get("multi_hypothesis_mode") and not (
            q.get("hypothesis_ids") or q.get("discriminates_hypotheses")
        ):
            gaps.append(
                TraceabilityGap(
                    question_id=str(qid),
                    gap_type="NO_HYPOTHESIS_LINK",
                    description=f"問句 '{qid}' 在多假設模式下缺少競爭假設連結",
                    severity="WARN",
                )
            )

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
            gaps.append(
                TraceabilityGap(
                    question_id="",
                    gap_type="UNKNOWN_UNCOVERED",
                    description=f"未知事項 '{key}' 未被任何問句覆蓋",
                    severity="BLOCK",
                )
            )
    return gaps


def check_orphan_questions_against_facts(
    questions: list[dict[str, Any]],
    known_fact_keys: set[str] | list[str],
) -> list[TraceabilityGap]:
    """Flag questions whose target_fact is not in the case fact set (irrelevant)."""
    known = set(known_fact_keys)
    gaps: list[TraceabilityGap] = []
    if not known:
        return gaps
    for q in questions:
        qid = str(q.get("question_id") or q.get("id") or "unknown")
        target = q.get("target_fact") or q.get("fact_ref")
        if target and target not in known and not str(target).startswith("explore_"):
            gaps.append(
                TraceabilityGap(
                    question_id=qid,
                    gap_type="ORPHAN_FACT_TARGET",
                    description=f"問句 '{qid}' 指向未登錄事實鍵 '{target}'",
                    severity="WARN",
                )
            )
    return gaps


def summarize_traceability(gaps: list[TraceabilityGap]) -> str:
    if not gaps:
        return "問句追溯性檢查通過"
    lines = [f"[{g.severity}] {g.description}" for g in gaps]
    return "\n".join(lines)
