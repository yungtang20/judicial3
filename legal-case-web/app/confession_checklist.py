"""Confession corroboration checklist (expert strategy §1.3, blueprint Phase 6).

When a suspect admits (ADMITTED) to a fact, the investigation manual requires
objective corroborating evidence before the admission can support a charging
decision.  This module provides a 6-item checklist that must be satisfied
before a document (brief, transfer, etc.) can be generated.

Checklist items (from investigation manual):
  1. 犯罪人 (suspect identity confirmed)
  2. 行為 (act confirmed by objective evidence)
  3. 時間 (time confirmed by objective evidence)
  4. 地點 (location confirmed by objective evidence)
  5. 物品 (objects/evidence confirmed)
  6. 客觀補強 (independent corroborating evidence exists)

Each item must have at least one linked evidence reference.  Missing items
block document generation (fail closed).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


CHECKLIST_ITEMS = [
    ("suspect_identity", "犯罪人", "嫌疑人身份已確認"),
    ("act_confirmed", "行為", "行為已由客觀證據確認"),
    ("time_confirmed", "時間", "時間已由客觀證據確認"),
    ("location_confirmed", "地點", "地點已由客觀證據確認"),
    ("objects_confirmed", "物品", "物品/證物已確認"),
    ("corroborating_evidence", "客觀補強", "存在獨立的客觀補強證據"),
]


@dataclass
class ChecklistItem:
    item_id: str
    label: str
    description: str
    satisfied: bool = False
    evidence_refs: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ConfessionChecklist:
    """6-item confession corroboration checklist."""
    case_id: str = ""
    items: list[ChecklistItem] = field(default_factory=list)

    def __post_init__(self):
        if not self.items:
            self.items = [
                ChecklistItem(item_id=iid, label=label, description=desc)
                for iid, label, desc in CHECKLIST_ITEMS
            ]

    def mark_satisfied(self, item_id: str, evidence_refs: list[str] | None = None, notes: str = "") -> bool:
        """Mark an item as satisfied with evidence references."""
        for item in self.items:
            if item.item_id == item_id:
                item.satisfied = True
                if evidence_refs:
                    item.evidence_refs = list(evidence_refs)
                if notes:
                    item.notes = notes
                return True
        return False

    def mark_unsatisfied(self, item_id: str) -> bool:
        for item in self.items:
            if item.item_id == item_id:
                item.satisfied = False
                item.evidence_refs = []
                return True
        return False

    def is_complete(self) -> bool:
        """All 6 items must be satisfied for the checklist to pass."""
        return all(item.satisfied for item in self.items)

    def missing_items(self) -> list[ChecklistItem]:
        return [item for item in self.items if not item.satisfied]

    def missing_labels(self) -> list[str]:
        return [item.label for item in self.items if not item.satisfied]

    def completion_ratio(self) -> float:
        if not self.items:
            return 0.0
        satisfied = sum(1 for item in self.items if item.satisfied)
        return satisfied / len(self.items)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "items": [item.to_dict() for item in self.items],
            "is_complete": self.is_complete(),
            "missing_labels": self.missing_labels(),
            "completion_ratio": self.completion_ratio(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConfessionChecklist":
        cl = cls(case_id=data.get("case_id", ""))
        for item_data in data.get("items", []):
            for item in cl.items:
                if item.item_id == item_data.get("item_id"):
                    item.satisfied = item_data.get("satisfied", False)
                    item.evidence_refs = list(item_data.get("evidence_refs", []))
                    item.notes = item_data.get("notes", "")
        return cl