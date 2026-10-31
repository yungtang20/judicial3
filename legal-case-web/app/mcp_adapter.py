"""MCP adapter boundary for taiwan-law tools.

Without a live connected MCP client, all lookups fail closed as MCP_UNAVAILABLE.
Does not invent statute text. Callers must attach McpVerificationRecord to the case.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .mcp_verification import (
    McpVerificationRecord,
    VerificationStatus,
    build_record,
    classify_mcp_result,
)


@dataclass
class McpLookupResult:
    records: list[dict[str, Any]] = field(default_factory=list)
    verification: McpVerificationRecord | None = None
    available: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "records": self.records,
            "verification": self.verification.to_dict() if self.verification else None,
            "available": self.available,
        }


class TaiwanLawMcpAdapter:
    """Optional inject of real tool callables; default is unavailable."""

    def __init__(
        self,
        search_laws: Callable[..., Any] | None = None,
        search_judgments: Callable[..., Any] | None = None,
    ) -> None:
        self._search_laws = search_laws
        self._search_judgments = search_judgments

    def search_laws(
        self,
        query: str,
        *,
        case_revision: int | None = None,
        version_checked_for_event_date: bool = False,
    ) -> McpLookupResult:
        if self._search_laws is None:
            ver = build_record(
                tool="search_taiwan_laws",
                status=VerificationStatus.MCP_UNAVAILABLE,
                query=query,
                case_revision=case_revision,
                notes="no live MCP client bound",
            )
            return McpLookupResult(records=[], verification=ver, available=False)
        try:
            raw = self._search_laws(query=query)
            hits = list(raw) if raw is not None else []
            if not isinstance(hits, list):
                hits = [hits]
            source_url = ""
            if hits and isinstance(hits[0], dict):
                source_url = str(hits[0].get("source_url") or hits[0].get("url") or "")
            status = classify_mcp_result(
                tool_available=True,
                hit_count=len(hits),
                source_url=source_url,
                version_checked_for_event_date=version_checked_for_event_date,
            )
            ver = build_record(
                tool="search_taiwan_laws",
                status=status,
                query=query,
                source_url=source_url,
                case_revision=case_revision,
                hit_count=len(hits),
            )
            return McpLookupResult(records=hits, verification=ver, available=True)
        except Exception as exc:  # noqa: BLE001
            ver = build_record(
                tool="search_taiwan_laws",
                status=VerificationStatus.MCP_UNAVAILABLE,
                query=query,
                case_revision=case_revision,
                notes=f"tool error: {type(exc).__name__}",
            )
            return McpLookupResult(records=[], verification=ver, available=False)
