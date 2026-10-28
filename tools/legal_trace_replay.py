"""隔離的候選罪名端到端追蹤器。

本工具只呼叫現有的純函式候選流程，不啟動 HTTP server、不連線資料庫／雲端、
不呼叫 LLM，也不修改正式推理邏輯。兩個專案以獨立 subprocess 執行，避免
同名 ``app`` package 互相污染。預設輸出 JSON 到 stdout；使用 ``--output``
時才寫入指定的本機診斷檔。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CIA = ROOT / "criminal-investigation-assistant"
LCW = ROOT / "legal-case-web"

SUMMARY = (
    "甲將手機放在便利商店櫃檯旁，乙拿取手機離開。乙表示原本以為是他人"
    "遺留、不要的手機。現有資料尚不能確定手機當時是否仍在甲的持有範圍，"
    "以及乙是否具有不法所有意圖。"
)
INTAKE = {
    "event_time": "2026-10-28T10:00:00+08:00",
    "location": "便利商店櫃檯旁",
    "summary": SUMMARY,
    "case_kind": "WITH_VICTIM",
}


def _git(cwd: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode:
        return f"ERROR:{result.stderr.strip()}"
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def metadata(project: Path, files: list[str]) -> dict[str, Any]:
    return {
        "path": str(project),
        "git_head": _git(project, ["rev-parse", "HEAD"]),
        "git_branch": _git(project, ["branch", "--show-current"]),
        "git_status_porcelain": _git(project, ["status", "--short"]),
        "files": {
            name: {"sha256": _sha256(project / name)}
            for name in files
            if (project / name).is_file()
        },
    }


def _run_json(project: Path, code: str) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project)
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=project,
        env=env,
        capture_output=True,
    )
    stdout = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
    stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
    if result.returncode:
        return {
            "execution": "ERROR",
            "returncode": result.returncode,
            "stderr": stderr[-4000:],
            "stdout_tail": stdout[-4000:],
        }
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        return {
            "execution": "ERROR",
            "returncode": result.returncode,
            "error": f"invalid helper JSON: {exc}",
            "stdout_tail": stdout[-4000:],
            "stderr": stderr[-4000:],
        }


CIA_CODE = r'''
import json
from app.domain import make_case
from app.question_bank import QuestionBank

intake = json.loads(__import__("os").environ["TRACE_INTAKE"])
case = make_case(intake, QuestionBank())
print(json.dumps({
    "execution": "PASS",
    "entry": "app.domain.make_case",
    "facts": case.get("facts", []),
    "parties": case.get("parties", []),
    "events": case.get("events", []),
    "candidates": case.get("candidates", []),
    "case_state": case.get("state"),
    "revision": case.get("revision"),
    "llm": {"status": "NOT_RUN", "reason": "make_case path has no LLM call"},
    "database": {"status": "NOT_RUN", "reason": "no store invocation"},
}, ensure_ascii=False))
'''

LCW_CODE = r'''
import json
from app.config import QUESTION_BANK_PATH
from app.rules import classify_candidates, candidate_offenses, load_bank

intake = json.loads(__import__("os").environ["TRACE_INTAKE"])
bank = load_bank(QUESTION_BANK_PATH)
raw = candidate_offenses(intake["summary"], bank)
classified = classify_candidates(intake["summary"], bank)
print(json.dumps({
    "execution": "PASS",
    "entry": "app.rules.candidate_offenses -> app.rules.classify_candidates",
    "raw_candidates": raw,
    "classified": classified,
    "llm": {"status": "NOT_RUN", "reason": "rules-only isolated replay"},
    "database": {"status": "NOT_RUN", "reason": "no store invocation"},
}, ensure_ascii=False))
'''


def run() -> dict[str, Any]:
    cia_meta = metadata(
        CIA,
        ["app/domain.py", "app/question_bank.py", "data/runtime/question_bank.json"],
    )
    lcw_meta = metadata(
        LCW,
        ["app/rules.py", "app/workflow.py", "data/question_bank.json"],
    )
    encoded = json.dumps(INTAKE, ensure_ascii=False)
    cia_env = os.environ.copy()
    cia_env["TRACE_INTAKE"] = encoded
    lcw_env = os.environ.copy()
    lcw_env["TRACE_INTAKE"] = encoded

    def run_with_env(project: Path, code: str, env: dict[str, str]) -> dict[str, Any]:
        old = os.environ.get("TRACE_INTAKE")
        os.environ["TRACE_INTAKE"] = env["TRACE_INTAKE"]
        try:
            return _run_json(project, code)
        finally:
            if old is None:
                os.environ.pop("TRACE_INTAKE", None)
            else:
                os.environ["TRACE_INTAKE"] = old

    return {
        "schema_version": "legal-trace-replay.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "safety": {
            "external_network": "NOT_USED",
            "llm": "NOT_RUN",
            "database": "NOT_RUN",
            "http_server": "NOT_RUN",
            "formal_logic_modified": False,
        },
        "input": {"intake": INTAKE, "input_id": "F2_exact_take_variant"},
        "projects": {
            "criminal_investigation_assistant": {
                "metadata": cia_meta,
                "replay": run_with_env(CIA, CIA_CODE, cia_env),
                "source_entry": {
                    "http": "app/server.py:165-170 Handler.do_POST",
                    "case": "app/domain.py make_case",
                    "candidates": "app/domain.py analyze_candidates",
                    "child_routes": "app/question_bank.py QuestionBank.child_routes",
                    "output": "app/server.py:48-61 public_case",
                },
            },
            "legal_case_web": {
                "metadata": lcw_meta,
                "replay": run_with_env(LCW, LCW_CODE, lcw_env),
                "source_entry": {
                    "http": "app/server.py:793-800 ANALYZE_ROUTE",
                    "candidates": "app/rules.py:2033 candidate_offenses",
                    "classification": "app/rules.py:2463 classify_candidates",
                    "merge": "app/workflow.py:1138-1217",
                    "output": "app/workflow.py:1285-1299 public_case",
                },
            },
        },
        "not_observed": {
            "original_request_id": True,
            "original_api_response": True,
            "original_revision_payload": True,
            "original_prompt_and_model_response": True,
            "original_retrieval_result": True,
            "original_ui_trace": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="write JSON trace to a local file")
    args = parser.parse_args()
    payload = json.dumps(run(), ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
