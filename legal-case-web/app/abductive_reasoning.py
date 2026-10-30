"""Abductive reasoning (borrowed from Legal-Skills-Chinese legal-abductive-reasoning).

When evidence is incomplete or facts are ambiguous, generate and evaluate
the most plausible explanatory hypotheses. Uses Mill's five methods for
structured causal inference.

Mill's five methods:
  1. Method of Agreement (求同法)
  2. Method of Difference (求異法)
  3. Joint Method (求同求異法)
  4. Method of Residues (共變法)
  5. Method of Concomitant Variation (剩余法)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Hypothesis:
    hypothesis_id: str
    description: str
    supporting_facts: list[str] = field(default_factory=list)
    contradicting_facts: list[str] = field(default_factory=list)
    plausibility: str = "UNKNOWN"  # HIGH, MEDIUM, LOW, UNKNOWN
    mill_method: str = ""

    def assess(self) -> str:
        """Assess plausibility based on supporting/contradicting facts."""
        support_count = len(self.supporting_facts)
        contra_count = len(self.contradicting_facts)
        if contra_count > 0 and support_count == 0:
            self.plausibility = "LOW"
        elif support_count >= 2 and contra_count == 0:
            self.plausibility = "HIGH"
        elif support_count >= 1 and contra_count <= 1:
            self.plausibility = "MEDIUM"
        else:
            self.plausibility = "LOW"
        return self.plausibility

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["plausibility"] = self.plausibility
        return d


@dataclass
class AbductiveResult:
    unknown_fact: str
    hypotheses: list[Hypothesis] = field(default_factory=list)
    best_hypothesis: str = ""

    def select_best(self) -> str:
        for h in self.hypotheses:
            h.assess()
        if not self.hypotheses:
            self.best_hypothesis = ""
            return ""
        best = max(self.hypotheses, key=lambda h: {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}.get(h.plausibility, 0))
        self.best_hypothesis = best.hypothesis_id
        return self.best_hypothesis

    def to_dict(self) -> dict[str, Any]:
        return {
            "unknown_fact": self.unknown_fact,
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "best_hypothesis": self.best_hypothesis,
        }


def generate_hypotheses(unknown_fact: str, known_facts: list[str]) -> AbductiveResult:
    """Generate hypotheses for an unknown fact based on known facts.

    Uses Mill's methods to structure the inference.
    """
    result = AbductiveResult(unknown_fact=unknown_fact)
    # Method of Agreement: find common factors
    if known_facts:
        result.hypotheses.append(Hypothesis(
            hypothesis_id=f"hyp:agreement:{unknown_fact}",
            description=f"基於求同法：已知事實 {', '.join(known_facts)} 共同指向 '{unknown_fact}'",
            supporting_facts=known_facts,
            mill_method="Method of Agreement (求同法)",
        ))
    # Method of Difference: if some cases have the fact and others don't
    result.hypotheses.append(Hypothesis(
        hypothesis_id=f"hyp:difference:{unknown_fact}",
        description=f"基於求異法：'{unknown_fact}' 的存在與否可能導致不同結果",
        mill_method="Method of Difference (求異法)",
    ))
    result.select_best()
    return result