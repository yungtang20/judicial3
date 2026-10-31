"""Fail-closed legal-source verification against MCP for analysis candidates.

The application never substitutes model memory for statutes. For each candidate's
curated ``source`` (law name + article number, taken only from the rule bank
— never from raw case text), this module:

1. calls the bound MCP adapter (local snapshot first, remote live lookup second);
2. records one ``McpVerificationRecord`` per source on the case and on the
   candidate (``law_verification``);
3. degrades to ``MCP_UNAVAILABLE`` / ``NOT_FOUND`` when the MCP is unreachable or
   returns no hits, without raising.
"""

from __future__ import annotations

from typing import Any

from .mcp_adapter import TaiwanLawMcpAdapter
from .mcp_verification import McpVerificationRecord, append_record


def verify_candidate_sources(
    candidates: list[dict[str, Any]],
    adapter: TaiwanLawMcpAdapter | None = None,
    case: dict[str, Any] | None = None,
) -> list[McpVerificationRecord]:
    """Verify each candidate's statutory source against the MCP, fail-closed."""
    records: list[McpVerificationRecord] = []
    if adapter is None:
        adapter = TaiwanLawMcpAdapter()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        source = candidate.get("source") or {}
        law_name = str(source.get("law_name", ""))
        article_no = str(source.get("article_no", ""))
        if not law_name or not article_no:
            continue
        query = f"{law_name} {article_no}"
        result = adapter.search_laws(query)
        ver = result.verification
        if ver is not None:
            records.append(ver)
            if case is not None:
                append_record(case, ver)
        candidate.setdefault("law_verification", []).append({
            "law_name": law_name,
            "article_no": article_no,
            "status": ver.status if ver else VerificationStatus.MCP_UNAVAILABLE.value,
            "source_url": ver.source_url if ver else "",
            "hit_count": len(result.records),
        })
    return records
