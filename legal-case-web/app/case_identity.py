"""案件可讀名稱與文件檔名的共用規則。"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any


CASE_IDENTITY_VERSION = "agency-v1"
_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


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
    names: list[str] = []
    for item in case.get("candidates") or []:
        if not isinstance(item, dict):
            continue
        if selected and item.get("id") not in selected:
            continue
        name = str(item.get("name") or "").strip()
        if name and name not in names:
            names.append(name)
    return "、".join(names) or "待確認"


def case_display_name(case: dict[str, Any]) -> str:
    intake = case.get("intake") or {}
    subject = str(intake.get("victim_identifier") or "").strip() or "未具名"
    officer = str(intake.get("officer") or "").strip() or "未填員警"
    return f"{_compact_roc_date(intake.get('event_time'))}{subject}遭{_offense_label(case)}案({officer})"


def case_identity(case: dict[str, Any]) -> dict[str, str]:
    intake = case.get("intake") or {}
    return {
        "format_version": CASE_IDENTITY_VERSION,
        "date": _compact_roc_date(intake.get("event_time")),
        "subject_name": str(intake.get("victim_identifier") or "").strip() or "未具名",
        "case_label": _offense_label(case),
        "officer_name": str(intake.get("officer") or "").strip() or "未填員警",
        "display_name": case_display_name(case),
    }


def safe_document_stem(case: dict[str, Any]) -> str:
    value = _INVALID_FILENAME_CHARS.sub("_", case_display_name(case))
    value = re.sub(r"\s+", " ", value).strip().strip(".")
    return value[:160] or "未命名案件"
