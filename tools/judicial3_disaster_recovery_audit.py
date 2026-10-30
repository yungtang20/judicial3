"""Non-destructive disaster-recovery evidence audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
counts = {key: 0 for key in ("PASS", "FAIL", "BLOCKED", "NOT_RUN")}


def record(status: str, label: str, detail: str = "") -> None:
    counts[status] += 1
    print(f"[{status}] {label}{' :: ' + detail if detail else ''}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup-manifest", type=Path)
    parser.add_argument("--restore-report", type=Path)
    args = parser.parse_args()
    for rel in (
        "tools/postgres_backup.py", "tools/postgres_restore.py", "tools/tests/test_disaster_recovery.py",
        "docs/PHASE3_3_BACKUP_STRATEGY.md", "docs/PHASE3_3_RESTORE_RUNBOOK.md",
        "docs/PHASE3_3_ROLLBACK_RUNBOOK.md", "docs/PHASE3_3_MONITORING.md",
        "docs/PHASE3_3_DISASTER_RECOVERY_TEST.md",
    ):
        record("PASS" if (ROOT / rel).is_file() else "FAIL", f"required DR artifact {rel}")
    if args.backup_manifest and args.backup_manifest.is_file():
        try:
            data = json.loads(args.backup_manifest.read_text(encoding="utf-8"))
            valid = bool(data.get("sha256")) and data.get("size_bytes", 0) > 0 and data.get("format") == "postgres-custom+age"
            record("PASS" if valid else "FAIL", "executed backup integrity evidence")
        except (OSError, json.JSONDecodeError):
            record("FAIL", "executed backup integrity evidence", "invalid manifest")
    else:
        record("NOT_RUN", "executed backup integrity evidence", "manifest not supplied")
    if args.restore_report and args.restore_report.is_file():
        record("PASS", "executed isolated restore evidence", "report supplied for manual review")
    else:
        record("NOT_RUN", "executed isolated restore evidence", "restore report not supplied")
    record("NOT_RUN", "measured RPO/RTO", "requires successful staging backup and restore timestamps")
    record("NOT_RUN", "application rollback and monitoring alerts", "requires live staging")
    final = "FAIL" if counts["FAIL"] else ("BLOCKED" if counts["BLOCKED"] or counts["NOT_RUN"] else "PASS")
    code = 1 if counts["FAIL"] else (2 if counts["BLOCKED"] or counts["NOT_RUN"] else 0)
    print("SUMMARY " + " ".join(f"{key}={value}" for key, value in counts.items()))
    print(f"FINAL_STATUS={final} EXIT_CODE={code}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
