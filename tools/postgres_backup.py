"""Create a verified, encrypted PostgreSQL custom-format backup without logging credentials."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse


def postgres_environment(url: str) -> tuple[dict[str, str], str]:
    parsed = urlparse(url)
    if parsed.scheme not in {"postgres", "postgresql"} or not parsed.hostname or not parsed.path.strip("/"):
        raise ValueError("backup database URL is invalid")
    database = parsed.path.strip("/")
    env = os.environ.copy()
    env.update({
        "PGHOST": parsed.hostname,
        "PGPORT": str(parsed.port or 5432),
        "PGDATABASE": database,
        "PGUSER": unquote(parsed.username or ""),
        "PGPASSWORD": unquote(parsed.password or ""),
        "PGSSLMODE": "require" if parsed.hostname not in {"127.0.0.1", "localhost"} else "prefer",
    })
    return env, database


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def backup_name(database: str, now: datetime | None = None) -> str:
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    safe = "".join(char if char.isalnum() or char in "-_" else "_" for char in database)
    return f"judicial3-{safe}-{stamp}.dump.age"


def run_checked(command: list[str], *, env: dict[str, str] | None = None) -> None:
    result = subprocess.run(command, env=env, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"backup command failed: {Path(command[0]).name} exit={result.returncode}")


def create_backup(output_dir: Path) -> tuple[Path, Path]:
    url = os.environ.get("JUDICIAL3_BACKUP_DATABASE_URL", "")
    recipient = os.environ.get("JUDICIAL3_BACKUP_AGE_RECIPIENT", "")
    if not url or not recipient:
        raise RuntimeError("JUDICIAL3_BACKUP_DATABASE_URL and JUDICIAL3_BACKUP_AGE_RECIPIENT are required")
    for executable in ("pg_dump", "pg_restore", "age"):
        if not shutil.which(executable):
            raise RuntimeError(f"required executable is unavailable: {executable}")
    pg_env, database = postgres_environment(url)
    output_dir.mkdir(parents=True, exist_ok=True)
    final_path = output_dir / backup_name(database)
    manifest_path = final_path.with_suffix(final_path.suffix + ".json")
    if final_path.exists() or manifest_path.exists():
        raise RuntimeError("backup target already exists; valid backups are never overwritten")
    with tempfile.TemporaryDirectory(prefix="judicial3-backup-") as temporary:
        plain = Path(temporary) / "backup.dump"
        encrypted = Path(temporary) / final_path.name
        run_checked(["pg_dump", "--format=custom", "--no-password", "--file", str(plain)], env=pg_env)
        run_checked(["pg_restore", "--list", str(plain)])
        run_checked(["age", "--recipient", recipient, "--output", str(encrypted), str(plain)])
        encrypted.replace(final_path)
    manifest = {
        "format": "postgres-custom+age",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "database_label": database,
        "file": final_path.name,
        "size_bytes": final_path.stat().st_size,
        "sha256": sha256(final_path),
        "remote_upload": "BLOCKED_UNTIL_PROVIDER_AND_CREDENTIALS_APPROVED",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return final_path, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        backup, manifest = create_backup(args.output_dir.resolve())
        print(f"BACKUP_PASS file={backup.name} manifest={manifest.name} encrypted=true")
        return 0
    except Exception as error:
        print(f"BACKUP_FAIL reason={type(error).__name__}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
