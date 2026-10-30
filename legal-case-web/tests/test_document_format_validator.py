"""Tests for document format validator."""

from app.document_format_validator import (
    has_blocking_failure,
    validate_brief_length,
    validate_page_count,
    validate_required_fields,
    validate_version_binding,
    validate_document,
)


def test_brief_length_ok():
    r = validate_brief_length("短文")
    assert r.passed is True


def test_brief_length_exceeded():
    r = validate_brief_length("a" * 501)
    assert r.passed is False


def test_page_count_ok():
    r = validate_page_count(5)
    assert r.passed is True


def test_page_count_exceeded():
    r = validate_page_count(9)
    assert r.passed is False


def test_required_fields_missing():
    checks = validate_required_fields({}, ["jurisdiction"])
    assert any(not c.passed for c in checks)


def test_required_fields_present():
    checks = validate_required_fields({"jurisdiction": "台北"}, ["jurisdiction"])
    assert all(c.passed for c in checks)


def test_version_binding_ok():
    r = validate_version_binding("v1", "v1", "v1")
    assert r.passed is True


def test_version_binding_mismatch():
    r = validate_version_binding("v1", "v2", "v1")
    assert r.passed is False


def test_validate_document():
    checks = validate_document({"jurisdiction": "台北", "officer": "王"}, brief_text="短", page_count=3)
    assert not has_blocking_failure(checks)


def test_has_blocking_failure():
    checks = [validate_brief_length("a" * 501)]
    assert has_blocking_failure(checks) is True