from __future__ import annotations

import re
from typing import Any


ALLOWED_FIELDS = {"law_id", "article_no", "issue_tags", "effective_date"}
FORBIDDEN_FIELD_HINTS = {
    "name", "person", "case_id", "case_number", "summary", "narrative",
    "answer", "location", "address", "event_time", "phone", "email",
}
SENSITIVE_PATTERNS = [
    re.compile(r"[A-Z][12]\d{8}"),
    re.compile(r"09\d{8}"),
    re.compile(r"(?:臺|台).{0,8}(?:市|縣).{0,16}(?:路|街|巷|號)"),
    re.compile(r"[A-Za-z]{1,4}\d{8,}"),
]


class LegalQueryRejected(ValueError):
    pass


def sanitize_legal_query(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise LegalQueryRejected("法律查詢必須是物件")
    unknown = set(raw) - ALLOWED_FIELDS
    if unknown:
        raise LegalQueryRejected(f"法律查詢包含不允許欄位：{sorted(unknown)}")
    if FORBIDDEN_FIELD_HINTS.intersection({key.lower() for key in raw}):
        raise LegalQueryRejected("法律查詢不得包含案件或個人欄位")
    cleaned: dict[str, Any] = {}
    for key, value in raw.items():
        if key == "issue_tags":
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise LegalQueryRejected("issue_tags 必須是文字陣列")
            normalized = [item.strip() for item in value if item.strip()]
            text = " ".join(normalized)
            cleaned[key] = normalized
        else:
            text = str(value).strip()
            cleaned[key] = text
        if any(pattern.search(text) for pattern in SENSITIVE_PATTERNS):
            raise LegalQueryRejected("法律查詢疑似包含個資、代號、地址或案件內容")
    if not cleaned.get("law_id") or not cleaned.get("article_no"):
        raise LegalQueryRejected("law_id 與 article_no 為必填")
    return cleaned
