"""Parser / retrieval anomaly logging (JSONL, inspired by judicial-search-tool).

Design:
- Append-only JSONL file under ``data/`` (or a caller-specified path).
- Each record captures a structured anomaly (e.g. empty field, single-line
  over-length, unbalanced quotes, missed citation) with enough context to
  diagnose parser edge cases later.
- The file is NEVER read by runtime logic; it is a diagnostic artifact only.
- Failures to write are swallowed (logged to stderr) so anomaly logging can
  never break the main flow.

This module is intentionally dependency-free and side-effect-safe.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ANOMALY_PATH = Path(__file__).resolve().parents[1] / "data" / "parser_anomalies.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_anomaly(
    anomaly_type: str,
    *,
    source_ref: str = "",
    details: dict[str, Any] | None = None,
    path: str | Path | None = None,
) -> None:
    """Append one anomaly record to the JSONL file.

    Parameters
    ----------
    anomaly_type:
        Short machine-readable tag, e.g. ``"empty_field"``, ``"single_line_overlength"``,
        ``"unbalanced_quotes"``, ``"missed_citation"``.
    source_ref:
        Identifier for the source document / case (never raw PII or full text).
    details:
        Arbitrary JSON-serializable context.  Callers must ensure no PII,
        case payload, or full judgment text is included.
    path:
        Override the default anomaly file path (useful for tests).
    """
    target = Path(path) if path is not None else DEFAULT_ANOMALY_PATH
    record = {
        "timestamp": _now_iso(),
        "anomaly_type": anomaly_type,
        "source_ref": source_ref,
        "details": details or {},
    }
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"[anomaly_log] write failed: {exc}", file=sys.stderr)


def read_anomalies(path: str | Path | None = None) -> list[dict[str, Any]]:
    """Read all anomaly records from the JSONL file (diagnostic use only)."""
    target = Path(path) if path is not None else DEFAULT_ANOMALY_PATH
    if not target.exists():
        return []
    records: list[dict[str, Any]] = []
    try:
        with target.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return records


def clear_anomalies(path: str | Path | None = None) -> None:
    """Remove the anomaly file (for test isolation)."""
    target = Path(path) if path is not None else DEFAULT_ANOMALY_PATH
    try:
        if target.exists():
            target.unlink()
    except OSError:
        pass