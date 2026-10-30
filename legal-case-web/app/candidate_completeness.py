"""Candidate offense completeness checker (blueprint Phase 5, §5.1).

Every candidate legal direction must have:
  - At least one constitutive element (構成要件)
  - Each element must have at least one pending fact (待證事項)
  - Each pending fact must have at least one linked question (問句)
  - Alternative directions must be preserved (not silently dropped)

This module validates candidate completeness and returns a list of gaps.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CompletenessGap:
    candidate_id: str
    gap_type: str
    description: str
    severity: str = "BLOCK"  # BLOCK = must fix before proceeding


def check_candidate_completeness(candidates: list[dict[str, Any]]) -> list[CompletenessGap]:
    """Check each candidate for completeness. Returns list of gaps (empty = OK)."""
    gaps: list[CompletenessGap] = []

    if not candidates:
        gaps.append(CompletenessGap(
            candidate_id="",
            gap_type="NO_CANDIDATES",
            description="未提出任何候選犯罪方向",
            severity="WARN",
        ))
        return gaps

    for cand in candidates:
        cid = cand.get("offense_id", cand.get("id", "unknown"))
        elements = cand.get("elements", [])
        if not elements:
            gaps.append(CompletenessGap(
                candidate_id=cid,
                gap_type="NO_ELEMENTS",
                description=f"候選 '{cid}' 缺少構成要件",
            ))
            continue

        for elem in elements:
            elem_id = elem.get("element_id", elem.get("id", "unknown"))
            pending_facts = elem.get("pending_facts", elem.get("facts", []))
            if not pending_facts:
                gaps.append(CompletenessGap(
                    candidate_id=cid,
                    gap_type="NO_PENDING_FACTS",
                    description=f"候選 '{cid}' 要件 '{elem_id}' 缺少待證事項",
                ))
                continue

            for fact in pending_facts:
                fact_id = fact if isinstance(fact, str) else fact.get("fact_id", fact.get("id", "unknown"))
                questions = fact.get("questions", []) if isinstance(fact, dict) else []
                if not questions and isinstance(fact, dict):
                    gaps.append(CompletenessGap(
                        candidate_id=cid,
                        gap_type="NO_QUESTIONS",
                        description=f"候選 '{cid}' 待證事項 '{fact_id}' 缺少對應問句",
                        severity="WARN",
                    ))

    return gaps


def check_alternative_preservation(
    candidates: list[dict[str, Any]],
    alternative_ids: list[str] | None = None,
) -> list[CompletenessGap]:
    """Check that alternative directions are preserved, not silently dropped."""
    gaps: list[CompletenessGap] = []
    if not alternative_ids:
        return gaps

    candidate_ids = {c.get("offense_id", c.get("id", "")) for c in candidates}
    for alt_id in alternative_ids:
        if alt_id not in candidate_ids:
            gaps.append(CompletenessGap(
                candidate_id=alt_id,
                gap_type="ALTERNATIVE_DROPPED",
                description=f"替代方向 '{alt_id}' 被靜默移除，應保留並標註理由",
            ))
    return gaps


def has_blocking_gaps(gaps: list[CompletenessGap]) -> bool:
    return any(g.severity == "BLOCK" for g in gaps)


def summarize_gaps(gaps: list[CompletenessGap]) -> str:
    if not gaps:
        return "候選完整性檢查通過"
    lines = [f"[{g.severity}] {g.description}" for g in gaps]
    return "\n".join(lines)