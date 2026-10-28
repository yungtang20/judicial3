from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from app.citation_contract import (
    PARSE_PARTIAL,
    citation_contract_is_valid,
    has_same_citation,
    parse_citations,
)


ROOT = Path(__file__).resolve().parents[1]
CITATION_FIXTURE = ROOT / "LEGAL_CITATION_FIXTURE.json"
TRACE_FIXTURE = ROOT / "LEGAL_TRACE_FIXTURE.json"


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _shape(item: dict) -> dict:
    return {key: item.get(key) for key in (
        "law_name", "article_number", "article_subnumber", "paragraph_number",
        "item_number", "subitem_number", "parse_status",
    )}


def test_all_human_authored_citation_fixture_expectations():
    fixture = _load(CITATION_FIXTURE)
    for case in fixture["cases"]:
        parsed = parse_citations(case["input"], source_ref=f"fixture:{case['id']}")
        assert [_shape(item.to_dict()) for item in parsed] == case["expected"], case["id"]
        for item in parsed:
            value = item.to_dict()
            assert citation_contract_is_valid(value)
            assert value["source_ref"] == f"fixture:{case['id']}"
            assert value["raw_text"] in case["input"]


def test_negation_is_preserved_as_unanalyzed_stance():
    parsed = parse_citations("本案與刑法第320條無關。", source_ref="fixture:negation")
    assert len(parsed) == 1
    assert parsed[0].stance_status == "NOT_ANALYZED"
    assert parsed[0].law_name == "中華民國刑法"
    assert parsed[0].raw_text == "刑法第320條"


def test_different_laws_and_paragraphs_are_not_equal():
    civil = parse_citations("民法第320條")[0]
    criminal = parse_citations("刑法第320條")[0]
    paragraph_one = parse_citations("刑法第320條第1項")[0]
    paragraph_two = parse_citations("刑法第320條第2項")[0]
    assert not has_same_citation(civil, criminal)
    assert not has_same_citation(paragraph_one, paragraph_two)


def test_unknown_law_is_partial_and_not_guessed():
    parsed = parse_citations("某法第320條")[0]
    assert parsed.law_name is None
    assert parsed.law_name_status == "UNKNOWN"
    assert parsed.parse_status == PARSE_PARTIAL


def test_malformed_law_like_reference_is_not_silently_dropped():
    parsed = parse_citations("刑法第320項", source_ref="fixture:unparsed")
    assert len(parsed) == 1
    assert parsed[0].parse_status == "UNPARSED"
    assert parsed[0].article_number is None
    assert parsed[0].raw_text == "刑法第320項"


def test_version_change_does_not_overwrite_raw_text():
    fixture = _load(CITATION_FIXTURE)["version_drift"]
    old = parse_citations(fixture["input"], normalization_version=fixture["old_version"])[0]
    new = parse_citations(fixture["input"], normalization_version=fixture["new_version"])[0]
    assert old.raw_text == fixture["raw_text_must_remain"]
    assert new.raw_text == fixture["raw_text_must_remain"]
    assert old.normalization_version != new.normalization_version


def test_case_trace_fixture_preserves_unknowns_and_separates_basis():
    fixture = _load(TRACE_FIXTURE)
    assert fixture["fixture_only"] is True
    assert fixture["analysis_contract"]["llm"] == "NOT_USED"
    assert fixture["analysis_contract"]["database"] == "NOT_USED"
    assert fixture["applied_legal_basis"] == []
    assert any(item["object"] == "UNKNOWN" for item in fixture["facts"])
    assert all(item["readiness_status"] == "NEEDS_FACTS" for item in fixture["candidates"])
    assert all(item["candidate_status"] == "UNRESOLVED" for item in fixture["candidates"])
    assert all(item["fact_gap"] for item in fixture["questions"])
    assert any(item["verification_status"] == "AVAILABLE_UNVERIFIED" for item in fixture["sources"])


def test_case_trace_references_parse_to_expected_citations():
    fixture = _load(TRACE_FIXTURE)
    for candidate in fixture["candidates"]:
        parsed = parse_citations(candidate["legal_citations"][0], source_ref=candidate["candidate_id"])
        assert parsed
        assert all(item.law_name == "中華民國刑法" for item in parsed)
        assert all(item.parse_status == "SUCCESS" for item in parsed)


def test_parser_is_deterministic_for_same_input_and_version():
    text = "依刑法第320條，並依同法第337條。"
    left = [asdict(item) for item in parse_citations(text, source_ref="fixture:deterministic")]
    right = [asdict(item) for item in parse_citations(text, source_ref="fixture:deterministic")]
    assert left == right
