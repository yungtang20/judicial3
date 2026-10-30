"""Tamper-evident audit log with hash chain (expert strategy §1.9).

Each audit entry includes a hash of the previous entry, forming a chain.
If any entry is modified or deleted, the chain breaks and verification fails.
This provides append-only integrity without requiring a database constraint.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class AuditEntry:
    """A single tamper-evident audit entry."""
    event: str
    at: str
    actor: str = "system"
    metadata: dict[str, Any] = field(default_factory=dict)
    prev_hash: str = ""
    entry_hash: str = ""

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of this entry (excluding entry_hash itself)."""
        payload = {
            "event": self.event,
            "at": self.at,
            "actor": self.actor,
            "metadata": self.metadata,
            "prev_hash": self.prev_hash,
        }
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def seal(self) -> None:
        """Compute and set entry_hash."""
        self.entry_hash = self.compute_hash()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuditEntry":
        return cls(
            event=data.get("event", ""),
            at=data.get("at", ""),
            actor=data.get("actor", "system"),
            metadata=dict(data.get("metadata", {})),
            prev_hash=data.get("prev_hash", ""),
            entry_hash=data.get("entry_hash", ""),
        )


class AuditChain:
    """Manages a chain of tamper-evident audit entries."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def append(self, event: str, *, actor: str = "system", metadata: dict[str, Any] | None = None) -> AuditEntry:
        """Append a new entry to the chain, sealing it with the previous hash."""
        prev_hash = self._entries[-1].entry_hash if self._entries else "GENESIS"
        entry = AuditEntry(
            event=event,
            at=datetime.now(timezone.utc).isoformat(),
            actor=actor,
            metadata=metadata or {},
            prev_hash=prev_hash,
        )
        entry.seal()
        self._entries.append(entry)
        return entry

    def verify(self) -> tuple[bool, str]:
        """Verify the integrity of the entire chain.

        Returns (True, "") if valid, (False, reason) if tampered.
        """
        if not self._entries:
            return True, ""

        # First entry must link to GENESIS
        if self._entries[0].prev_hash != "GENESIS":
            return False, "first entry prev_hash must be GENESIS"

        for i, entry in enumerate(self._entries):
            # Recompute hash
            recomputed = entry.compute_hash()
            if recomputed != entry.entry_hash:
                return False, f"entry {i} hash mismatch (tampered)"

            # Check chain link
            if i > 0:
                if entry.prev_hash != self._entries[i - 1].entry_hash:
                    return False, f"entry {i} prev_hash does not match entry {i-1} hash (chain broken)"

        return True, ""

    def entries(self) -> list[AuditEntry]:
        return list(self._entries)

    def to_list(self) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self._entries]

    @classmethod
    def from_list(cls, data: list[dict[str, Any]]) -> "AuditChain":
        chain = cls()
        for item in data:
            entry = AuditEntry.from_dict(item)
            chain._entries.append(entry)
        return chain

    def length(self) -> int:
        return len(self._entries)