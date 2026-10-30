"""Fact state machine for criminal investigation (expert strategy §1.5, §3.3).

Fact states:
  - ASSERTED:   stated by a party but not yet verified
  - ADMITTED:   admitted by the suspect/defendant (confession)
  - DENIED:     denied by the suspect/defendant
  - INFERRED:   inferred from other facts/evidence (not directly stated)
  - UNKNOWN:    no evidence either way

Key rules (from investigation manual):
  1. DENIED does not mean the fact does not exist (denial ≠ exclusion).
  2. ADMITTED must have corroborating objective evidence (confession alone ≠ conviction).
  3. INFERRED must cite the source facts/evidence it was derived from.
  4. UNKNOWN facts must be covered by follow-up questions.
  5. State transitions are logged with reason and timestamp.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class FactState(str, Enum):
    ASSERTED = "ASSERTED"
    ADMITTED = "ADMITTED"
    DENIED = "DENIED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


# Valid state transitions
VALID_TRANSITIONS: dict[FactState, set[FactState]] = {
    FactState.ASSERTED: {FactState.ADMITTED, FactState.DENIED, FactState.INFERRED, FactState.UNKNOWN},
    FactState.ADMITTED: {FactState.DENIED, FactState.UNKNOWN},  # can be retracted
    FactState.DENIED: {FactState.ADMITTED, FactState.INFERRED, FactState.UNKNOWN},  # denial can be overcome by evidence
    FactState.INFERRED: {FactState.ASSERTED, FactState.ADMITTED, FactState.DENIED, FactState.UNKNOWN},
    FactState.UNKNOWN: {FactState.ASSERTED, FactState.ADMITTED, FactState.DENIED, FactState.INFERRED},
}


@dataclass
class FactTransition:
    """Records a state transition for audit purposes."""
    from_state: str
    to_state: str
    reason: str
    timestamp: str
    actor: str = "system"  # "system" or "human:<id>"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ManagedFact:
    """A fact with state machine tracking."""
    fact_key: str
    value: Any
    state: FactState = FactState.UNKNOWN
    source_refs: list[str] = field(default_factory=list)
    corroborating_evidence: list[str] = field(default_factory=list)
    inferred_from: list[str] = field(default_factory=list)
    transitions: list[FactTransition] = field(default_factory=list)
    last_updated: str = ""

    def __post_init__(self):
        if isinstance(self.state, str):
            self.state = FactState(self.state)
        if not self.last_updated:
            self.last_updated = datetime.now(timezone.utc).isoformat()

    def transition_to(
        self,
        new_state: FactState,
        reason: str,
        actor: str = "system",
    ) -> bool:
        """Attempt a state transition. Returns True if successful."""
        if isinstance(new_state, str):
            new_state = FactState(new_state)
        if new_state not in VALID_TRANSITIONS.get(self.state, set()):
            return False
        # Special rule: ADMITTED requires corroborating evidence for conviction
        # (but the state transition itself is allowed; the gate is at document output)
        transition = FactTransition(
            from_state=self.state.value,
            to_state=new_state.value,
            reason=reason,
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor=actor,
        )
        self.transitions.append(transition)
        self.state = new_state
        self.last_updated = transition.timestamp
        return True

    def has_corroboration(self) -> bool:
        """Check if an ADMITTED fact has corroborating objective evidence."""
        return self.state == FactState.ADMITTED and len(self.corroborating_evidence) > 0

    def is_denial_with_evidence(self) -> bool:
        """Check if a fact is DENIED but has supporting evidence (contradiction)."""
        return self.state == FactState.DENIED and len(self.source_refs) > 0

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ManagedFact":
        return cls(
            fact_key=data.get("fact_key", ""),
            value=data.get("value"),
            state=data.get("state", "UNKNOWN"),
            source_refs=list(data.get("source_refs", [])),
            corroborating_evidence=list(data.get("corroborating_evidence", [])),
            inferred_from=list(data.get("inferred_from", [])),
            transitions=[FactTransition(**t) for t in data.get("transitions", [])],
            last_updated=data.get("last_updated", ""),
        )


def check_admission_corroboration(facts: list[ManagedFact]) -> list[dict[str, str]]:
    """Check all ADMITTED facts for corroborating evidence.

    Returns a list of issues (empty = all OK).
    """
    issues: list[dict[str, str]] = []
    for fact in facts:
        if fact.state == FactState.ADMITTED and not fact.has_corroboration():
            issues.append({
                "fact_key": fact.fact_key,
                "issue": "ADMISSION_WITHOUT_CORROBORATION",
                "description": f"事實 '{fact.fact_key}' 為自白 (ADMITTED)，但缺乏客觀補強證據",
            })
    return issues


def find_denial_contradictions(facts: list[ManagedFact]) -> list[dict[str, str]]:
    """Find facts that are DENIED but have supporting evidence (contradiction)."""
    contradictions: list[dict[str, str]] = []
    for fact in facts:
        if fact.is_denial_with_evidence():
            contradictions.append({
                "fact_key": fact.fact_key,
                "issue": "DENIAL_WITH_EVIDENCE",
                "description": (
                    f"事實 '{fact.fact_key}' 被否認 (DENIED)，"
                    f"但仍有 {len(fact.source_refs)} 筆來源證據支持"
                ),
            })
    return contradictions