from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.legal_query import LegalQueryRejected, sanitize_legal_query
from app.storage import RevisionStore


def test_deidentified_legal_query_allows_only_locator_fields():
    assert sanitize_legal_query({
        "law_id": "C0000001", "article_no": "320",
        "issue_tags": ["持有關係", "不法所有意圖"], "effective_date": "2026-10-27",
    })["article_no"] == "320"
    with pytest.raises(LegalQueryRejected):
        sanitize_legal_query({"law_id": "C0000001", "article_no": "320", "summary": "甲拿走皮夾"})
    with pytest.raises(LegalQueryRejected):
        sanitize_legal_query({"law_id": "C0000001", "article_no": "320", "issue_tags": ["臺北市中正區虛擬路1號"]})


def test_audit_database_schema_cannot_store_case_text(tmp_path: Path):
    store = RevisionStore(tmp_path / "case.db", tmp_path / "audit.db")
    with sqlite3.connect(store.audit_path) as db:
        columns = {row[1] for row in db.execute("PRAGMA table_info(audit_event)")}
    assert columns == {"audit_id", "command_id", "action", "request_digest", "result_digest", "result_code", "at"}
    assert not columns.intersection({"case_id", "name", "summary", "narrative", "answer", "location"})


def test_audit_listing_exposes_only_hash_metadata(tmp_path: Path):
    store = RevisionStore(tmp_path / "case.db", tmp_path / "audit.db")
    store._audit("command-1", "TEST_ACTION", "a" * 64, "b" * 64, "COMMITTED")
    events = store.list_audit_events()
    assert len(events) == 1
    assert set(events[0]) == {
        "audit_id", "command_id", "action", "request_digest", "result_digest", "result_code", "at",
    }
    assert events[0]["action"] == "TEST_ACTION"


def test_revision_database_has_normalized_core_tables(tmp_path: Path):
    store = RevisionStore(tmp_path / "case.db", tmp_path / "audit.db")
    with sqlite3.connect(store.path) as db:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {
        "case_head", "case_revision", "case_fact", "case_candidate", "element_gap",
        "question_batch", "question_item", "case_answer", "case_number", "gate_approval",
        "source_pack_pin", "command_log", "document_run",
    }.issubset(tables)
