#!/usr/bin/env python3
"""Verify Codex-oriented skill layout: .agents/skills/*/SKILL.md exists and names align."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_SKILLS = ROOT / ".agents" / "skills"
CANONICAL = ROOT / "skills"

REQUIRED = [
    "taiwan-law-mode",
    "search-taiwan-laws",
    "search-taiwan-judgments",
    "evidence-argument-chain",
    "quality-gate",
    "judicial-resource-discovery",
]


def frontmatter_name(text: str) -> str | None:
    m = re.search(r"^name:\s*(\S+)", text, re.M)
    return m.group(1).strip() if m else None


def main() -> int:
    errors: list[str] = []
    if not (ROOT / "AGENTS.md").is_file():
        errors.append("missing root AGENTS.md")
    if not AGENTS_SKILLS.is_dir():
        errors.append("missing .agents/skills/")
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1

    for name in REQUIRED:
        path = AGENTS_SKILLS / name / "SKILL.md"
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        fm = frontmatter_name(text)
        if fm and fm != name:
            errors.append(f"name mismatch in {path}: {fm!r} != {name!r}")

    # playbooks remain under skills/
    playbooks = CANONICAL / "playbooks"
    if not playbooks.is_dir():
        errors.append("missing skills/playbooks/")

    if errors:
        print("FAIL: skill discovery checks")
        for e in errors:
            print(" -", e)
        return 1
    print("PASS: root AGENTS.md and .agents/skills required set present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
