"""Two-stage LLM scoring (borrowed from judicial-search-tool).

Stage 1 (screening): Use a small char budget (3K) to quickly score each item.
  Only items with score > 0 proceed to Stage 2.

Stage 2 (full-pass): Use a larger char budget (12K) for detailed scoring.
  Produces score, direction, position, excerpt, found_in.

This reduces token cost by ~60% for large candidate sets.
Also includes smart truncate: when text exceeds budget, extract keyword
windows instead of naive truncation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

# Budgets (characters)
SCREENING_BUDGET = 3000
FULL_PASS_BUDGET = 12000
CONTEXT_HEAD = 300
CONTEXT_TAIL = 300
WINDOW_SIZE = 2000


@dataclass
class ScoreResult:
    item_id: str
    score: int  # 0-10
    direction: str  # "support", "oppose", "neutral"
    position: str  # short summary (≤60 chars)
    excerpt: str  # original text excerpt (≤150 chars)
    found_in: str  # which section
    stage: str  # "screening" or "full_pass"
    truncated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def smart_truncate(text: str, budget: int, keywords: list[str] | None = None) -> tuple[str, bool]:
    """Truncate text to fit budget using keyword windows.

    If text fits within budget, return as-is.
    Otherwise, extract windows around keyword hits, preserving head/tail context.

    Returns (truncated_text, was_truncated).
    """
    if len(text) <= budget:
        return text, False

    keywords = keywords or []
    # Find keyword positions
    hits: list[int] = []
    for kw in keywords:
        if not kw:
            continue
        idx = 0
        while True:
            pos = text.find(kw, idx)
            if pos == -1:
                break
            hits.append(pos)
            idx = pos + len(kw)

    if not hits:
        # No keywords found; fall back to head + tail
        head = text[:CONTEXT_HEAD]
        tail = text[-CONTEXT_TAIL:]
        return head + "\n...\n" + tail, True

    # Sort and merge windows
    hits.sort()
    windows: list[tuple[int, int]] = []
    for pos in hits:
        start = max(0, pos - WINDOW_SIZE // 2)
        end = min(len(text), pos + WINDOW_SIZE // 2)
        windows.append((start, end))

    # Merge overlapping windows
    merged: list[tuple[int, int]] = []
    for start, end in windows:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    # Build truncated text
    parts: list[str] = []
    # Head context
    if merged and merged[0][0] > CONTEXT_HEAD:
        parts.append(text[:CONTEXT_HEAD])
        parts.append("...")

    for start, end in merged:
        parts.append(text[start:end])

    # Tail context
    if merged and merged[-1][1] < len(text) - CONTEXT_TAIL:
        parts.append("...")
        parts.append(text[-CONTEXT_TAIL:])

    truncated = "\n".join(parts)
    # Ensure within budget (rough)
    if len(truncated) > budget:
        truncated = truncated[:budget]
    return truncated, True


def should_proceed_to_full_pass(screening_score: int, threshold: int = 0) -> bool:
    """Determine if an item should proceed to full-pass scoring.

    Items with screening_score > threshold proceed.
    """
    return screening_score > threshold


def two_stage_summary(total_items: int, screening_passed: int) -> dict[str, Any]:
    """Summary of two-stage scoring efficiency."""
    if total_items == 0:
        return {"total": 0, "screening_passed": 0, "savings_pct": 0.0}
    savings = (1 - screening_passed / total_items) * 100
    return {
        "total": total_items,
        "screening_passed": screening_passed,
        "full_pass_skipped": total_items - screening_passed,
        "savings_pct": round(savings, 1),
    }