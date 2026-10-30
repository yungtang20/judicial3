"""Tests for citation tuple match (covers) added from judicial-search-tool."""

from app.citation_contract import (
    Citation,
    CitationMention,
    citation_covers,
    mention_to_citation,
    parse_legal_keyword,
)


def test_covers_coarse_query_matches_fine_reference():
    query = Citation(law_name="中華民國刑法", article_number=320)
    ref = Citation(law_name="中華民國刑法", article_number=320, paragraph_number=1)
    assert query.covers(ref) is True


def test_covers_fine_query_does_not_match_coarse_reference():
    query = Citation(law_name="中華民國刑法", article_number=320, paragraph_number=1)
    ref = Citation(law_name="中華民國刑法", article_number=320)
    assert query.covers(ref) is False


def test_covers_different_article_no_match():
    query = Citation(law_name="中華民國刑法", article_number=320)
    ref = Citation(law_name="中華民國刑法", article_number=321)
    assert query.covers(ref) is False


def test_covers_different_law_no_match():
    query = Citation(law_name="中華民國刑法", article_number=320)
    ref = Citation(law_name="中華民國民法", article_number=320)
    assert query.covers(ref) is False


def test_covers_none_law_is_unconstrained():
    query = Citation(law_name=None, article_number=320)
    ref = Citation(law_name="中華民國刑法", article_number=320)
    assert query.covers(ref) is True


def test_covers_paragraph_mismatch_no_match():
    query = Citation(law_name="中華民國刑法", article_number=320, paragraph_number=1)
    ref = Citation(law_name="中華民國刑法", article_number=320, paragraph_number=2)
    assert query.covers(ref) is False


def test_citation_covers_wrapper():
    q = Citation(law_name="中華民國刑法", article_number=320)
    r = Citation(law_name="中華民國刑法", article_number=320, paragraph_number=1)
    assert citation_covers(q, r) is True


def test_mention_to_citation_roundtrip():
    mention = CitationMention(
        mention_id="citation:0001",
        law_name="中華民國刑法",
        article_number=320,
        article_subnumber=None,
        paragraph_number=1,
        item_number=None,
        subitem_number=None,
        raw_text="刑法第320條第1項",
        source_ref="test",
        source_start=0,
        source_end=10,
        parse_status="SUCCESS",
        law_name_status="APPROVED_ALIAS",
        normalization_version="tw-citation-v1",
    )
    cit = mention_to_citation(mention)
    assert cit.law_name == "中華民國刑法"
    assert cit.article_number == 320
    assert cit.paragraph_number == 1


def test_parse_legal_keyword_basic():
    cit = parse_legal_keyword("刑法第320條")
    assert cit is not None
    assert cit.law_name == "中華民國刑法"
    assert cit.article_number == 320


def test_parse_legal_keyword_with_paragraph():
    cit = parse_legal_keyword("刑法第320條第1項")
    assert cit is not None
    assert cit.paragraph_number == 1


def test_parse_legal_keyword_with_sub():
    cit = parse_legal_keyword("刑法第172條之1")
    assert cit is not None
    assert cit.article_subnumber == 1


def test_parse_legal_keyword_free_text_returns_none():
    cit = parse_legal_keyword("比例原則")
    assert cit is None


def test_parse_legal_keyword_empty_returns_none():
    assert parse_legal_keyword("") is None
    assert parse_legal_keyword(None) is None