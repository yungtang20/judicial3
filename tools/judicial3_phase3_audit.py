"""Offline Phase 3 audit.

The audit intentionally separates static evidence from executable test evidence.
It never connects to a production database and never prints secret values.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str]) -> tuple[str, int]:
    if os.name == "nt" and command and command[0] in {"npm", "npx"}:
        command[0] += ".cmd"
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    output_encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    status = "PASS" if completed.returncode == 0 else "FAIL"
    print(f"{label}: {status} exit={completed.returncode}")
    if completed.stdout:
        print(completed.stdout[-2000:].encode(output_encoding, errors="replace").decode(output_encoding, errors="replace"))
    if completed.stderr:
        print(completed.stderr[-2000:].encode(output_encoding, errors="replace").decode(output_encoding, errors="replace"), file=sys.stderr)
    return label, completed.returncode


def static_checks() -> list[tuple[str, bool]]:
    required = [
        "database/migrations/0011_production_auth.sql",
        "database/migrations/0012_phase3_security_hardening.sql",
        "src/server/config.ts",
        "src/server/databaseRuntime.ts",
        "src/server/auth.ts",
        "render.yaml",
        "tests/auth_session_lifecycle.test.ts",
        "tests/database_runtime.test.ts",
        "tests/rls_policy.test.ts",
    ]
    checks: list[tuple[str, bool]] = []
    for rel in required:
        checks.append((f"static file {rel}", (ROOT / rel).is_file()))
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    scripts = package.get("scripts", {})
    checks.extend(
        [
            ("production start uses tsx", scripts.get("start") == "tsx server.ts"),
            ("migration command exists", scripts.get("db:migrate") == "tsx tools/migrate.ts"),
            ("production blueprint has readiness", "healthCheckPath: /api/health/ready" in (ROOT / "render.yaml").read_text(encoding="utf-8")),
            ("production blueprint does not contain secret values", "postgres://" not in (ROOT / "render.yaml").read_text(encoding="utf-8")),
        ]
    )
    for label, ok in checks:
        print(f"{label}: {'PASS' if ok else 'FAIL'}")
    return checks


def main() -> int:
    os.environ.pop("DATABASE_URL", None)
    checks = static_checks()
    failures = sum(not ok for _, ok in checks)
    # The script records runnable checks but does not turn absent local
    # dependencies or external PostgreSQL into a false PASS.
    commands = [
        ("typescript", ["npm", "run", "lint"]),
        ("phase3 tests", ["npm", "test"]),
    ]
    for label, command in commands:
        _, code = run(label, command)
        failures += code != 0
    print("real PostgreSQL: NOT_RUN (requires isolated PostgreSQL test database)")
    print("Render validation: NOT_RUN (no external deployment mutation or credential use)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
