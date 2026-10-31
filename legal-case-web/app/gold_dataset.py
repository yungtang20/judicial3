"""Load and score offline gold dataset cases (engineering metrics only)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .competing_hypotheses import example_custody_property_set

FIXTURE_DIR = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "gold_dataset"


def load_gold_case(path: Path | None = None) -> dict[str, Any]:
    p = path or (FIXTURE_DIR / "case_custody_vs_theft.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    if data.get("contains_case_data") is True:
        raise ValueError("gold case must not contain real case data")
    return data


def score_hypothesis_coverage(gold: dict[str, Any]) -> dict[str, Any]:
    """Compare example competing set to gold expected ids (smoke metric)."""
    expected = set(gold.get("expected_hypothesis_ids") or [])
    ch = example_custody_property_set()
    got = {h.hypothesis_id for h in ch.hypotheses}
    missing = sorted(expected - got)
    extra = sorted(got - expected)
    recall = 1.0 if not expected else (len(expected & got) / len(expected))
    return {
        "gold_id": gold.get("gold_id"),
        "hypothesis_recall": recall,
        "missing_hypothesis_ids": missing,
        "extra_hypothesis_ids": extra,
        "must_not_auto_convict": bool(gold.get("must_not_auto_convict", True)),
        "disclaimer": "工程指標，非法律正確性證明；須人工審閱。",
    }
