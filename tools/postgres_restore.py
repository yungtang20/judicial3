"""Restore an encrypted backup only into an explicitly disposable database."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from postgres_backup import postgres_environment, sha256


SAFE_DATABASE_SUFFIXES = ("_restore", "_staging", "_disposable", "_test")


def assert_disposable_database(database: str) -> None:
    if not database.lower().endswith(SAFE_DATABASE_SUFFIXES):
        raise RuntimeError("restore target database name is not explicitly disposable")


def run_checked(command: list[str], *, env: dict[str, str] | None = None) -> None:
    result = subprocess.run(command, env=env, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"restore command failed: {Path(command[0]).name} exit={result.returncode}")


def restore(backup: Path, manifest_path: Path) -> None:
    url = os.environ.get("JUDICIAL3_RESTORE_DATABASE_URL", "")
    identity = os.environ.get("JUDICIAL3_BACKUP_AGE_IDENTITY_FILE", "")
    if not url or not identity:
        raise RuntimeError("restore URL and age identity file are required")
    for executable in ("pg_restore", "psql", "age"):
        if not shutil.which(executable):
            raise RuntimeError(f"required executable is unavailable: {executable}")
    pg_env, database = postgres_environment(url)
    assert_disposable_database(database)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("sha256") != sha256(backup) or manifest.get("size_bytes") != backup.stat().st_size:
        raise RuntimeError("backup integrity check failed")
    with tempfile.TemporaryDirectory(prefix="judicial3-restore-") as temporary:
        plain = Path(temporary) / "backup.dump"
        run_checked(["age", "--decrypt", "--identity", identity, "--output", str(plain), str(backup)])
        run_checked(["pg_restore", "--list", str(plain)])
        run_checked(["pg_restore", "--exit-on-error", "--no-owner", "--no-privileges", "--dbname", database, str(plain)], env=pg_env)
        run_checked(["psql", "--no-password", "--tuples-only", "--command", "SELECT COUNT(*) FROM schema_migrations"], env=pg_env)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        restore(args.backup.resolve(), args.manifest.resolve())
        print("RESTORE_PASS target=disposable integrity=verified ledger=queried")
        return 0
    except Exception as error:
        print(f"RESTORE_FAIL reason={type(error).__name__}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
