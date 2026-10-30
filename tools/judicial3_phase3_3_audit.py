"""Phase 3.2.1-3.3 audit with strict separation of local and live evidence."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COUNTS = {key: 0 for key in ("PASS", "FAIL", "BLOCKED", "NOT_RUN")}


def record(status: str, label: str, detail: str = "") -> None:
    COUNTS[status] += 1
    print(f"[{status}] {label}{' :: ' + detail if detail else ''}")


def text(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        record("FAIL", f"required file {path}", "missing")
        return ""
    record("PASS", f"required file {path}")
    return target.read_text(encoding="utf-8")


def command(label: str, args: list[str], expected: set[int] = {0}) -> None:
    try:
        result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=900)
    except (OSError, subprocess.TimeoutExpired) as error:
        record("BLOCKED", label, type(error).__name__)
        return
    record("PASS" if result.returncode in expected else "FAIL", label, f"exit={result.returncode}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--original-worktree", type=Path)
    args = parser.parse_args()

    branch = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True).stdout.strip()
    branch = branch or os.environ.get("GITHUB_HEAD_REF", "") or os.environ.get("GITHUB_REF_NAME", "")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True).stdout.splitlines()
    record("PASS" if branch else "FAIL", "Git branch", branch or "missing")
    record("PASS" if len(head) == 40 else "FAIL", "Git HEAD", head if len(head) == 40 else "invalid")
    record("PASS", "Git dirty status observed", f"entries={len(dirty)}")

    original = args.original_worktree or (Path(os.environ["JUDICIAL3_ORIGINAL_WORKTREE"]) if os.environ.get("JUDICIAL3_ORIGINAL_WORKTREE") else None)
    if original and (original / ".git").exists():
        original_status = subprocess.run(["git", "status", "--porcelain"], cwd=original, text=True, capture_output=True).stdout.splitlines()
        record("PASS", "original worktree protected observation", f"entries={len(original_status)}")
    else:
        record("NOT_RUN", "original worktree protected observation", "explicit path unavailable")

    production = text("render.yaml")
    web_section = production.split("databases:", 1)[0]
    privileged = ("MIGRATION_DATABASE_URL", "JUDICIAL3_PROVISIONING_DATABASE_URL", "preDeployCommand")
    record("PASS" if all(name not in web_section for name in privileged) else "FAIL", "Web service excludes privileged database credentials")
    migration = text("render.migration-runner.yaml")
    record("PASS" if "judicial3-staging-migrator" in migration and "DATABASE_URL" in migration and "JUDICIAL3_PROVISIONING_DATABASE_URL" not in migration else "FAIL", "dedicated migration runner boundary")
    staging = text("render.staging.yaml")
    record("PASS" if "judicial3-staging-web" in staging and "judicial3-staging-db" in staging and all(name not in staging.split("databases:", 1)[0] for name in privileged[:2]) else "FAIL", "staging Blueprint isolation")
    acceptance = text("render.acceptance-runner.yaml")
    record("PASS" if "judicial3-staging-acceptance" in acceptance and "JUDICIAL3_TEST_PROVISIONING_DATABASE_URL" in acceptance and "MIGRATION_DATABASE_URL" not in acceptance else "FAIL", "dedicated acceptance runner boundary")

    for required in (
        "tools/postgres_backup.py", "tools/postgres_restore.py", "tools/render_one_off_job.py",
        "tools/render_deploy_and_wait.py", "tools/staging_browser_acceptance.ts", "tools/secret_scan.py",
        ".github/workflows/ci.yml", ".github/workflows/staging-release.yml",
        ".github/workflows/production-release.yml",
    ):
        text(required)

    if args.ci:
        command("Python syntax", [os.sys.executable, "-m", "py_compile", "tools/judicial3_phase3_3_audit.py", "tools/judicial3_disaster_recovery_audit.py", "tools/postgres_backup.py", "tools/postgres_restore.py", "tools/render_one_off_job.py", "tools/render_deploy_and_wait.py"])
        command("Secret leakage scan", [os.sys.executable, "tools/secret_scan.py"])
        command("Disaster recovery unit tests", [os.sys.executable, "-m", "unittest", "discover", "-s", "tools/tests"])
    else:
        record("NOT_RUN", "repository command suite", "use --ci")

    live = {
        "Render staging web resource": "JUDICIAL3_STAGING_SERVICE_ID",
        "Render staging database resource": "JUDICIAL3_STAGING_DATABASE_ID",
        "Render migration runner resource": "JUDICIAL3_STAGING_MIGRATOR_ID",
        "Render staging HTTPS URL": "JUDICIAL3_STAGING_URL",
        "Render deployed commit": "JUDICIAL3_STAGING_COMMIT_SHA",
    }
    for label, name in live.items():
        value = os.environ.get(name, "")
        valid = value.startswith("https://") if name.endswith("URL") else bool(value)
        record("PASS" if valid else "BLOCKED", label, "evidence supplied" if valid else f"{name} unavailable")
    record("NOT_RUN", "live PostgreSQL role/RLS/provisioning acceptance", "requires staging-only credentials")
    record("NOT_RUN", "live login/session/browser acceptance", "requires deployed staging and test account")
    record("NOT_RUN", "live backup/restore/rollback/monitoring acceptance", "requires approved staging resources")

    final = "FAIL" if COUNTS["FAIL"] else ("BLOCKED" if COUNTS["BLOCKED"] or COUNTS["NOT_RUN"] else "PASS")
    code = 1 if COUNTS["FAIL"] else (2 if COUNTS["BLOCKED"] or COUNTS["NOT_RUN"] else 0)
    print("SUMMARY " + " ".join(f"{key}={value}" for key, value in COUNTS.items()))
    print(f"FINAL_STATUS={final} EXIT_CODE={code}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
