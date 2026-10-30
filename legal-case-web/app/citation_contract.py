"""Offline Taiwan legal citation contract and parser.

This module is intentionally not imported by the formal case workflow.  It
normalizes citation mentions only; it never decides legal applicability,
candidate offense, or applied legal basis.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Iterable


NORMALIZATION_VERSION = "tw-citation-v1"
PARSE_SUCCESS = "SUCCESS"
PARSE_PARTIAL = "PARTIAL"
PARSE_UNPARSED = "UNPARSED"

APPROVED_LAW_ALIASES: dict[str, str] = {
    "刑法": "中華民國刑法",
    "中華民國刑法": "中華民國刑法",
    "民法": "中華民國民法",
    "中華民國民法": "中華民國民法",
    "行政罰法": "行政罰法",
    "勞動基準法": "勞動基準法",
    "勞基法": "勞動基準法",
}

_DIGITS = {"〇": 0, "零": 0, "○": 0, "０": 0, "一": 1, "二": 2, "兩": 2,
           "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_UNITS = {"十": 10, "百": 100, "千": 1000, "萬": 10000}
_NUM = r"(?:\d+|[〇零○０一二兩三四五六七八九十百千萬]+)"
_LAW = r"(?:[\u4e00-\u9fff]{1,24}法|同法)"
_ATOM_BODY = rf"{_NUM}\s*(?:條(?:\s*之\s*{_NUM})?|之\s*{_NUM}\s*條?)"
_ATOM = rf"(?P<number>{_NUM})\s*(?:條(?:\s*之\s*(?P<sub>{_NUM}))?|之\s*(?P<sub_alt>{_NUM})\s*條?)"
_SEQUENCE = rf"(?P<sequence>{_ATOM_BODY}(?:\s*(?:、|,|，|及|與|或|和|暨|至|到)\s*(?:第\s*)?{_ATOM_BODY})*)"
_MENTION_RE = re.compile(
    rf"(?P<law>{_LAW})?\s*(?:第\s*)?{_SEQUENCE}"
    rf"(?P<qualifiers>(?:\s*第?\s*{_NUM}\s*項)?(?:\s*第?\s*{_NUM}\s*款)?(?:\s*第?\s*{_NUM}\s*目)?)"
)
_ATOM_RE = re.compile(rf"(?:第\s*)?{_ATOM}")
_UNPARSED_RE = re.compile(rf"(?P<raw>{_LAW}\s*第\s*{_NUM}\s*(?:項|款|目))")
_QUALIFIER_RE = re.compile(
    rf"(?:\s*第?\s*(?P<paragraph>{_NUM})\s*項)?"
    rf"(?:\s*第?\s*(?P<item>{_NUM})\s*款)?"
    rf"(?:\s*第?\s*(?P<subitem>{_NUM})\s*目)?"
)


def chinese_number(value: str) -> int | None:
    """Convert Arabic/full-width/Chinese numerals without guessing invalid text."""

    text = str(value or "").strip()
    if not text:
        return None
    if text.isdigit():
        return int(text)
    if all("０" <= char <= "９" for char in text):
        return int(text.translate(str.maketrans("０１２３４５６７８９", "0123456789")))
    total = 0
    current = 0
    seen = False
    for char in text:
        if char in _DIGITS:
            current = _DIGITS[char]
            seen = True
        elif char in _UNITS:
            seen = True
            unit = _UNITS[char]
            total += (current or 1) * unit
            current = 0
        else:
            return None
    if not seen:
        return None
    return total + current


def normalize_law_name(raw: str | None) -> tuple[str | None, str]:
    """Return canonical law name and status; unknown names are not guessed."""

    value = str(raw or "").strip()
    if not value or value == "同法":
        return None, "UNKNOWN"
    canonical = APPROVED_LAW_ALIASES.get(value)
    if canonical:
        return canonical, "APPROVED_ALIAS"
    return None, "UNKNOWN"


@dataclass(frozen=True)
class CitationMention:
    """A textual mention, not an applicability conclusion."""

    mention_id: str
    law_name: str | None
    article_number: int | None
    article_subnumber: int | None
    paragraph_number: int | None
    item_number: int | None
    subitem_number: int | None
    raw_text: str
    source_ref: str
    source_start: int
    source_end: int
    parse_status: str
    law_name_status: str
    normalization_version: str
    mention_type: str = "CITATION_MENTION"
    stance_status: str = "NOT_ANALYZED"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LegalSource:
    """A separately verified source reference; parser output does not create it."""

    law_name: str
    source_version: str
    source_ref: str
    verification_status: str = "UNKNOWN"


@dataclass(frozen=True)
class LegalApplicabilityCandidate:
    """An explicit analysis object, never automatically created by parsing."""

    candidate_id: str
    citation_mention_ids: tuple[str, ...]
    status: str
    reason: str
    fact_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class AppliedLegalBasis:
    """A separately approved/applied legal basis; empty until an authorized step creates it."""

    basis_id: str
    citation_mention_ids: tuple[str, ...]
    source_version: str
    approval_ref: str
    status: str = "HUMAN_REVIEW_REQUIRED"


def _parse_atom(match: re.Match[str]) -> tuple[int | None, int | None]:
    article = chinese_number(match.group("number"))
    sub = chinese_number(match.group("sub") or match.group("sub_alt"))
    return article, sub


def _previous_law(mentions: list[CitationMention], text: str, start: int) -> str | None:
    if not mentions:
        return None
    previous = mentions[-1]
    if previous.law_name and start - previous.source_end <= 80:
        return previous.law_name
    return None


def parse_citations(
    text: str,
    *,
    source_ref: str = "",
    normalization_version: str = NORMALIZATION_VERSION,
) -> list[CitationMention]:
    """Parse citation mentions while preserving raw text and source offsets.

    The parser intentionally does not inspect negation, factual support, or
    offense applicability.  Those remain independent analysis responsibilities.
    """

    if not isinstance(text, str) or not text:
        return []
    mentions: list[CitationMention] = []
    for match in _MENTION_RE.finditer(text):
        raw = match.group(0)
        law_raw = (match.group("law") or "").strip()
        # A connector immediately before a law name (e.g. 「民法第320條與刑法第320條」)
        # may be consumed by the intentionally broad unknown-law pattern.  It is
        # punctuation/context, not part of the law name.
        connector = re.match(r"^[、,，及與或和暨至到]\s*", law_raw)
        connector_len = len(connector.group(0)) if connector else 0
        law_raw = law_raw[connector_len:]
        # Narrative prefixes such as 「依刑法」 or 「本案與刑法」 can also be
        # consumed before a known law suffix.  Strip only when the suffix is
        # an approved alias; unknown law names remain unresolved.
        matched_approved = False
        for approved_name in sorted(APPROVED_LAW_ALIASES, key=len, reverse=True):
            if law_raw.endswith(approved_name):
                connector_len = len(match.group("law") or "") - len(approved_name)
                law_raw = approved_name
                matched_approved = True
                break
        if not matched_approved and law_raw.endswith("同法"):
            connector_len = len(match.group("law") or "") - len("同法")
            law_raw = "同法"
        mention_start = match.start() + connector_len
        raw = text[mention_start:match.end()]
        if law_raw == "同法":
            law_name = _previous_law(mentions, text, match.start())
            law_status = "CONTEXT_RESOLVED" if law_name else "UNKNOWN"
        elif law_raw:
            law_name, law_status = normalize_law_name(law_raw)
        else:
            law_name, law_status = _previous_law(mentions, text, match.start()), "CONTEXT_RESOLVED" if mentions and _previous_law(mentions, text, match.start()) else "UNKNOWN"

        qualifiers = _QUALIFIER_RE.fullmatch(match.group("qualifiers") or "")
        paragraph = chinese_number(qualifiers.group("paragraph")) if qualifiers else None
        item = chinese_number(qualifiers.group("item")) if qualifiers else None
        subitem = chinese_number(qualifiers.group("subitem")) if qualifiers else None
        atom_matches = list(_ATOM_RE.finditer(match.group("sequence")))
        for index, atom in enumerate(atom_matches):
            article, sub = _parse_atom(atom)
            status = PARSE_SUCCESS if law_name and article is not None else PARSE_PARTIAL
            mention_id = f"citation:{len(mentions) + 1:04d}"
            mentions.append(CitationMention(
                mention_id=mention_id,
                law_name=law_name,
                article_number=article,
                article_subnumber=sub,
                paragraph_number=paragraph,
                item_number=item,
                subitem_number=subitem,
                raw_text=raw if index == 0 else atom.group(0),
                source_ref=source_ref,
                source_start=mention_start if index == 0 else match.start() + atom.start(),
                source_end=match.end() if index == 0 else match.start() + atom.end(),
                parse_status=status,
                law_name_status=law_status,
                normalization_version=normalization_version,
            ))
    # A law-like malformed reference must remain observable.  This does not
    # invent an article number; it records the raw span as UNPARSED.
    covered = {(item.source_start, item.source_end) for item in mentions}
    for match in _UNPARSED_RE.finditer(text):
        if any(start <= match.start() < end for start, end in covered):
            continue
        raw = match.group("raw")
        law_raw = raw.split("第", 1)[0].strip()
        law_name, law_status = normalize_law_name(law_raw)
        mentions.append(CitationMention(
            mention_id=f"citation:{len(mentions) + 1:04d}",
            law_name=law_name,
            article_number=None,
            article_subnumber=None,
            paragraph_number=None,
            item_number=None,
            subitem_number=None,
            raw_text=raw,
            source_ref=source_ref,
            source_start=match.start(),
            source_end=match.end(),
            parse_status=PARSE_UNPARSED,
            law_name_status=law_status,
            normalization_version=normalization_version,
        ))
    mentions.sort(key=lambda item: item.source_start)
    return mentions


def parse_to_dicts(text: str, *, source_ref: str = "", normalization_version: str = NORMALIZATION_VERSION) -> list[dict[str, Any]]:
    return [item.to_dict() for item in parse_citations(text, source_ref=source_ref, normalization_version=normalization_version)]


def has_same_citation(left: CitationMention, right: CitationMention) -> bool:
    """Exact structured comparison; does not compare legal applicability."""

    return (
        left.law_name == right.law_name
        and left.article_number == right.article_number
        and left.article_subnumber == right.article_subnumber
        and left.paragraph_number == right.paragraph_number
        and left.item_number == right.item_number
        and left.subitem_number == right.subitem_number
    )


def citation_contract_is_valid(value: dict[str, Any]) -> bool:
    required = {
        "law_name", "article_number", "article_subnumber", "paragraph_number",
        "item_number", "subitem_number", "raw_text", "source_ref", "parse_status",
        "normalization_version",
    }
    return required <= value.keys() and value.get("parse_status") in {
        PARSE_SUCCESS, PARSE_PARTIAL, PARSE_UNPARSED,
    }


# ---------------------------------------------------------------------------
# Citation tuple match (borrowed from judicial-search-tool citation_normalizer)
# ---------------------------------------------------------------------------
# Coarse-to-fine coverage comparison: a lawyer's query citation (often coarse,
# e.g. "刑法第320條") should match a judgment's extracted citation that is more
# specific (e.g. "刑法第320條第1項"), but NOT vice versa.  This prevents
# negation sentences like "本件與刑法第320條無關" from being counted as hits
# when only a string-contains check is used.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Citation:
    """Structured citation tuple for coarse-to-fine coverage comparison.

    Mirrors ``CitationMention`` but is a lightweight value object that can be
    constructed from a lawyer's search keyword (which may be coarse) and from
    a parsed ``CitationMention`` (which may be fine-grained).
    """

    law_name: str | None
    article_number: int | None
    article_subnumber: int | None = None
    paragraph_number: int | None = None
    item_number: int | None = None
    subitem_number: int | None = None

    def as_tuple(self) -> tuple:
        return (
            self.law_name,
            self.article_number,
            self.article_subnumber,
            self.paragraph_number,
            self.item_number,
            self.subitem_number,
        )

    def covers(self, other: "Citation") -> bool:
        """Return True if ``self`` (query) should match ``other`` (reference).

        Law name: if self.law_name is None, law name is unconstrained (lawyer
        did not specify a law).  Otherwise other.law_name must equal self.law_name.
        Article: must be equal (required on both sides).
        Sub/paragraph/item/subitem: if self has a value, other must equal it;
        if self is None, unconstrained (coarse query matches fine reference).
        """
        if self.law_name is not None and other.law_name != self.law_name:
            return False
        if self.article_number is None or other.article_number is None:
            return False
        if self.article_number != other.article_number:
            return False
        for s, o in (
            (self.article_subnumber, other.article_subnumber),
            (self.paragraph_number, other.paragraph_number),
            (self.item_number, other.item_number),
            (self.subitem_number, other.subitem_number),
        ):
            if s is not None and s != o:
                return False
        return True


def mention_to_citation(mention: CitationMention) -> Citation:
    """Convert a parsed ``CitationMention`` into a lightweight ``Citation``."""
    return Citation(
        law_name=mention.law_name,
        article_number=mention.article_number,
        article_subnumber=mention.article_subnumber,
        paragraph_number=mention.paragraph_number,
        item_number=mention.item_number,
        subitem_number=mention.subitem_number,
    )


def citation_covers(query: Citation, reference: Citation) -> bool:
    """Convenience wrapper around ``Citation.covers``."""
    return query.covers(reference)


def parse_legal_keyword(keyword: str) -> Citation | None:
    """Parse a lawyer's keyword like ``刑法第320條`` into a ``Citation``.

    Returns None if the keyword does not look like a legal-article reference
    (e.g. a free-text concept like ``比例原則``).  Callers should fall back to
    a plain keyword path in that case.
    """
    if not isinstance(keyword, str) or not keyword.strip():
        return None
    text = keyword.strip()

    # Reuse the same numeral regex as the mention parser.
    _num = r"(?:\d+|[〇零○０一二兩三四五六七八九十百千萬]+)"

    # Law name: optional, 1-24 CJK chars ending in 法/條例/規則/辦法/細則 or 同法
    law_match = re.search(r"([\u4e00-\u9fff]{1,24}(?:法|條例|規則|辦法|細則)|同法)", text)
    law_raw = law_match.group(1) if law_match else None
    law_name = None
    if law_raw and law_raw != "同法":
        law_name, _status = normalize_law_name(law_raw)
        if law_name is None:
            # Unknown law: keep raw name as-is (do not guess canonical)
            law_name = law_raw
    elif law_raw == "同法":
        law_name = None  # context-dependent; caller must resolve

    # Article number: 第N條 or N條 or N (bare)
    article_match = re.search(rf"第?\s*({_num})\s*條?", text)
    if not article_match:
        return None
    article_raw = article_match.group(1)
    article_num = chinese_number(article_raw)
    if article_num is None or article_num > 9999:
        return None

    # 之 N / -N sub-number
    sub = None
    sub_match = re.search(rf"(?:之|-)\s*({_num})", text)
    if sub_match:
        sub = chinese_number(sub_match.group(1))

    # 項 / 款 / 目
    paragraph = None
    item = None
    subitem = None
    para_match = re.search(rf"第?\s*({_num})\s*項", text)
    if para_match:
        paragraph = chinese_number(para_match.group(1))
    item_match = re.search(rf"第?\s*({_num})\s*款", text)
    if item_match:
        item = chinese_number(item_match.group(1))
    subitem_match = re.search(rf"第?\s*({_num})\s*目", text)
    if subitem_match:
        subitem = chinese_number(subitem_match.group(1))

    return Citation(
        law_name=law_name,
        article_number=article_num,
        article_subnumber=sub,
        paragraph_number=paragraph,
        item_number=item,
        subitem_number=subitem,
    )
