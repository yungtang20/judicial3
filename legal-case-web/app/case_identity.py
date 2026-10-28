"""案件可讀名稱與文件檔名的共用規則。"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any


CASE_IDENTITY_VERSION = "agency-v1"
_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_PROPERTY_BOUNDARY_PENDING = {"theft", "embezzlement"}


def _compact_roc_date(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "UNKNOWN"
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        match = re.search(r"(\d{1,3})年(\d{1,2})月(\d{1,2})日", text)
        if not match:
            return "UNKNOWN"
        return f"{int(match.group(1)):03d}{int(match.group(2)):02d}{int(match.group(3)):02d}"
    year = moment.year - 1911
    if year <= 0:
        return "UNKNOWN"
    return f"{year:03d}{moment.month:02d}{moment.day:02d}"


def _offense_label(case: dict[str, Any]) -> str:
    selected = set(case.get("selected_offenses") or [])
    if selected == _PROPERTY_BOUNDARY_PENDING:
        # 這是使用者指定的正式案由標籤；竊盜／侵占的區辨仍留在問句與內部審查。
        return "待侵占"
    if len(selected) > 1:
        return "待確認"
    names: list[str] = []
    for item in case.get("candidates") or []:
        if not isinstance(item, dict):
            continue
        if selected and item.get("id") not in selected:
            continue
        name = str(item.get("name") or "").strip()
        if name and name not in names:
            names.append(name)
    # 多個罪章在此階段只是競合／區分候選，不能直接合併成正式案由。
    return names[0] if len(names) == 1 else "待確認"


def _subject_name(case: dict[str, Any]) -> str:
    """案件名稱優先使用建立案件資料，否則回退到已保存的筆錄姓名。"""
    intake = case.get("intake") or {}
    subject = str(intake.get("victim_identifier") or "").strip()
    if subject:
        return subject
    profile = (case.get("profiles") or {}).get("victim:default") or {}
    return str(profile.get("name") or "").strip() or "未具名"


def case_display_name(case: dict[str, Any]) -> str:
    intake = case.get("intake") or {}
    subject = _subject_name(case)
    output_context = case.get("output_context") or {}
    officer = str(output_context.get("officer") or "").strip() or "未填員警"
    return f"{_compact_roc_date(intake.get('event_time'))}{subject}遭{_offense_label(case)}案({officer})"


def case_reason_name(case: dict[str, Any]) -> str:
    """正式條陳案由名稱；與保存案件名稱分離，不包含年月日及員警。"""
    intake = case.get("intake") or {}
    subject = _subject_name(case)
    return f"{subject}遭{_offense_label(case)}案"


def case_identity(case: dict[str, Any]) -> dict[str, str]:
    intake = case.get("intake") or {}
    return {
        "format_version": CASE_IDENTITY_VERSION,
        "date": _compact_roc_date(intake.get("event_time")),
        "subject_name": str(intake.get("victim_identifier") or "").strip() or "未具名",
        "case_label": _offense_label(case),
        "officer_name": str((case.get("output_context") or {}).get("officer") or "").strip() or "未填員警",
        "display_name": case_display_name(case),
    }


def safe_document_stem(case: dict[str, Any]) -> str:
    value = _INVALID_FILENAME_CHARS.sub("_", case_display_name(case))
    value = re.sub(r"\s+", " ", value).strip().strip(".")
    return value[:160] or "未命名案件"
