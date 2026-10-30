"""Tests for legal keyword search variant generator."""

from app.search_variants import (
    generate_article_variants,
    generate_paragraph_suffix,
    generate_search_variants,
    top_search_variants,
)


def test_article_variants_basic():
    variants = generate_article_variants(320)
    assert "第320條" in variants
    assert "320條" in variants


def test_article_variants_with_sub():
    variants = generate_article_variants(172, 1)
    assert "第172條之1" in variants
    assert "172-1" in variants or "第172-1條" in variants


def test_paragraph_suffix_basic():
    suffixes = generate_paragraph_suffix(1)
    assert "第1項" in suffixes
    assert "1項" in suffixes


def test_paragraph_suffix_none():
    suffixes = generate_paragraph_suffix(None)
    assert suffixes == [""]


def test_search_variants_with_law():
    variants = generate_search_variants("中華民國刑法", 320)
    assert any("中華民國刑法" in v and "320" in v for v in variants)


def test_search_variants_no_law():
    variants = generate_search_variants(None, 320)
    assert any("320" in v for v in variants)


def test_top_search_variants_limit():
    variants = generate_search_variants("中華民國刑法", 320, paragraph=1)
    top = top_search_variants(variants, limit=3)
    assert len(top) <= 3


def test_deduplication():
    variants = generate_search_variants("中華民國刑法", 320)
    assert len(variants) == len(set(variants))