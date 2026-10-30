"""Run the disposable PostgreSQL acceptance suite without exposing credentials."""

from __future__ import annotations

import os
import subprocess
import sys
from urllib.parse import urlparse


def safe_url_is_test_only(value: str) -> bool:
    parsed = urlparse(value)
    database = parsed.path.rsplit('/', 1)[-1].lower()
    return parsed.scheme in {"postgres", "postgresql"} and any(
        marker in database for marker in ("test", "staging", "sandbox", "disposable")
    )


def main() -> int:
    url = os.getenv("JUDICIAL3_TEST_DATABASE_URL")
    provisioning_url = os.getenv("JUDICIAL3_TEST_PROVISIONING_DATABASE_URL")
    app_url = os.getenv("JUDICIAL3_TEST_APP_DATABASE_URL")
    missing = [name for name, value in {
        "JUDICIAL3_TEST_DATABASE_URL": url,
        "JUDICIAL3_TEST_PROVISIONING_DATABASE_URL": provisioning_url,
        "JUDICIAL3_TEST_APP_DATABASE_URL": app_url,
    }.items() if not value]
    if missing:
        print(f"BLOCKED PostgreSQL acceptance missing variables: {', '.join(missing)}")
        print("PASS=0 FAIL=0 NOT_RUN=0 BLOCKED=1 EXIT_CODE=2 FINAL_STATUS=BLOCKED")
        return 2
    if url == os.getenv("DATABASE_URL") or not safe_url_is_test_only(url):
        print("BLOCKED PostgreSQL acceptance requires an isolated test/staging database URL")
        print("PASS=0 FAIL=0 NOT_RUN=0 BLOCKED=1 EXIT_CODE=2 FINAL_STATUS=BLOCKED")
        return 2
    if not safe_url_is_test_only(provisioning_url) or not safe_url_is_test_only(app_url):
        print("BLOCKED PostgreSQL acceptance role URLs must target test/staging databases")
        print("PASS=0 FAIL=0 NOT_RUN=0 BLOCKED=1 EXIT_CODE=2 FINAL_STATUS=BLOCKED")
        return 2

    env = os.environ.copy()
    env.update({
        "DATABASE_URL": url,
        "JUDICIAL3_TEST_PROVISIONING_DATABASE_URL": provisioning_url,
        "JUDICIAL3_TEST_APP_DATABASE_URL": app_url,
        "JUDICIAL3_DATABASE_ENGINE": "postgres",
        "JUDICIAL3_MIGRATION_MODE": "true",
        "JUDICIAL3_LOAD_TEST_SEED": "false",
        "NODE_ENV": "test",
    })
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
            timeout=300,
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


if __name__ == "__main__":
    raise SystemExit(main())
