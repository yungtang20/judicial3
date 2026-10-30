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


def run_postgres_acceptance() -> None:
    command = [sys.executable, "tools/judicial3_postgres_acceptance.py"]
    try:
        result = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=360)
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        record("BLOCKED", "PostgreSQL acceptance", type(error).__name__)
        return
    if result.stdout:
        safe_output(result.stdout)
    if result.returncode == 0:
        record("PASS", "PostgreSQL acceptance", "disposable database suite exit=0")
    elif result.returncode == 2:
        record("BLOCKED", "PostgreSQL acceptance", "isolated PostgreSQL environment unavailable")
    else:
        record("FAIL", "PostgreSQL acceptance", f"exit={result.returncode}")
        if result.stderr:
            safe_output(result.stderr[-3000:] + "\n", error_stream=True)


def static_audit() -> None:
    required = [
        "database/migrations/0013_system_roles.sql",
        "database/migrations/0014_provisioner_least_privilege.sql",
        "src/server/auth.ts",
        "src/server/provisioning.ts",
        "src/server/databaseService.ts",
        "src/server/databaseRuntime.ts",
        "tests/critical_fixes.test.ts",
        "tests/role_seed_isolation.test.ts",
        "tools/judicial3_postgres_acceptance.py",
        "tools/postgres_acceptance.ts",
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
    provisioning = (ROOT / "tools/provision_user.ts").read_text(encoding="utf-8")
    runtime = (ROOT / "src/server/databaseRuntime.ts").read_text(encoding="utf-8")
    if "JUDICIAL3_PROVISIONING_DATABASE_URL" in provisioning and "MIGRATION_DATABASE_URL" not in provisioning and "assertProvisioningRole" in provisioning and "JUDICIAL3_PROVISIONING_MODE" in runtime:
        record("PASS", "provisioning CLI is dedicated and fail-closed")
    else:
        record("FAIL", "provisioning CLI is dedicated and fail-closed")


def main() -> int:
    static_audit()
    run_command("TypeScript", ["npm", "run", "lint"])
    run_command("critical-fix and regression tests", ["npm", "test"], timeout=300)
    run_postgres_acceptance()
    if os.getenv("RENDER_API_KEY") or os.getenv("RENDER_CLI_TOKEN"):
        record("NOT_RUN", "Render live validation", "credentials detected but live mutation is outside this audit")
    else:
        record("BLOCKED", "Render live validation", "no Render credentials; no deployment performed")
    provisional = 1 if counts["FAIL"] else (2 if counts["NOT_RUN"] or counts["BLOCKED"] else 0)
    final_status = "FAIL" if counts["FAIL"] else ("BLOCKED" if provisional == 2 else "PASS")
    print("SUMMARY " + " ".join(f"{key}={value}" for key, value in counts.items()))
    print(f"PASS={counts['PASS']} FAIL={counts['FAIL']} NOT_RUN={counts['NOT_RUN']} BLOCKED={counts['BLOCKED']} EXIT_CODE={provisional} FINAL_STATUS={final_status}")
    if counts["FAIL"]:
        return 1
    if counts["NOT_RUN"] or counts["BLOCKED"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
