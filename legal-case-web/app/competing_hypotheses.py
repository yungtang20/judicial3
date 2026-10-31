"""Competing hypotheses for parallel case directions.

Do NOT rank legal establishment by count of supporting facts.
DENIED is a party statement, not factual FALSE.
Fact statuses: ASSERTED, ADMITTED, DENIED, INFERRED, UNKNOWN.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4


ALLOWED_FACT_STATUS = frozenset(
    {"ASSERTED", "ADMITTED", "DENIED", "INFERRED", "UNKNOWN"}
)

ALLOWED_HYPOTHESIS_STATUS = frozenset(
    {"ACTIVE", "NEED_REVIEW", "LOWERED", "PARKED"}
)


@dataclass
class FactRef:
    fact_key: str
    status: str = "UNKNOWN"  # ASSERTED | ADMITTED | DENIED | INFERRED | UNKNOWN
    note: str = ""

    def __post_init__(self) -> None:
        if self.status not in ALLOWED_FACT_STATUS:
            self.status = "UNKNOWN"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Hypothesis:
    hypothesis_id: str
    description: str
    supporting_facts: list[FactRef] = field(default_factory=list)
    contradicting_facts: list[FactRef] = field(default_factory=list)
    unknown_facts: list[FactRef] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)
    discriminating_questions: list[str] = field(default_factory=list)
    legal_sources: list[dict[str, Any]] = field(default_factory=list)
    status: str = "NEED_REVIEW"

    def __post_init__(self) -> None:
        if not self.hypothesis_id:
            self.hypothesis_id = str(uuid4())
        if self.status not in ALLOWED_HYPOTHESIS_STATUS:
            self.status = "NEED_REVIEW"

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "description": self.description,
            "supporting_facts": [f.to_dict() for f in self.supporting_facts],
            "contradicting_facts": [f.to_dict() for f in self.contradicting_facts],
            "unknown_facts": [f.to_dict() for f in self.unknown_facts],
            "required_evidence": list(self.required_evidence),
            "discriminating_questions": list(self.discriminating_questions),
            "legal_sources": list(self.legal_sources),
            "status": self.status,
            # Explicit: never treat support count as legal proof
            "support_count_is_not_legal_proof": True,
        }


@dataclass
class CompetingHypotheses:
    """Set of mutually considered directions (e.g. 侵占 vs 竊盜 vs 民事)."""

    case_id: str = ""
    hypotheses: list[Hypothesis] = field(default_factory=list)

    def add(self, hypothesis: Hypothesis) -> None:
        self.hypotheses.append(hypothesis)

    def discriminating_question_pool(self) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for h in self.hypotheses:
            for q in h.discriminating_questions:
                if q not in seen:
                    seen.add(q)
                    out.append(q)
        return out

    def unknowns_union(self) -> list[str]:
        keys: list[str] = []
        seen: set[str] = set()
        for h in self.hypotheses:
            for f in h.unknown_facts:
                if f.fact_key not in seen:
                    seen.add(f.fact_key)
                    keys.append(f.fact_key)
        return keys

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "discriminating_questions": self.discriminating_question_pool(),
            "unknown_fact_keys": self.unknowns_union(),
            "disclaimer": "候選方向僅供調查與人工審閱，不表示犯罪成立或排除。",
        }


def example_custody_property_set() -> CompetingHypotheses:
    """Illustrative set: 侵占 / 竊盜 / 詐欺 / 民事 — not a legal conclusion."""
    ch = CompetingHypotheses(case_id="example")
    ch.add(
        Hypothesis(
            hypothesis_id="hyp-embezzlement",
            description="侵占方向：是否已合法持有、有無易持有為所有",
            unknown_facts=[
                FactRef("lawful_custody", "UNKNOWN"),
                FactRef("conversion_act", "UNKNOWN"),
            ],
            required_evidence=["交付保管經過", "處分或拒還行為"],
            discriminating_questions=[
                "財物交付時是否基於保管／委託合意？",
                "事後有無表示據為己有或拒不返還？",
            ],
            status="NEED_REVIEW",
        )
    )
    ch.add(
        Hypothesis(
            hypothesis_id="hyp-theft",
            description="竊盜方向：是否原由他人持有、如何取得",
            unknown_facts=[
                FactRef("prior_holder", "UNKNOWN"),
                FactRef("taking_method", "UNKNOWN"),
            ],
            required_evidence=["取得當下持有狀態", "取得方式"],
            discriminating_questions=[
                "取得前財物由誰事實管領？",
                "是否未經同意而取走？",
            ],
            status="NEED_REVIEW",
        )
    )
    ch.add(
        Hypothesis(
            hypothesis_id="hyp-fraud",
            description="詐欺方向：交付前有無施用詐術",
            unknown_facts=[FactRef("deception_before_delivery", "UNKNOWN")],
            required_evidence=["交付前陳述與真相", "陷於錯誤與處分財產關連"],
            discriminating_questions=["對方因何交付財物？交付前有無不實資訊？"],
            status="NEED_REVIEW",
        )
    )
    ch.add(
        Hypothesis(
            hypothesis_id="hyp-civil",
            description="民事爭議：契約、授權或返還約定",
            unknown_facts=[FactRef("contract_or_authorization", "UNKNOWN")],
            required_evidence=["契約或授權文件", "返還約定"],
            discriminating_questions=["雙方有無借用、買賣或授權約定？"],
            status="NEED_REVIEW",
        )
    )
    return ch
