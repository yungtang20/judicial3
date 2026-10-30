"""Version invalidation / STALE marking (expert strategy §1.7, blueprint §7).

When upstream data changes (case revision, analysis revision, fact update),
downstream documents (briefs, interview records, transfer documents) must be
automatically marked STALE.  Stale documents cannot be treated as the latest
approved version.

Dependency chain:
  CaseRevision → AnalysisRevision → DocumentRevision

Any upstream change propagates STALE downstream.  Regeneration preserves the
old version for comparison.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class DocumentStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    STALE = "STALE"
    SUPERSEDED = "SUPERSEDED"


@dataclass
class VersionNode:
    """A node in the version dependency chain."""
    node_id: str
    node_type: str  # "case", "analysis", "document"
    version: int
    status: str = "DRAFT"
    upstream_deps: list[str] = field(default_factory=list)  # node_ids this depends on
    upstream_versions: dict[str, int] = field(default_factory=dict)  # dep_id → version at creation
    created_at: str = ""
    invalidated_at: str = ""
    invalidated_reason: str = ""

    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = DocumentStatus(self.status).value if self.status in [e.value for e in DocumentStatus] else self.status
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class VersionChain:
    """Manages a chain of versioned nodes with STALE propagation."""

    def __init__(self) -> None:
        self._nodes: dict[str, VersionNode] = {}

    def register(self, node: VersionNode) -> None:
        self._nodes[node.node_id] = node

    def get(self, node_id: str) -> VersionNode | None:
        return self._nodes.get(node_id)

    def update_upstream(self, node_id: str, new_version: int) -> list[str]:
        """Notify that an upstream node has changed to new_version.

        Marks all downstream dependents as STALE if their recorded upstream
        version doesn't match.  Returns list of invalidated node_ids.
        """
        invalidated: list[str] = []
        for nid, node in list(self._nodes.items()):
            if node_id in node.upstream_deps:
                recorded = node.upstream_versions.get(node_id, 0)
                if recorded != new_version and node.status != DocumentStatus.STALE.value:
                    node.status = DocumentStatus.STALE.value
                    node.invalidated_at = datetime.now(timezone.utc).isoformat()
                    node.invalidated_reason = (
                        f"upstream {node_id} changed from v{recorded} to v{new_version}"
                    )
                    invalidated.append(nid)
                    # Propagate further downstream: mark all dependents of this node stale
                    for dep_nid, dep_node in list(self._nodes.items()):
                        if nid in dep_node.upstream_deps and dep_node.status != DocumentStatus.STALE.value:
                            dep_node.status = DocumentStatus.STALE.value
                            dep_node.invalidated_at = datetime.now(timezone.utc).isoformat()
                            dep_node.invalidated_reason = f"upstream {nid} marked stale"
                            invalidated.append(dep_nid)
        return invalidated

    def mark_stale(self, node_id: str, reason: str) -> bool:
        """Manually mark a node as STALE."""
        node = self._nodes.get(node_id)
        if node is None:
            return False
        if node.status == DocumentStatus.STALE.value:
            return False
        node.status = DocumentStatus.STALE.value
        node.invalidated_at = datetime.now(timezone.utc).isoformat()
        node.invalidated_reason = reason
        # Propagate
        for nid, n in self._nodes.items():
            if node_id in n.upstream_deps:
                self.mark_stale(nid, f"upstream {node_id} marked stale: {reason}")
        return True

    def is_stale(self, node_id: str) -> bool:
        node = self._nodes.get(node_id)
        if node is None:
            return False
        return node.status == DocumentStatus.STALE.value

    def all_nodes(self) -> list[VersionNode]:
        return list(self._nodes.values())

    def stale_nodes(self) -> list[VersionNode]:
        return [n for n in self._nodes.values() if n.status == DocumentStatus.STALE.value]