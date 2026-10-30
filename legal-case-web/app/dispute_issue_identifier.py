"""Dispute issue identification (borrowed from Legal-Skills-Chinese dispute-issue-identification).

Identifies core dispute issues from legal facts:
  - Which facts are contested (disputed)
  - Which are uncontested (can be skipped)
  - What are the core legal questions
  - Transforms case relationships into legal relationship questions
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DisputeIssue:
    issue_id: str
    issue_type: str  # "contested_fact", "legal_question", "evidence_dispute"
    description: str
    contested_by: list[str] = field(default_factory=list)  # who contests
    related_elements: list[str] = field(default_factory=list)
    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def identify_dispute_issues(
    facts: list[dict[str, Any]],
    parties: list[str] | None = None,
) -> list[DisputeIssue]:
    """Identify dispute issues from a list of facts.

    Args:
        facts: List of fact dicts with keys: fact_key, value, status, source_refs, etc.
        parties: List of party identifiers (e.g., ["suspect", "victim"]).

    Returns:
        List of DisputeIssue objects.
    """
    issues: list[DisputeIssue] = []
    parties = parties or ["suspect", "victim"]

    for f in facts:
        fact_key = f.get("fact_key", f.get("id", "unknown"))
        status = f.get("status", f.get("machine_status", "UNKNOWN"))

        # DENIED facts are contested
        if status == "DENIED":
            issues.append(DisputeIssue(
                issue_id=f"dispute:{fact_key}",
                issue_type="contested_fact",
                description=f"事實 '{fact_key}' 被否認，為爭議焦點",
                contested_by=["suspect"],
                related_elements=f.get("element_refs", []),
                priority="HIGH",
            ))

        # DISPUTED facts are contested
        if status == "DISPUTED":
            issues.append(DisputeIssue(
                issue_id=f"dispute:{fact_key}",
                issue_type="contested_fact",
                description=f"事實 '{fact_key}' 有矛盾，需釐清",
                contested_by=["system"],
                related_elements=f.get("element_refs", []),
                priority="HIGH",
            ))

        # Facts with multiple source refs but conflicting may be disputed
        source_refs = f.get("source_refs", [])
        if len(source_refs) > 1 and status in ("ASSERTED", "UNKNOWN"):
            issues.append(DisputeIssue(
                issue_id=f"evidence_dispute:{fact_key}",
                issue_type="evidence_dispute",
                description=f"事實 '{fact_key}' 有多個來源，可能有證據衝突",
                contested_by=["system"],
                related_elements=f.get("element_refs", []),
                priority="MEDIUM",
            ))

    # Identify uncontested facts (can be skipped in questioning)
    uncontested = [f for f in facts if f.get("status") in ("ADMITTED", "FACT")]
    if uncontested:
        issues.append(DisputeIssue(
            issue_id="uncontested_summary",
            issue_type="legal_question",
            description=f"有 {len(uncontested)} 項無爭議事實，可跳過詢問",
            priority="LOW",
        ))

    return issues


def summarize_disputes(issues: list[DisputeIssue]) -> str:
    if not issues:
        return "無爭議焦點"
    high = [i for i in issues if i.priority == "HIGH"]
    medium = [i for i in issues if i.priority == "MEDIUM"]
    lines = []
    if high:
        lines.append(f"高優先爭議 ({len(high)} 項):")
        for i in high:
            lines.append(f"  - {i.description}")
    if medium:
        lines.append(f"中優先爭議 ({len(medium)} 項):")
        for i in medium:
            lines.append(f"  - {i.description}")
    return "\n".join(lines)