"""Gold dataset loader smoke tests."""

from __future__ import annotations

from app.gold_dataset import load_gold_case, score_hypothesis_coverage


def test_load_and_score_custody_case():
    gold = load_gold_case()
    assert gold["must_not_auto_convict"] is True
    assert gold["contains_case_data"] is False
    score = score_hypothesis_coverage(gold)
    assert score["hypothesis_recall"] == 1.0
    assert "人工" in score["disclaimer"]
