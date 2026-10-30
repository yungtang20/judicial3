"""Legal keyword search variant generator (borrowed from judicial-search-tool).

Generates multiple search variants for a legal article keyword to improve
recall in MCP search.  Handles:
  - Arabic ↔ Chinese numerals (320 ↔ 三百二十)
  - 之 N / -N / .N forms (第172條之1 / 172-1 / 172.1)
  - 項/款/目 suffixes
  - Law name variants (full name ↔ abbreviation)
  - 第 prefix presence/absence

This is an offline utility; it does not make network calls.
"""

from __future__ import annotations

import re
from typing import Any

# Reuse the numeral conversion from citation_contract
from .citation_contract import chinese_number


def _int_to_chinese(n: int) -> str:
    """Convert integer to Chinese numeral (small scale)."""
    if n == 0:
        return "〇"
    if n < 0:
        return "-" + _int_to_chinese(-n)
    digits = "〇一二三四五六七八九"
    if n < 10:
        return digits[n]
    if n < 20:
        return "十" + (digits[n - 10] if n > 10 else "")
    if n < 100:
        tens, ones = divmod(n, 10)
        return digits[tens] + "十" + (digits[ones] if ones else "")
    if n < 1000:
        hundreds, rest = divmod(n, 100)
        tens_str = _int_to_chinese(rest) if rest else ""
        return digits[hundreds] + "百" + tens_str
    if n < 10000:
        thousands, rest = divmod(n, 1000)
        rest_str = _int_to_chinese(rest) if rest else ""
        return digits[thousands] + "千" + rest_str
    return str(n)


def generate_article_variants(article: int, sub: int | None = None) -> list[str]:
    """Generate all common written forms of an article number."""
    chi_a = _int_to_chinese(article)
    variants: list[str] = []

    if sub is None:
        for a in [str(article), chi_a]:
            variants.append(f"第{a}條")
            variants.append(f"{a}條")
    else:
        chi_s = _int_to_chinese(sub)
        for a, s in [(str(article), str(sub)), (chi_a, chi_s),
                     (str(article), chi_s), (chi_a, str(sub))]:
            variants.append(f"第{a}條之{s}")
            variants.append(f"{a}條之{s}")
            variants.append(f"{a}之{s}條")
        variants.append(f"第{article}-{sub}條")
        variants.append(f"{article}-{sub}")

    # Deduplicate preserving order
    seen: set[str] = set()
    result: list[str] = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            result.append(v)
    return result


def generate_paragraph_suffix(paragraph: int | None, item: int | None = None, subitem: int | None = None) -> list[str]:
    """Generate suffix variants for paragraph/item/subitem. Empty string if none."""
    if paragraph is None and item is None and subitem is None:
        return [""]

    def _num_forms(n: int) -> list[str]:
        return [str(n), _int_to_chinese(n)]

    layers: list[list[str]] = [[]]
    if paragraph is not None:
        forms: list[str] = []
        for n in _num_forms(paragraph):
            forms += [f"第{n}項", f"{n}項"]
        layers.append(forms)
    if item is not None:
        forms = []
        for n in _num_forms(item):
            forms += [f"第{n}款", f"{n}款"]
        layers.append(forms)
    if subitem is not None:
        forms = []
        for n in _num_forms(subitem):
            forms += [f"第{n}目", f"{n}目"]
        layers.append(forms)

    # Cartesian product
    result: list[str] = [""]
    for layer in layers[1:]:
        result = [prev + cur for prev in result for cur in layer]
    result = [s for s in result if s]
    result.append("")  # allow bare article without suffix
    seen: set[str] = set()
    final: list[str] = []
    for v in result:
        if v not in seen:
            seen.add(v)
            final.append(v)
    return final


def generate_search_variants(
    law_name: str | None,
    article: int,
    sub: int | None = None,
    paragraph: int | None = None,
    item: int | None = None,
    subitem: int | None = None,
    law_variants: list[str] | None = None,
) -> list[str]:
    """Generate all search variants for a legal article keyword.

    Args:
        law_name: Canonical law name (or None for no law prefix).
        article: Article number.
        sub: Sub-article number (之 N).
        paragraph: Paragraph number (項).
        item: Item number (款).
        subitem: Subitem number (目).
        law_variants: List of law name variants (full + abbreviations). If None, uses [law_name].

    Returns:
        Deduplicated list of search variant strings.
    """
    article_parts = generate_article_variants(article, sub)
    suffix_parts = generate_paragraph_suffix(paragraph, item, subitem)

    if law_variants is None:
        law_variants = [law_name] if law_name else [""]
    elif law_name and law_name not in law_variants:
        law_variants = [law_name] + law_variants

    results: list[str] = []
    for law in law_variants:
        for a in article_parts:
            for s in suffix_parts:
                prefix = f"{law}" if law else ""
                results.append(f"{prefix}{a}{s}")

    seen: set[str] = set()
    final: list[str] = []
    for v in results:
        if v not in seen:
            seen.add(v)
            final.append(v)
    return final


def top_search_variants(variants: list[str], limit: int = 5) -> list[str]:
    """Select top N variants for MCP search (reduce rate-limit pressure).

    Priority: full law name + 第N條 > abbreviation + 第N條 > has digit > shorter.
    """
    def score(v: str) -> tuple:
        has_first_char = "第" in v
        has_digit = any(c.isdigit() for c in v)
        return (
            0 if has_first_char else 1,
            0 if has_digit else 1,
            len(v),
        )
    sorted_variants = sorted(variants, key=score)
    return sorted_variants[:limit]