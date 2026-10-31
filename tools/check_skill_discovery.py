#!/usr/bin/env python3
"""Verify Codex-oriented skill layout: .agents/skills/*/SKILL.md exists and names align.

Also verifies each required skill has a canonical copy under skills/ (skills/ is the
authoritative source; .agents/skills/ is the Codex-discoverable mirror).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_SKILLS = ROOT / ".agents" / "skills"
CANONICAL = ROOT / "skills"

REQUIRED_SKILLS = {
    "taiwan-law-mode": "taiwan-law-mode/SKILL.md",
    "search-taiwan-laws": "atomic/search-taiwan-laws/SKILL.md",
    "search-taiwan-judgments": "atomic/search-taiwan-judgments/SKILL.md",
    "evidence-argument-chain": "atomic/evidence-argument-chain/SKILL.md",
    "quality-gate": "atomic/quality-gate/SKILL.md",
    "judicial-resource-discovery": "judicial-resource-discovery/SKILL.md",
    "verify-and-sediment": "verify-and-sediment/SKILL.md",
}


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

    for name, canonical_rel in REQUIRED_SKILLS.items():
        agents_path = AGENTS_SKILLS / name / "SKILL.md"
        canonical_path = CANONICAL / canonical_rel
        if not agents_path.is_file():
            errors.append(f"missing {agents_path.relative_to(ROOT)}")
        if not canonical_path.is_file():
            errors.append(f"missing canonical {canonical_path.relative_to(ROOT)}")
        text = agents_path.read_text(encoding="utf-8") if agents_path.is_file() else ""
        fm = frontmatter_name(text)
        if fm and fm != name:
            errors.append(f"name mismatch in {agents_path}: {fm!r} != {name!r}")

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
