"""High-confidence tracked-file secret scan; reports paths and rule names, never values."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github-token": re.compile(r"\bgh[opsu]_[A-Za-z0-9]{30,}\b"),
    "aws-secret": re.compile(r"(?i)aws_secret_access_key\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{30,}"),
    "render-key": re.compile(r"\brnd_[A-Za-z0-9]{24,}\b"),
    "live-postgres-url": re.compile(r"postgres(?:ql)?://[^\s:'\"]+:[^\s@'\"]{12,}@(?!127\.0\.0\.1|localhost|example\.invalid)"),
}


def tracked_files() -> list[Path]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True)
    return [ROOT / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def main() -> int:
    findings: list[tuple[str, str]] = []
    for path in tracked_files():
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for name, pattern in RULES.items():
            if pattern.search(content):
                findings.append((path.relative_to(ROOT).as_posix(), name))
    if findings:
        for path, rule in findings:
            print(f"SECRET_SCAN_FAIL path={path} rule={rule}")
        return 1
    print("SECRET_SCAN_PASS tracked_files_only high_confidence_rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
