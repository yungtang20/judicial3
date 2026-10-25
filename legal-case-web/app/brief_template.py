"""條陳可調整內容與固定標準段落。"""

from __future__ import annotations

from typing import Any

BRIEF_TEMPLATE_KEYS = ("case_reason", "summary_label", "followup_label")
MAX_OVERRIDE_LENGTH = 200


def clean_brief_template(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, str] = {}
    for key in BRIEF_TEMPLATE_KEYS:
        text = value.get(key)
        if isinstance(text, str) and text.strip():
            result[key] = text.strip()[:MAX_OVERRIDE_LENGTH]
    return result


def brief_value(template: dict[str, str], key: str, default: str) -> str:
    return template.get(key) or default
