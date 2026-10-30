"""Run the real PostgreSQL acceptance suite with fail-closed safety checks."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from urllib.parse import urlparse

TEST_DATABASE_RE = re.compile(r"^[a-z][a-z0-9_]*_(?:test|disposable|staging)$")


def connection_fingerprint(value: str) -> tuple[str, str, int, str, str]:
    parsed = urlparse(value)
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower()
    port = parsed.port or 5432
    database = parsed.path.rsplit("/", 1)[-1].lower()
    user = parsed.username or ""
    return scheme, host, port, database, user


def safe_test_url(value: str) -> bool:
    scheme, host, _port, database, _user = connection_fingerprint(value)
    return scheme in {"postgres", "postgresql"} and bool(host) and bool(TEST_DATABASE_RE.fullmatch(database))


def validate_urls(url: str, provisioning_url: str, app_url: str) -> tuple[bool, str]:
    values = [url, provisioning_url, app_url]
    if not all(safe_test_url(value) for value in values):
        return False, "all URLs must target a database ending in _test, _disposable or _staging"
    fingerprints = [connection_fingerprint(value) for value in values]
    if len({fingerprint[:4] for fingerprint in fingerprints}) != 1:
        return False, "migration, app and provisioner URLs must share host, port and database"
    users = [fingerprint[4] for fingerprint in fingerprints]
    if users[1:] != ["judicial3_provisioner_login", "judicial3_app"]:
        return False, "provisioner and app URLs must use their dedicated login roles"
    if len(set(users)) != 3:
        return False, "migration, app and provisioner session users must be distinct"
    for production_name in ("DATABASE_URL", "MIGRATION_DATABASE_URL"):
        production_url = os.getenv(production_name)
        if production_url and any(value == production_url for value in values):
            return False, f"test URL must not equal {production_name}"
    return True, "safe isolated target"


def run_suite(env: dict[str, str]) -> int:
    executable = "npx.cmd" if os.name == "nt" else "npx"
    try:
        result = subprocess.run(
            [executable, "tsx", "tools/postgres_acceptance.ts"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=600,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        print(f"BLOCKED PostgreSQL acceptance could not execute: {type(error).__name__}")
        print("PASS=0 FAIL=0 NOT_RUN=0 BLOCKED=1 EXIT_CODE=2 FINAL_STATUS=BLOCKED")
        return 2
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr[-4000:], file=sys.stderr)
    return result.returncode


def main() -> int:
    url = os.getenv("JUDICIAL3_TEST_DATABASE_URL")
    provisioning_url = os.getenv("JUDICIAL3_TEST_PROVISIONING_DATABASE_URL")
    app_url = os.getenv("JUDICIAL3_TEST_APP_DATABASE_URL")
    values = [url, provisioning_url, app_url]
    if not any(values):
        env = os.environ.copy()
        env["JUDICIAL3_USE_EMBEDDED_POSTGRES"] = "true"
        return run_suite(env)
    if not all(values):
        print("BLOCKED PostgreSQL acceptance requires all three isolated connection URLs")
        print("PASS=0 FAIL=0 NOT_RUN=0 BLOCKED=1 EXIT_CODE=2 FINAL_STATUS=BLOCKED")
        return 2
    valid, reason = validate_urls(url, provisioning_url, app_url)
    if not valid:
        print(f"BLOCKED PostgreSQL acceptance safety check: {reason}")
        print("PASS=0 FAIL=0 NOT_RUN=0 BLOCKED=1 EXIT_CODE=2 FINAL_STATUS=BLOCKED")
        return 2
    return run_suite(os.environ.copy())


if __name__ == "__main__":
    raise SystemExit(main())
