#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JUDICIAL3 MVP 行為稽核：區分靜態檢查與實際 subprocess 測試。"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
COUNTS = {"PASS": 0, "FAIL": 0, "NOT_RUN": 0}


def result(check_id: str, title: str, status: str, evidence: str = "") -> None:
    COUNTS[status] += 1
    print(f"[{status}] {check_id} {title}")
    if evidence:
        print(f"       {evidence}")


def run_command(check_id: str, title: str, command: list[str], marker: str | None = None, timeout: int = 90) -> None:
    try:
        completed = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
    except FileNotFoundError as exc:
        result(check_id, title, "NOT_RUN", f"依賴不存在: {exc}")
        return
    except subprocess.TimeoutExpired:
        result(check_id, title, "FAIL", "命令逾時")
        return
    output = (completed.stdout or "") + (completed.stderr or "")
    ok = completed.returncode == 0 and (marker is None or marker in output)
    evidence = f"exit={completed.returncode}"
    if not ok:
        evidence += f"; output_tail={output[-500:]}"
    result(check_id, title, "PASS" if ok else "FAIL", evidence)


print("JUDICIAL3 MVP AUDIT")
print(f"root={ROOT}")
print("\n[STATIC] 必要檔案與資料邊界")
for relative in [
    "server.ts",
    "src/server/auth.ts",
    "src/server/databaseService.ts",
    "src/services/legalReasoningEngine.ts",
    "src/types/index.ts",
    "database/migrations/0010_mvp_traceability.sql",
    "tests/mvp_complete_flow.test.ts",
    "tests/api_route_auth.test.ts",
    "docs/MVP_REFERENCE_RESEARCH.md",
    "docs/MVP_GAP_MATRIX.md",
]:
    path = ROOT / relative
    result(f"FILE-{relative.replace('/', '-')}", f"必要檔案存在: {relative}", "PASS" if path.is_file() else "FAIL", str(path))

db_code = (ROOT / "src/server/databaseService.ts").read_text(encoding="utf-8")
auth_code = (ROOT / "src/server/auth.ts").read_text(encoding="utf-8")
engine_code = (ROOT / "src/services/legalReasoningEngine.ts").read_text(encoding="utf-8")
server_code = (ROOT / "server.ts").read_text(encoding="utf-8")
result("STATIC-FACT-EVIDENCE", "Fact 與 Evidence 分離及保存入口", "PASS" if "evidence_items" in db_code and "EvidenceItem" in engine_code else "FAIL")
result("STATIC-OWNER", "案件查詢使用 owner 條件", "PASS" if "lead_investigator_id = $2::UUID" in db_code else "FAIL")
result("STATIC-FAIL-CLOSED", "PGlite 失敗不切 memory fallback", "PASS" if "dbInstance = new PGlite(dbPath)" in db_code and "Persistent store initialization failed" in db_code else "FAIL")
result("STATIC-AUTH-CHAT", "案件內容對話 API 經認證", "PASS" if "app.post('/api/chat', requireApiUser" in server_code else "FAIL")
result("STATIC-TRACE", "要件／問句追溯欄位保存", "PASS" if "constituent_elements" in db_code and "target_fact_refs" in db_code else "FAIL")
result("STATIC-HMAC", "HMAC token 驗證", "PASS" if "timingSafeEqual" in auth_code and "JUDICIAL3_SESSION_SECRET" in auth_code else "FAIL")
result("STATIC-UNKNOWN", "UNKNOWN／DENIED 未被當成 FALSE", "PASS" if "assertion_status === 'UNKNOWN'" in engine_code and "assertion_status === 'DENIED'" in engine_code else "FAIL")

print("\n[BEHAVIOR] 實際執行測試")
bin_dir = ROOT / "node_modules" / ".bin"
tsx = str(bin_dir / ("tsx.exe" if os.name == "nt" else "tsx"))
tsc = str(bin_dir / ("tsc.exe" if os.name == "nt" else "tsc"))
run_command("TEST-TSC", "TypeScript 型別檢查", [tsc, "--noEmit"])
run_command("TEST-SCENARIOS", "既有 14 情境回歸", [tsx, "tests/legal_reasoning_scenarios.test.ts"], "總測試情境數: 14 | 通過: 14 | 失敗: 0")
run_command("TEST-CORRECTIVE", "候選／要件反事實測試", [tsx, "tests/legal_reasoning_corrective.test.ts"], "CORRECTIVE_PASS")
run_command("TEST-AUTH", "API 認證與 owner 測試", [tsx, "tests/api_auth.test.ts"], "API_AUTH_PASS")
run_command("TEST-API-ROUTE", "實際 server route 認證測試", [tsx, "tests/api_route_auth.test.ts"], "API_ROUTE_AUTH_PASS", timeout=120)
run_command("TEST-FLOW", "完整建案保存讀取修訂流程", [tsx, "tests/mvp_complete_flow.test.ts"], "MVP_FLOW_PASS", timeout=120)
run_command("TEST-BUILD", "Production build", ["npm.cmd" if os.name == "nt" else "npm", "run", "build", "--", "--emptyOutDir"], "built in", timeout=120)

print("\nSUMMARY")
print(f"PASS={COUNTS['PASS']} FAIL={COUNTS['FAIL']} NOT_RUN={COUNTS['NOT_RUN']}")
sys.exit(1 if COUNTS["FAIL"] or COUNTS["NOT_RUN"] else 0)
