"""Tests for synonym tier management."""

from app.synonym_tiers import SynonymDictionary, SynonymTier


def test_confirmed_variants_only_from_confirmed_tier():
    d = SynonymDictionary()
    d.discover("僱傭", ["雇傭", "僱庸"], corpus_hits=50)
    # candidate tier → not expanded
    assert d.confirmed_variants("僱傭") == ["僱傭"]
    d.approve("僱傭")
    assert d.confirmed_variants("僱傭") == ["僱傭", "雇傭", "僱庸"]


def test_discover_forced_candidate_even_high_hits():
    d = SynonymDictionary()
    entry = d.discover("測試", ["變體"], corpus_hits=100)
    assert entry.tier == SynonymTier.CANDIDATE


def test_discover_zero_hits_rejected():
    d = SynonymDictionary()
    entry = d.discover("假詞", ["假"], corpus_hits=0)
    assert entry.tier == SynonymTier.REJECTED


def test_discover_low_hits_likely_typo():
    d = SynonymDictionary()
    entry = d.discover("錯字", ["錯"], corpus_hits=3)
    assert entry.tier == SynonymTier.LIKELY_TYPO


def test_reject_demotes_candidate():
    d = SynonymDictionary()
    d.discover("詞", ["變"], corpus_hits=10)
    assert d.reject("詞") is True
    assert d.get("詞").tier == SynonymTier.REJECTED


def test_approve_non_candidate_returns_false():
    d = SynonymDictionary()
    d.discover("詞", ["變"], corpus_hits=0)  # rejected
    assert d.approve("詞") is False


def test_candidates_for_review():
    d = SynonymDictionary()
    d.discover("a", ["a1"], corpus_hits=10)
    d.discover("b", ["b1"], corpus_hits=0)
    cands = d.candidates_for_review()
    assert len(cands) == 1
    assert cands[0].term == "a"


def test_roundtrip_serialization():
    d = SynonymDictionary()
    d.discover("僱傭", ["雇傭"], corpus_hits=10)
    d.approve("僱傭")
    data = d.to_dict_list()
    d2 = SynonymDictionary.from_dict_list(data)
    assert d2.confirmed_variants("僱傭") == ["僱傭", "雇傭"]