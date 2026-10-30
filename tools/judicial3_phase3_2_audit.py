"""Phase 3.2 repository audit; external staging evidence is never inferred."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
counts = {name: 0 for name in ("PASS", "FAIL", "BLOCKED", "NOT_RUN")}


def record(status: str, label: str, detail: str = "") -> None:
    counts[status] += 1
    print(f"[{status}] {label}{(' :: ' + detail) if detail else ''}")


def command(label: str, args: list[str], timeout: int = 360) -> None:
    executable = args[0]
    if os.name == "nt" and executable in {"npm", "npx"}:
        args[0] = executable + ".cmd"
    try:
        result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        record("BLOCKED", label, type(error).__name__)
        return
    if result.returncode == 0:
        record("PASS", label, "exit=0")
    elif result.returncode == 2:
        record("BLOCKED", label, "exit=2; explicit NOT_RUN/BLOCKED evidence")
        print((result.stdout + result.stderr)[-4000:])
    else:
        record("FAIL", label, f"exit={result.returncode}")
        print((result.stdout + result.stderr)[-4000:])


def static_checks() -> None:
    required = [
        ".github/workflows/ci.yml", "render.yaml", "package.json",
        "database/migrations/0013_system_roles.sql",
        "database/migrations/0014_provisioner_least_privilege.sql",
        "src/server/databaseRuntime.ts", "src/server/provisioning.ts",
        "tools/provision_user.ts", "tools/judicial3_postgres_acceptance.py",
        "tools/postgres_acceptance.ts", "docs/PHASE3_2_INVENTORY.md",
        "tools/postgres_acceptance_embedded.ts",
        "docs/PHASE3_2_CI_REPORT.md", "docs/PHASE3_2_RENDER_STAGING_REPORT.md",
        "docs/PHASE3_2_POSTGRES_ACCEPTANCE.md", "docs/PHASE3_2_SECURITY_AUDIT.md",
        "docs/PHASE3_2_FINAL_REPORT.md",
    ]
    for rel in required:
        record("PASS" if (ROOT / rel).is_file() else "FAIL", f"required file {rel}")
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    scripts = package.get("scripts", {})
    record("PASS" if all(scripts.get(name) for name in ("lint", "test", "build")) else "FAIL", "package verification scripts")
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for marker in ("pull_request:", "branches: [main]", "npm ci", "npm run lint", "npm test", "npm run build", "phase3_2_audit.py"):
        record("PASS" if marker in workflow else "FAIL", f"CI marker {marker}")
    migration = (ROOT / "database/migrations/0014_provisioner_least_privilege.sql").read_text(encoding="utf-8")
    role_migration = (ROOT / "database/migrations/0013_system_roles.sql").read_text(encoding="utf-8")
    runtime = (ROOT / "src/server/databaseRuntime.ts").read_text(encoding="utf-8")
    provisioning = (ROOT / "src/server/provisioning.ts").read_text(encoding="utf-8")
    for marker in ("judicial3_app", "judicial3_provisioner", "judicial3_provisioner_login", "GRANT INSERT", "REVOKE ALL ON ALL TABLES"):
        record("PASS" if marker in migration or marker in role_migration or marker in provisioning else "FAIL", f"role safety marker {marker}")
    migrate_tool = (ROOT / "tools/migrate.ts").read_text(encoding="utf-8")
    for marker in ("SET ROLE", "RESET ROLE", "JUDICIAL3_PROVISIONING_MODE", "MIGRATION_DATABASE_URL"):
        record("PASS" if marker in runtime or marker in provisioning or marker in migrate_tool else "FAIL", f"runtime isolation marker {marker}")
    render = (ROOT / "render.yaml").read_text(encoding="utf-8")
    record("PASS" if "healthCheckPath: /api/health/ready" in render and "preDeployCommand: npm run db:migrate" in render else "FAIL", "Render build/start/migration/health configuration")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true", help="run repository-local checks for CI")
    args = parser.parse_args()
    branch = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True).stdout.strip()
    branch = branch or os.environ.get("GITHUB_HEAD_REF", "") or os.environ.get("GITHUB_REF_NAME", "")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True).stdout.strip()
    record("PASS" if branch else "FAIL", "git branch", branch or "missing")
    record("PASS" if len(head) == 40 else "FAIL", "git HEAD", head)
    static_checks()
    if args.ci:
        command("Python syntax", [sys.executable, "-m", "py_compile", "tools/judicial3_phase3_2_audit.py"])
        command("embedded/local PostgreSQL acceptance", [sys.executable, "tools/judicial3_postgres_acceptance.py"])
    else:
        record("NOT_RUN", "repository-local commands", "run with --ci or execute commands individually")
    if os.environ.get("JUDICIAL3_RENDER_STAGING_URL") and os.environ.get("RENDER_API_KEY"):
        record("NOT_RUN", "Render staging live validation", "credentials detected; live mutation is not performed by this repository audit")
    else:
        record("BLOCKED", "Render staging live validation", "independent staging URL and non-production credentials are absent")
    status = "FAIL" if counts["FAIL"] else ("BLOCKED" if counts["BLOCKED"] or counts["NOT_RUN"] else "PASS")
    exit_code = 1 if counts["FAIL"] else (2 if counts["BLOCKED"] or counts["NOT_RUN"] else 0)
    print("SUMMARY " + " ".join(f"{key}={value}" for key, value in counts.items()))
    print(f"FINAL_STATUS={status} EXIT_CODE={exit_code}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
