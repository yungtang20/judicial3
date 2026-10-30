"""Evidence-argument chain (borrowed from Legal-Skills-Chinese evidence-argument-chain).

Establishes a complete mapping:
  Claim → Constitutive Element → Evidence → Proof Assessment

Ensures every claim has sufficient evidence, every piece of evidence has
a clear purpose, and proof strength is assessed (sufficient / insufficient /
needs corroboration).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class EvidenceLink:
    evidence_id: str
    evidence_type: str  # "testimonial", "physical", "documentary", "digital", "circumstantial"
    description: str
    supports_claim: bool = True
    source_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProofAssessment:
    element_id: str
    claim: str
    evidence_links: list[EvidenceLink] = field(default_factory=list)
    proof_strength: str = "INSUFFICIENT"  # SUFFICIENT, INSUFFICIENT, NEEDS_CORROBORATION
    missing_evidence: list[str] = field(default_factory=list)
    notes: str = ""

    def assess(self) -> str:
        """Assess proof strength based on evidence links."""
        if not self.evidence_links:
            self.proof_strength = "INSUFFICIENT"
            self.missing_evidence = ["無任何證據支持"]
            return self.proof_strength

        supporting = [e for e in self.evidence_links if e.supports_claim]
        if len(supporting) >= 2:
            self.proof_strength = "SUFFICIENT"
        elif len(supporting) == 1:
            self.proof_strength = "NEEDS_CORROBORATION"
            self.missing_evidence = ["需補強證據"]
        else:
            self.proof_strength = "INSUFFICIENT"
            self.missing_evidence = ["現有證據不支持主張"]
        return self.proof_strength

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["proof_strength"] = self.proof_strength
        return d


@dataclass
class EvidenceArgumentChain:
    """Complete evidence-argument chain for a candidate direction."""
    candidate_id: str
    assessments: list[ProofAssessment] = field(default_factory=list)

    def add_assessment(self, assessment: ProofAssessment) -> None:
        assessment.assess()
        self.assessments.append(assessment)

    def overall_strength(self) -> str:
        if not self.assessments:
            return "NO_EVIDENCE"
        strengths = [a.proof_strength for a in self.assessments]
        if all(s == "SUFFICIENT" for s in strengths):
            return "STRONG"
        if any(s == "INSUFFICIENT" for s in strengths):
            return "WEAK"
        return "MODERATE"

    def gaps(self) -> list[str]:
        """Return list of proof gaps."""
        result = []
        for a in self.assessments:
            if a.proof_strength != "SUFFICIENT":
                result.append(f"{a.element_id}: {a.proof_strength} - {', '.join(a.missing_evidence)}")
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "assessments": [a.to_dict() for a in self.assessments],
            "overall_strength": self.overall_strength(),
            "gaps": self.gaps(),
        }