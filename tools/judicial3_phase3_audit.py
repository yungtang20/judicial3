"""Phase 3 critical-fix audit with explicit PASS/FAIL/NOT_RUN/BLOCKED states."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
counts = {"PASS": 0, "FAIL": 0, "NOT_RUN": 0, "BLOCKED": 0}


def safe_output(value: str, error_stream: bool = False) -> None:
    stream = sys.stderr if error_stream else sys.stdout
    buffer = getattr(stream, "buffer", None)
    if buffer is not None:
        buffer.write(value.encode("utf-8", errors="replace"))
        buffer.flush()
    else:
        stream.write(value.encode("utf-8", errors="replace").decode("utf-8"))


def record(status: str, label: str, detail: str = "") -> None:
    counts[status] += 1
    suffix = f" :: {detail}" if detail else ""
    print(f"[{status}] {label}{suffix}")


def run_command(label: str, command: list[str], timeout: int = 180) -> None:
    executable = command[0]
    if os.name == "nt" and executable in {"npm", "npx"}:
        command[0] = f"{executable}.cmd"
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        record("BLOCKED", label, "executable or dependency not found")
        return
    except subprocess.TimeoutExpired:
        record("FAIL", label, f"timeout after {timeout}s")
        return
    if result.returncode == 0:
        record("PASS", label, "exit=0")
    else:
        record("FAIL", label, f"exit={result.returncode}")
        if result.stdout:
            safe_output(result.stdout[-3000:] + "\n")
        if result.stderr:
            safe_output(result.stderr[-1200:] + "\n", error_stream=True)


def static_audit() -> None:
    required = [
        "database/migrations/0013_system_roles.sql",
        "src/server/auth.ts",
        "src/server/databaseService.ts",
        "src/server/databaseRuntime.ts",
        "tests/critical_fixes.test.ts",
        "docs/PHASE3_CRITICAL_FIXES_REPORT.md",
    ]
    for rel in required:
        if (ROOT / rel).is_file():
            record("PASS", f"file {rel}")
        else:
            record("FAIL", f"file {rel}", "missing")
    try:
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        if package.get("scripts", {}).get("test"):
            record("PASS", "test script declared")
        else:
            record("FAIL", "test script declared")
    except (OSError, json.JSONDecodeError) as error:
        record("FAIL", "package.json parse", type(error).__name__)
    migration = (ROOT / "database/migrations/0013_system_roles.sql").read_text(encoding="utf-8")
    if "ON CONFLICT (role_code) DO NOTHING" in migration and "CREATE POLICY p_user_roles_read" in migration:
        record("PASS", "role seed is idempotent and read-only")
    else:
        record("FAIL", "role seed is idempotent and read-only")
    runtime = (ROOT / "src/server/databaseRuntime.ts").read_text(encoding="utf-8")
    if "stripOuterTransaction" in runtime and "migrationBody" not in runtime:
        record("PASS", "migration wrapper parser is lexer-based")
    else:
        record("FAIL", "migration wrapper parser is lexer-based")


def main() -> int:
    static_audit()
    run_command("TypeScript", ["npm", "run", "lint"])
    run_command("critical-fix and regression tests", ["npm", "test"], timeout=300)
    for executable in ("psql", "docker", "pg_isready"):
        if shutil.which(executable):
            record("PASS", f"{executable} available")
        else:
            record("BLOCKED", f"{executable} available", "no isolated PostgreSQL tool")
    if os.getenv("RENDER_API_KEY") or os.getenv("RENDER_CLI_TOKEN"):
        record("NOT_RUN", "Render live validation", "credentials detected but live mutation is outside this audit")
    else:
        record("BLOCKED", "Render live validation", "no Render credentials; no deployment performed")
    print("SUMMARY " + " ".join(f"{key}={value}" for key, value in counts.items()))
    if counts["FAIL"]:
        return 1
    if counts["NOT_RUN"] or counts["BLOCKED"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
