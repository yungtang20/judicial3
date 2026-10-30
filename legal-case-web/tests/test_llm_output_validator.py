"""Tests for LLM output schema validation."""

from app.llm_output_validator import (
    validate_candidate_output,
    validate_question_output,
    validate_json_output,
)


def test_valid_candidate_output():
    output = {
        "candidates": [
            {"offense_id": "theft", "status": "NEED_REVIEW", "reason": "test", "source_refs": ["s1"]},
        ],
        "source_refs": ["s1"],
    }
    result = validate_candidate_output(output)
    assert result.valid is True
    assert result.errors == []


def test_missing_required_field():
    output = {"candidates": []}
    result = validate_candidate_output(output)
    assert result.valid is False
    assert any("source_refs" in e for e in result.errors)


def test_invalid_status():
    output = {
        "candidates": [{"offense_id": "x", "status": "INVALID", "reason": "r", "source_refs": ["s"]}],
        "source_refs": ["s"],
    }
    result = validate_candidate_output(output)
    assert result.valid is False
    assert any("invalid status" in e for e in result.errors)


def test_forbidden_conclusion_in_reason():
    output = {
        "candidates": [{"offense_id": "x", "status": "NEED_REVIEW", "reason": "被告自白犯罪成立", "source_refs": ["s"]}],
        "source_refs": ["s"],
    }
    result = validate_candidate_output(output)
    assert result.valid is False
    assert any("forbidden conclusion" in e for e in result.errors)


def test_valid_question_output():
    output = {
        "questions": [{"question_text": "時間？", "target_fact": "time", "element_ref": "e1", "source_refs": ["s1"]}],
        "source_refs": ["s1"],
    }
    result = validate_question_output(output)
    assert result.valid is True


def test_validate_json_output_valid():
    ok, data, err = validate_json_output('{"a": 1}')
    assert ok is True
    assert data == {"a": 1}


def test_validate_json_output_invalid():
    ok, data, err = validate_json_output("not json")
    assert ok is False
    assert "parse error" in err.lower() or "JSON" in err