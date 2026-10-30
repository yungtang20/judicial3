"""Forbidden conclusion scanner (expert strategy §1.12).

System output (candidate analysis, question text, brief text, document text)
must never contain conclusions that bypass human review or overstate evidence.
This module scans text for known forbidden conclusion patterns and returns
a list of violations.  It is a hard gate: any violation blocks output.

Patterns are grouped by category:
  - AUTO_CONVICT: conclusions that treat a statement as proof of guilt
  - KEYWORD_TO_CRIME: conclusions that equate a keyword with a crime
  - DENIAL_EQUALS_EXCLUSION: conclusions that treat denial as exclusion
  - CONFESSION_WITHOUT_CORROBORATION: conclusions that treat confession as sufficient
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ForbiddenConclusion:
    category: str
    pattern: str
    description: str
    severity: str = "BLOCK"  # BLOCK = hard gate, WARN = advisory


# ---------------------------------------------------------------------------
# Forbidden conclusion patterns (Taiwan criminal investigation context)
# ---------------------------------------------------------------------------
# Each pattern is a regex.  Matching is case-insensitive and whitespace-tolerant.
# Patterns are intentionally conservative: false positives are preferred over
# false negatives (fail closed).
# ---------------------------------------------------------------------------

FORBIDDEN_PATTERNS: list[ForbiddenConclusion] = [
    # --- AUTO_CONVICT: treating statements as proof of guilt ---
    ForbiddenConclusion(
        category="AUTO_CONVICT",
        pattern=r"被告.{0,6}自白.{0,6}(?:犯罪成立|有罪|構成)",
        description="自白不等於犯罪成立，必須有客觀補強證據",
    ),
    ForbiddenConclusion(
        category="AUTO_CONVICT",
        pattern=r"犯罪嫌疑人.{0,6}(?:有罪|犯罪成立|應移送)",
        description="嫌疑階段不得宣稱有罪或應移送",
    ),
    ForbiddenConclusion(
        category="AUTO_CONVICT",
        pattern=r"(?:已|已確|確定).{0,4}(?:定罪|犯罪成立|有罪)",
        description="未經司法程序不得宣稱定罪",
    ),
    # --- KEYWORD_TO_CRIME: equating keyword with crime ---
    ForbiddenConclusion(
        category="KEYWORD_TO_CRIME",
        pattern=r"(?:竊取|偷竊|拿走).{0,10}(?:構成|成立).{0,6}竊盜",
        description="『竊取』是當事人說法，不等於竊盜罪成立",
    ),
    ForbiddenConclusion(
        category="KEYWORD_TO_CRIME",
        pattern=r"(?:詐騙|欺騙).{0,10}(?:構成|成立).{0,6}詐欺",
        description="『詐騙』是當事人說法，不等於詐欺罪成立",
    ),
    ForbiddenConclusion(
        category="KEYWORD_TO_CRIME",
        pattern=r"關鍵字.{0,6}命中.{0,6}(?:構成|成立|有罪)",
        description="關鍵字命中不等於構成犯罪",
    ),
    # --- DENIAL_EQUALS_EXCLUSION: treating denial as exclusion ---
    ForbiddenConclusion(
        category="DENIAL_EQUALS_EXCLUSION",
        pattern=r"被告.{0,6}否認.{0,10}(?:排除|不構成|無罪)",
        description="否認不等於事實不存在或犯罪不成立",
    ),
    ForbiddenConclusion(
        category="DENIAL_EQUALS_EXCLUSION",
        pattern=r"未.{0,4}供述.{0,10}(?:排除|不構成|無罪)",
        description="未供述不等於排除犯罪可能",
    ),
    # --- CONFESSION_WITHOUT_CORROBORATION ---
    ForbiddenConclusion(
        category="CONFESSION_WITHOUT_CORROBORATION",
        pattern=r"自白.{0,10}(?:即可|足以|直接).{0,6}(?:認定|定罪|移送)",
        description="自白必須有客觀補強證據，不得單獨認定",
    ),
]


def scan_forbidden_conclusions(text: str) -> list[dict[str, str]]:
    """Scan text for forbidden conclusion patterns.

    Returns a list of violation dicts, each with:
      - category: violation category
      - pattern: the matched pattern
      - description: human-readable explanation
      - matched_text: the actual matched substring
      - severity: BLOCK or WARN

    Empty list = no violations.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    violations: list[dict[str, str]] = []
    for fc in FORBIDDEN_PATTERNS:
        for match in re.finditer(fc.pattern, text, re.IGNORECASE):
            violations.append({
                "category": fc.category,
                "pattern": fc.pattern,
                "description": fc.description,
                "matched_text": match.group(0),
                "severity": fc.severity,
            })
    return violations


def has_blocking_violation(text: str) -> bool:
    """Return True if text contains any BLOCK-severity forbidden conclusion."""
    violations = scan_forbidden_conclusions(text)
    return any(v["severity"] == "BLOCK" for v in violations)


def assert_no_forbidden_conclusions(text: str, context: str = "") -> None:
    """Raise ValueError if text contains blocking forbidden conclusions."""
    violations = scan_forbidden_conclusions(text)
    blocking = [v for v in violations if v["severity"] == "BLOCK"]
    if blocking:
        details = "; ".join(v["description"] for v in blocking)
        raise ValueError(
            f"FORBIDDEN_CONCLUSION [{context}]: {details}"
        )