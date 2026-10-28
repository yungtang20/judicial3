"""Read-only comparison adapter for the two candidate-generation pipelines."""
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
STANDARD_FACTS = [
    {"id": "F-OWNERSHIP", "text": "甲表示手機為其所有", "source": "甲陳述", "status": "ASSERTED_NOT_VERIFIED"},
    {"id": "F-PLACEMENT", "text": "甲表示曾將手機暫放在便利商店櫃檯旁", "source": "甲陳述", "status": "ASSERTED_NOT_VERIFIED"},
    {"id": "F-POSSESSION", "text": "手機是否仍在甲的持有範圍：未確認", "source": "待確認事項", "status": "UNKNOWN"},
    {"id": "F-TAKING", "text": "乙承認拿取手機", "source": "乙陳述", "status": "ASSERTED_NOT_VERIFIED"},
    {"id": "F-BELIEF", "text": "乙表示自己以為手機是他人遺留、不要的物品", "source": "乙辯解", "status": "ASSERTED_NOT_VERIFIED"},
    {"id": "F-INTENT", "text": "乙是否具有不法所有意圖：未確認", "source": "待確認事項", "status": "UNKNOWN"},
    {"id": "F-RECOVERY", "text": "手機目前尚未尋獲", "source": "案件結果記載", "status": "ASSERTED_NOT_VERIFIED"},
]
SUMMARY = "。".join(item["text"] for item in STANDARD_FACTS) + "。"
INTAKE = {"event_time": "2026-10-28T10:00:00+08:00", "location": "便利商店櫃檯旁", "summary": SUMMARY, "case_kind": "WITH_VICTIM"}


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _git(cwd: Path, args: list[str]) -> str:
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True)
    return p.stdout.decode("utf-8", "replace").strip() if p.returncode == 0 else "ERROR"


def _metadata(cwd: Path, files: list[str]) -> dict[str, Any]:
    return {"path": str(cwd), "head": _git(cwd, ["rev-parse", "HEAD"]), "branch": _git(cwd, ["branch", "--show-current"]), "status": _git(cwd, ["status", "--short"]), "files": {n: _sha(cwd / n) for n in files if (cwd / n).is_file()}}


def _run(cwd: Path, code: str) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(cwd)
    p = subprocess.run(
        [sys.executable, "-c", code],
        cwd=cwd,
        env=env,
        input=json.dumps(INTAKE, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
    )
    out = p.stdout.decode("utf-8", "replace") if p.stdout else ""
    err = p.stderr.decode("utf-8", "replace") if p.stderr else ""
    if p.returncode:
        return {"execution": "ERROR", "returncode": p.returncode, "stderr": err[-4000:]}
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        return {"execution": "ERROR", "error": str(exc), "stdout_tail": out[-4000:], "stderr": err[-4000:]}


CIA_CODE = r'''
import json, sys
from app.domain import extract_facts, make_case
from app.question_bank import QuestionBank
intake=json.loads(sys.stdin.buffer.read().decode("utf-8"))
facts=extract_facts(intake)
case=make_case(intake, QuestionBank())
print(json.dumps({"execution":"PASS","entry":"app.domain.extract_facts -> make_case -> analyze_candidates","facts":facts,"candidates":case["candidates"]},ensure_ascii=True))
'''

LCW_CODE = r'''
import json, sys
from app.config import QUESTION_BANK_PATH
from app.rules import analyze_gate1, candidate_offenses, classify_candidates, load_bank
intake=json.loads(sys.stdin.buffer.read().decode("utf-8"))
bank=load_bank(QUESTION_BANK_PATH)
gate1=analyze_gate1(intake, use_ai=False)
raw=candidate_offenses(intake["summary"], bank, gate1)
classified=classify_candidates(intake["summary"], bank, gate1)
print(json.dumps({"execution":"PASS","entry":"app.rules.analyze_gate1(use_ai=False) -> candidate_offenses -> classify_candidates","gate1":gate1,"raw_candidates":raw,"classified":classified},ensure_ascii=True))
'''


def _j(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def _candidate_rows(items: list[dict[str, Any]], project: str) -> list[dict[str, Any]]:
    rows = []
    for item in items:
        children = item.get("child_routes", item.get("legal_routes", []))
        rows.append({"id": item.get("candidate_id", item.get("id")), "status": item.get("status"), "score": item.get("score", "N/A"), "eligibility": item.get("candidate_eligibility", "N/A"), "source": "CIA.analyze_candidates" if project == "CIA" else "LCW.candidate_offenses", "supporting": item.get("supporting_facts", item.get("matched_terms", [])), "children": [{"id": c.get("route_id", c.get("id")), "status": c.get("status", c.get("review_status")), "article": c.get("article_no")} for c in children]})
    return rows


def build() -> dict[str, Any]:
    return {
        "schema_version": "legal-trace-diff.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": {"id": "STANDARD_SEMANTIC_FACTS_V1", "facts": STANDARD_FACTS, "summary": SUMMARY},
        "safety": {"network": "NOT_USED", "llm": "NOT_RUN", "database": "NOT_RUN", "http": "NOT_RUN", "formal_logic_modified": False},
        "projects": {
            "CIA": {"metadata": _metadata(CIA, ["app/domain.py", "app/question_bank.py", "data/runtime/question_bank.json"]), "replay": _run(CIA, CIA_CODE)},
            "legal-case-web": {"metadata": _metadata(LCW, ["app/rules.py", "app/workflow.py", "data/question_bank.json"]), "replay": _run(LCW, LCW_CODE)},
        },
        "mapping": {
            "ownership": {"CIA": "NOT_MAPPED", "legal-case-web": "fact_key='' source statement only"},
            "placement": {"CIA": "F-PLACE / FACT from intake location", "legal-case-web": "fact_key='' source statement only"},
            "possession": {"CIA": "UNKNOWN rights/possession gate", "legal-case-web": "fact_key='' source statement only"},
            "taking": {"CIA": "UNKNOWN conduct gate plus narrative", "legal-case-web": "fact_key='' source statement only"},
            "belief": {"CIA": "UNKNOWN mental-state gate plus narrative", "legal-case-web": "fact_key='' source statement only"},
            "intent": {"CIA": "UNKNOWN mental-state gate", "legal-case-web": "fact_key='' source statement only"},
            "recovery": {"CIA": "UNKNOWN result/evidence gate", "legal-case-web": "fact_key='' source statement only"},
        },
    }


def print_terminal(r: dict[str, Any]) -> None:
    print("=== LEGAL-TRACE-DIFF-004 / STANDARD SEMANTIC FACTS ===")
    print("Input facts:", _j(r["input"]["facts"]))
    print("\n=== A. FACT MODEL COMPARISON ===")
    print("| item | CIA | legal-case-web | semantic difference |\n|---|---|---|---|")
    labels = {"ownership": "手機所有權", "placement": "手機放置方式", "possession": "手機是否仍在甲持有範圍", "taking": "乙拿取手機陳述", "belief": "乙對手機狀態認知", "intent": "不法所有意圖", "recovery": "手機是否尋獲"}
    for key, label in labels.items():
        print(f"| {label} | {_j(r['mapping'][key]['CIA'])} | {_j(r['mapping'][key]['legal-case-web'])} | 是（欄位／模型不同） |")
    print("\n=== B. INITIAL CANDIDATES ===")
    for name, project in r["projects"].items():
        replay = project["replay"]
        print(f"\n[{name}] execution={replay.get('execution')} entry={replay.get('entry')}")
        facts = replay.get("facts") if name == "CIA" else replay.get("gate1", {}).get("facts")
        print("facts:", _j(facts or []))
        items = replay.get("candidates") if name == "CIA" else replay.get("raw_candidates")
        for row in _candidate_rows(items or [], name):
            print("candidate:", _j(row))
        if not items:
            print("candidate: []")
        if name == "legal-case-web":
            print("classified:", _j(replay.get("classified", {})))
    print("\n=== C. FIRST SUBSTANTIVE DIFFERENCE ===")
    print("CIA: embezzlement/NEEDS_FACTS/50 from app.domain.analyze_candidates")
    print("legal-case-web: theft/NEED_REVIEW/ELIGIBLE_CANDIDATE from app.rules.candidate_offenses")
    print("first stage: each project's fact conversion completes, then initial candidate generation")
    print("current-snapshot conclusion: FACT; original-output causation: UNKNOWN")
    print("\n=== D. STATUS CONTRACT ===")
    print("CIA NEEDS_FACTS=parent candidate gate; child status is separately NEEDS_FACTS/HUMAN_REVIEW_REQUIRED")
    print("legal-case-web NEED_REVIEW=candidate status; ELIGIBLE_CANDIDATE=route eligibility; review_status=human review")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = build()
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print_terminal(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
