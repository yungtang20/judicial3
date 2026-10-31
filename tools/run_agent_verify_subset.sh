#!/usr/bin/env bash
# Subset verification for agent loop + skills discovery (engineering evidence only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "== skill discovery =="
python tools/check_skill_discovery.py
echo "== stage2 + agent_loop unit tests =="
cd legal-case-web
python -m pytest tests/test_stage2_modules.py tests/test_agent_loop.py -q
echo "PASS: agent verify subset (not legal acceptance)"
