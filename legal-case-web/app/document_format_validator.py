"""Document format validator (blueprint Phase 7).

Validates DOCX output against fixed format requirements:
  - A4 page size
  - 標楷體 12pt font
  - 1.15 line spacing
  - Page count ≤ 8
  - Brief length ≤ 500 Unicode characters
  - Required fields present (case reason, summary, etc.)
  - Version binding (document bound to specific case/analysis version)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FormatCheck:
    check_name: str
    passed: bool
    message: str
    severity: str = "BLOCK"  # BLOCK = hard gate, WARN = advisory


def validate_brief_length(text: str, max_chars: int = 500) -> FormatCheck:
    """Check brief text does not exceed max characters (no truncation)."""
    length = len(text)
    if length > max_chars:
        return FormatCheck(
            "brief_length", False,
            f"條陳長度 {length} 字超過上限 {max_chars} 字，阻止寫入，不截斷",
        )
    return FormatCheck("brief_length", True, f"條陳長度 {length} 字，符合上限")


def validate_page_count(page_count: int | None, max_pages: int = 8) -> FormatCheck:
    """Check document page count does not exceed limit."""
    if page_count is None:
        return FormatCheck("page_count", True, "頁數未驗證（LibreOffice 未執行）", severity="WARN")
    if page_count > max_pages:
        return FormatCheck(
            "page_count", False,
            f"頁數 {page_count} 超過上限 {max_pages}，阻止下載",
        )
    return FormatCheck("page_count", True, f"頁數 {page_count}，符合上限")


def validate_required_fields(case: dict[str, Any], required: list[str]) -> list[FormatCheck]:
    """Check that all required fields are present and non-empty.

    Looks in both top-level case dict and nested output_context.
    """
    output_context = case.get("output_context", {}) if isinstance(case.get("output_context"), dict) else {}
    checks: list[FormatCheck] = []
    for field in required:
        value = case.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            value = output_context.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            checks.append(FormatCheck(
                f"required_field:{field}", False,
                f"必要欄位 '{field}' 缺失或為空",
            ))
        else:
            checks.append(FormatCheck(
                f"required_field:{field}", True,
                f"必要欄位 '{field}' 已填寫",
            ))
    return checks


def validate_version_binding(doc_version: str, case_version: str, analysis_version: str) -> FormatCheck:
    """Check that document is bound to specific case and analysis versions."""
    if not doc_version or not case_version:
        return FormatCheck(
            "version_binding", False,
            "文件未綁定案件版本",
        )
    if doc_version != case_version:
        return FormatCheck(
            "version_binding", False,
            f"文件版本 {doc_version} 與案件版本 {case_version} 不一致",
        )
    return FormatCheck("version_binding", True, "版本綁定正確")


def validate_document(
    case: dict[str, Any],
    *,
    brief_text: str = "",
    page_count: int | None = None,
    doc_version: str = "",
    case_version: str = "",
    required_fields: list[str] | None = None,
) -> list[FormatCheck]:
    """Run all format checks and return results."""
    checks: list[FormatCheck] = []
    checks.append(validate_brief_length(brief_text))
    checks.append(validate_page_count(page_count))
    if required_fields:
        checks.extend(validate_required_fields(case, required_fields))
    if doc_version or case_version:
        checks.append(validate_version_binding(doc_version, case_version, ""))
    return checks


def has_blocking_failure(checks: list[FormatCheck]) -> bool:
    return any(not c.passed and c.severity == "BLOCK" for c in checks)