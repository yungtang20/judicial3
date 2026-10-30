"""4-tier synonym management (borrowed from judicial-search-tool).

Tiers:
  - confirmed:  auto-expanded during search; comes from lawyer approval or seed files.
  - candidate:  discovered by LLM during analysis; NOT auto-expanded; shown to lawyer
                for review.  Must be manually promoted to confirmed.
  - likely_typo: low corpus hit count (1-5); not expanded; low confidence.
  - rejected:    lawyer rejected or zero corpus hits; never expanded, never suggested.

Discovery-driven flow:
  Stage 3 analysis (LLM) discovers variant candidates → forced to ``candidate`` tier
  (even if corpus hits are high, because LLM may confuse distinct legal concepts).
  Lawyer reviews candidate list → approve (✓) promotes to confirmed, reject (✕)
  promotes to rejected.  Search expansion only uses ``confirmed`` tier.

This module is a pure data model + in-memory store.  Persistence is the caller's
responsibility (e.g. a JSON file or DB table).  It is intentionally not wired
into the formal case workflow until Human Gate approval.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class SynonymTier(str, Enum):
    CONFIRMED = "confirmed"
    CANDIDATE = "candidate"
    LIKELY_TYPO = "likely_typo"
    REJECTED = "rejected"


@dataclass(frozen=True)
class SynonymEntry:
    """One synonym group entry."""

    term: str
    variants: list[str]
    tier: SynonymTier
    corpus_hits: int = 0
    source: str = ""  # e.g. "seed", "llm_discovery", "lawyer_approval"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["tier"] = self.tier.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SynonymEntry":
        tier = data.get("tier", "candidate")
        if isinstance(tier, str):
            tier = SynonymTier(tier)
        return cls(
            term=data["term"],
            variants=list(data.get("variants", [])),
            tier=tier,
            corpus_hits=int(data.get("corpus_hits", 0)),
            source=data.get("source", ""),
        )


class SynonymDictionary:
    """In-memory synonym dictionary with tier filtering."""

    def __init__(self) -> None:
        self._entries: dict[str, SynonymEntry] = {}

    def upsert(self, entry: SynonymEntry) -> None:
        """Insert or replace an entry (by term)."""
        self._entries[entry.term] = entry

    def get(self, term: str) -> SynonymEntry | None:
        return self._entries.get(term)

    def all_entries(self) -> list[SynonymEntry]:
        return list(self._entries.values())

    def confirmed_variants(self, term: str) -> list[str]:
        """Return confirmed variants for a term (for search expansion).

        Only ``confirmed`` tier entries are returned.  Candidate, likely_typo,
        and rejected entries are excluded from search expansion.
        """
        entry = self._entries.get(term)
        if entry is None or entry.tier != SynonymTier.CONFIRMED:
            return [term]
        seen = {term}
        result = [term]
        for v in entry.variants:
            if v not in seen:
                seen.add(v)
                result.append(v)
        return result

    def candidates_for_review(self) -> list[SynonymEntry]:
        """Return all entries in ``candidate`` tier for lawyer review."""
        return [e for e in self._entries.values() if e.tier == SynonymTier.CANDIDATE]

    def approve(self, term: str) -> bool:
        """Promote a candidate to confirmed.  Returns True if changed."""
        entry = self._entries.get(term)
        if entry is None or entry.tier != SynonymTier.CANDIDATE:
            return False
        self._entries[term] = SynonymEntry(
            term=entry.term,
            variants=entry.variants,
            tier=SynonymTier.CONFIRMED,
            corpus_hits=entry.corpus_hits,
            source="lawyer_approval",
        )
        return True

    def reject(self, term: str) -> bool:
        """Demote a candidate to rejected.  Returns True if changed."""
        entry = self._entries.get(term)
        if entry is None or entry.tier != SynonymTier.CANDIDATE:
            return False
        self._entries[term] = SynonymEntry(
            term=entry.term,
            variants=entry.variants,
            tier=SynonymTier.REJECTED,
            corpus_hits=entry.corpus_hits,
            source="lawyer_rejection",
        )
        return True

    def discover(self, term: str, variants: list[str], corpus_hits: int = 0) -> SynonymEntry:
        """Register LLM-discovered variants as ``candidate`` tier (forced).

        Even if corpus_hits is high, the tier is forced to ``candidate`` because
        LLM may confuse distinct legal concepts (e.g. 雇主 vs 勞僱契約).
        """
        tier = SynonymTier.CANDIDATE
        if corpus_hits == 0:
            tier = SynonymTier.REJECTED
        elif 1 <= corpus_hits <= 5:
            tier = SynonymTier.LIKELY_TYPO
        # High corpus hits still candidate (not auto-confirmed) — lawyer must approve
        entry = SynonymEntry(
            term=term,
            variants=variants,
            tier=tier,
            corpus_hits=corpus_hits,
            source="llm_discovery",
        )
        self._entries[term] = entry
        return entry

    def to_dict_list(self) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self._entries.values()]

    @classmethod
    def from_dict_list(cls, data: list[dict[str, Any]]) -> "SynonymDictionary":
        d = cls()
        for item in data:
            d.upsert(SynonymEntry.from_dict(item))
        return d