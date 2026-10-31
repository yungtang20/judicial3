"""MCP call verification records.

MCP tool success does NOT equal correct legal application.
Statuses:
  MCP_UNAVAILABLE | NOT_FOUND | NEEDS_REVIEW | VERSION_UNVERIFIED | VERIFIED

Fail closed when MCP is unavailable: never substitute model memory for statutes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from hashlib import sha256
from typing import Any


class VerificationStatus(str, Enum):
    MCP_UNAVAILABLE = "MCP_UNAVAILABLE"
    NOT_FOUND = "NOT_FOUND"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    VERSION_UNVERIFIED = "VERSION_UNVERIFIED"
    VERIFIED = "VERIFIED"


@dataclass
class McpVerificationRecord:
    provider: str = "taiwan-law-mcp"
    tool: str = ""
    status: str = VerificationStatus.NEEDS_REVIEW.value
    query_hash: str = ""
    retrieved_at: str = ""
    source_url: str = ""
    jid: str = ""
    case_revision: int | None = None
    notes: str = ""
    raw_hit_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def hash_query(query: str) -> str:
    normalized = (query or "").strip().encode("utf-8")
    return sha256(normalized).hexdigest()[:16]


def build_record(
    *,
    tool: str,
    status: VerificationStatus | str,
    query: str = "",
    source_url: str = "",
    jid: str = "",
    case_revision: int | None = None,
    hit_count: int = 0,
    notes: str = "",
    provider: str = "taiwan-law-mcp",
) -> McpVerificationRecord:
    status_value = status.value if isinstance(status, VerificationStatus) else str(status)
    return McpVerificationRecord(
        provider=provider,
        tool=tool,
        status=status_value,
        query_hash=hash_query(query) if query else "",
        retrieved_at=datetime.now(UTC).isoformat(),
        source_url=source_url,
        jid=jid,
        case_revision=case_revision,
        notes=notes,
        raw_hit_count=hit_count,
    )


def classify_mcp_result(
    *,
    tool_available: bool,
    hit_count: int,
    source_url: str = "",
    jid: str = "",
    version_checked_for_event_date: bool = False,
) -> VerificationStatus:
    """Map tool outcome to status. Does not assert legal correctness."""
    if not tool_available:
        return VerificationStatus.MCP_UNAVAILABLE
    if hit_count <= 0:
        return VerificationStatus.NOT_FOUND
    if not source_url and not jid:
        return VerificationStatus.NEEDS_REVIEW
    if not version_checked_for_event_date:
        return VerificationStatus.VERSION_UNVERIFIED
    return VerificationStatus.VERIFIED


def fail_closed_message(status: VerificationStatus | str) -> str:
    status_value = status.value if isinstance(status, VerificationStatus) else str(status)
    if status_value == VerificationStatus.MCP_UNAVAILABLE.value:
        return "MCP 不可用：不得以模型記憶代替法源；標註 [待檢索] 並停止假裝已查證。"
    if status_value == VerificationStatus.NOT_FOUND.value:
        return "檢索無命中：標註 [待檢索]，可建議改寫關鍵字。"
    if status_value == VerificationStatus.VERSION_UNVERIFIED.value:
        return "已有來源但未核對事件日法規版本：標 VERSION_UNVERIFIED，需人工或沿革工具確認。"
    if status_value == VerificationStatus.NEEDS_REVIEW.value:
        return "來源不完整：需人工審閱後才能作為引用。"
    return "已記錄 MCP 回傳來源；仍須人工判斷是否適用本案。"


def append_record(case: dict[str, Any], record: McpVerificationRecord) -> None:
    """Attach verification log on case dict (in-memory / payload-compatible)."""
    log = case.setdefault("mcp_verification_log", [])
    if isinstance(log, list):
        log.append(record.to_dict())
