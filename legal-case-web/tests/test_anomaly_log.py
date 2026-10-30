"""Tests for anomaly log module."""

import json
from pathlib import Path

from app.anomaly_log import clear_anomalies, log_anomaly, read_anomalies


def test_log_and_read_anomaly(tmp_path: Path):
    path = tmp_path / "anomalies.jsonl"
    clear_anomalies(path)
    log_anomaly("empty_field", source_ref="case-1", details={"field": "facts"}, path=path)
    records = read_anomalies(path)
    assert len(records) == 1
    assert records[0]["anomaly_type"] == "empty_field"
    assert records[0]["source_ref"] == "case-1"
    assert records[0]["details"]["field"] == "facts"


def test_multiple_anomalies_appended(tmp_path: Path):
    path = tmp_path / "anomalies.jsonl"
    clear_anomalies(path)
    log_anomaly("a", path=path)
    log_anomaly("b", path=path)
    records = read_anomalies(path)
    assert len(records) == 2


def test_read_missing_file_returns_empty(tmp_path: Path):
    path = tmp_path / "nonexistent.jsonl"
    assert read_anomalies(path) == []


def test_clear_removes_file(tmp_path: Path):
    path = tmp_path / "anomalies.jsonl"
    log_anomaly("x", path=path)
    assert path.exists()
    clear_anomalies(path)
    assert not path.exists()