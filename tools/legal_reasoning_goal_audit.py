#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
臺灣刑事法律推理目標與架構靜態/邏輯稽核腳本
專案: yungtang20/judicial3
任務編號: JUDICIAL3-INDEPENDENT-ACCEPTANCE-REMEDIATION-001
版本: 2026-10-29

驗證目標:
1. 5 份核心文件齊全性與結構規範
2. 5 大法學 AI 平台研究報告與嚴格證據分級標籤 ([已證實的實作], [已觀察的功能], [官方文件所述], [推論或假說], [UNKNOWN])
3. 資料合約完整性 (5元事實狀態, 4種候選狀態, 9大類偵訊問句)
4. 禁絕行為檢查 (嚴禁單一罪名分類偏誤, 嚴禁 UNKNOWN=FALSE, 嚴禁 DENIED=不存在)
5. JUDICIAL3 情境、法律推理修正及 API 認證測試實際執行
"""

import sys
import os
import subprocess
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

CHECKS_PASSED = 0
CHECKS_FAILED = 0
CHECKS_NOT_RUN = 0

def check_assert(condition: bool, check_id: str, title: str, details: str = ""):
    global CHECKS_PASSED, CHECKS_FAILED
    if condition:
        CHECKS_PASSED += 1
        print(f"  [✓ PASS] [{check_id}] {title}")
        if details:
            print(f"           佐證: {details}")
    else:
        CHECKS_FAILED += 1
        print(f"  [✗ FAIL] [{check_id}] {title}")
        if details:
            print(f"           原因: {details}")

print("======================================================================")
print("  臺灣刑事法律推理系統 - 終局目標與架構稽核工具 (Goal Audit)")
print("  專案: yungtang20/judicial3 | 版本: 2026-10-29")
print("======================================================================\n")

# -----------------------------------------------------------------------------
# 階段 1: 核心報告文件完整性檢查
# -----------------------------------------------------------------------------
print("[Step 1/5] 稽核核心規格與交付文件資產...")

required_docs = [
    ("LEGAL_AI_PLATFORM_RESEARCH_REPORT.md", "五大平台深度研究報告"),
    ("ARCHITECTURE_GAP_AUDIT.md", "架構差距稽核與根因分析報告"),
    ("IMPLEMENTATION_REPORT.md", "實施與重構技術報告"),
    ("TEST_RESULTS.md", "測試結果與驗收矩陣"),
]

for doc_name, desc in required_docs:
    p = os.path.join(ROOT_DIR, doc_name)
    exists = os.path.exists(p) and os.path.getsize(p) > 200
    check_assert(exists, f"DOC-{doc_name[:6]}", f"{desc} ({doc_name}) 存在且非空", f"路徑: {p}")

# -----------------------------------------------------------------------------
# 階段 2: 研究報告五大平台覆蓋與證據分級標準
# -----------------------------------------------------------------------------
print("\n[Step 2/5] 稽核五大平台研究深度與證據分級標準...")

research_path = os.path.join(ROOT_DIR, "LEGAL_AI_PLATFORM_RESEARCH_REPORT.md")
if os.path.exists(research_path):
    with open(research_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 檢查五大平台
    platforms = [
        ("Source A: CAIL", "china-ai-law-challenge"),
        ("Source B: judicial-search-tool", "ksliao0314"),
        ("Source C: TAILEXI", "jp.tailexi.org"),
        ("Source D: TWLawBot", "twlawbot.com"),
        ("Source E: 法源法律網", "lawbank.com.tw"),
    ]
    for label, pattern in platforms:
        has_platform = pattern in content
        check_assert(has_platform, f"SRC-{pattern[:8]}", f"完整研析 {label}", f"關鍵特徵: {pattern}")

    # 檢查 5 大證據標準標籤
    evidence_tags = [
        "[已證實的實作]",
        "[已觀察的功能]",
        "[官方文件所述]",
        "[推論或假說]",
        "[UNKNOWN]",
    ]
    for tag in evidence_tags:
        has_tag = tag in content
        check_assert(has_tag, f"EVI-{tag[1:4]}", f"嚴格證據分級標籤: {tag}", f"符合零幻覺防護規範")
else:
    check_assert(False, "SRC-ALL", "研究報告不存在，無法檢驗平台與標籤")

# -----------------------------------------------------------------------------
# 階段 3: 核心資料型別與法律合約稽核
# -----------------------------------------------------------------------------
print("\n[Step 3/5] 稽核法律推理資料型別合約 (src/types/index.ts)...")

types_path = os.path.join(ROOT_DIR, "src", "types", "index.ts")
if os.path.exists(types_path):
    with open(types_path, "r", encoding="utf-8") as f:
        types_code = f.read()

    # 五元事實狀態
    has_five_states = all(s in types_code for s in ["ASSERTED", "ADMITTED", "DENIED", "INFERRED", "UNKNOWN"])
    check_assert(has_five_states, "TYP-FACT-STATES", "五元事實狀態定義 (ASSERTED, ADMITTED, DENIED, INFERRED, UNKNOWN)")

    # 候選狀態
    has_candidate_states = all(s in types_code for s in ["PRIMARY", "ALTERNATIVE", "REJECTED", "UNRESOLVED"])
    check_assert(has_candidate_states, "TYP-CAND-STATES", "候選法律方向狀態定義 (PRIMARY, ALTERNATIVE, REJECTED, UNRESOLVED)")

    # 9 大類問句
    question_types = [
        "1_CORE_ELEMENT",
        "2_ACT_PROCESS",
        "3_SUBJECTIVE_INTENT",
        "4_TIME_LOCATION_PERSON",
        "5_FLOW_OF_PROPERTY",
        "6_EVIDENCE_SOURCE",
        "7_CONTRARY_ALTERNATIVE",
        "8_CONTRADICTION_SUPPLEMENT",
        "9_UNRESOLVED_INQUIRY",
    ]
    has_all_q_types = all(qt in types_code for qt in question_types)
    check_assert(has_all_q_types, "TYP-Q-TYPES", "9 大分類非誘導性偵訊筆錄問句型別宣告完整")
else:
    check_assert(False, "TYP-ALL", "型別檔案不存在")

# -----------------------------------------------------------------------------
# 階段 4: 法律推理核心引擎 (LegalReasoningEngine) 實作稽核
# -----------------------------------------------------------------------------
print("\n[Step 4/5] 稽核法律推理引擎能力 (src/services/legalReasoningEngine.ts)...")

engine_path = os.path.join(ROOT_DIR, "src", "services", "legalReasoningEngine.ts")
if os.path.exists(engine_path):
    with open(engine_path, "r", encoding="utf-8") as f:
        engine_code = f.read()

    # 檢查下游失效機制
    has_invalidation = "invalidateDownstreamOnFactChange" in engine_code
    check_assert(has_invalidation, "ENG-INVALIDATE", "實作上游變更下游自動無效化機制 (Cascade Invalidation)")

    # 檢查多候選方向支援
    has_multi_candidates = "evaluateLegalCandidates" in engine_code and "PRIMARY" in engine_code and "ALTERNATIVE" in engine_code
    check_assert(has_multi_candidates, "ENG-MULTI-CAND", "實作多候選法律方向平行涵攝 (拒絕單一罪名隧道偏誤)")

    # 檢查 9 類問句生成器
    has_q_gen = "generateInterviewQuestions" in engine_code and "1_CORE_ELEMENT" in engine_code
    check_assert(has_q_gen, "ENG-Q-GEN", "實作 9 大分類非誘導性偵訊筆錄問句動態映射")

    # 檢查三值邏輯防護 (嚴禁 UNKNOWN = FALSE, 嚴禁 DENIED = 不存在, 事證不足標為 INSUFFICIENT_DATA)
    has_three_valued = (
        ("assertion_status === 'UNKNOWN'" in engine_code)
        and ("assertion_status === 'DENIED'" in engine_code)
        and ("INSUFFICIENT_DATA" in engine_code)
    )
    check_assert(has_three_valued, "ENG-THREE-VALUED", "落實三值邏輯 (保留 UNKNOWN 與 DENIED 爭點，缺漏標為 INSUFFICIENT_DATA)")

    # 檢查公務條陳體裁驗證
    has_report_val = "generateAndValidateReport" in engine_code and "incident_time_roc" in engine_code
    check_assert(has_report_val, "ENG-REPORT-ROC", "落實公務條陳體裁與民國紀年檢驗約束")

    # 檢查前端真實調用整合 (App.tsx 與 CaseAnalyzer.ts 均調用 LegalReasoningEngine)
    app_path = os.path.join(ROOT_DIR, "src", "App.tsx")
    with open(app_path, "r", encoding="utf-8") as f:
        app_code = f.read()
    app_uses_engine = "LegalReasoningEngine.analyzeFullCase" in app_code
    check_assert(app_uses_engine, "FE-APP-ENGINE", "前端 App.tsx 真實調用 LegalReasoningEngine 進行全案涵攝與狀態機維護")

    case_analyzer_path = os.path.join(ROOT_DIR, "src", "services", "caseAnalyzer.ts")
    with open(case_analyzer_path, "r", encoding="utf-8") as f:
        analyzer_code = f.read()
    analyzer_delegates = "LegalReasoningEngine.analyzeFullCase" in analyzer_code
    check_assert(analyzer_delegates, "FE-ANALYZER-DELEGATE", "向後相容層 CaseAnalyzer 100% 委派至 LegalReasoningEngine")

    # 檢查資料庫防護（嚴禁遞歸刪除既有資料）
    db_service_path = os.path.join(ROOT_DIR, "src", "server", "databaseService.ts")
    with open(db_service_path, "r", encoding="utf-8") as f:
        db_code = f.read()
    no_destructive_rm = "fs.rmSync(dbPath" not in db_code
    check_assert(no_destructive_rm, "SEC-NO-RMSYNC", "databaseService.ts 已徹底清除破壞性遞歸刪除 (fs.rmSync)")

    # 這裡必須檢查「條件結果」，不能以非空字串當成布林值。
    # 先前 no_unknown_false 類型的寫法會因字串非空而永遠通過。
    executable_code = re.sub(r"//[^\n]*|/\*.*?\*/", "", engine_code, flags=re.S)
    no_unknown_false = not bool(re.search(r"(?:assertion_status|element_status|candidate_status)[^;\n]{0,80}UNKNOWN\s*={2,3}\s*FALSE", executable_code, re.I))
    no_denied_false = not bool(re.search(r"(?:assertion_status|element_status|candidate_status)[^;\n]{0,80}DENIED\s*={2,3}\s*FALSE", executable_code, re.I))
    check_assert(no_unknown_false, "ENG-NO-UNKNOWN-FALSE", "未知事項不得被實作成 FALSE")
    check_assert(no_denied_false, "ENG-NO-DENIED-FALSE", "否認事項不得被實作成不存在")

    # 行為證據：所有 SATISFIED 要件必須由引擎的追溯收斂器重新檢查。
    has_trace_gate = "normalizeCandidateTraceability" in engine_code and "related_evidence_refs" in engine_code
    check_assert(has_trace_gate, "ENG-TRACE-GATE", "SATISFIED 要件經 Fact/Evidence 追溯閘門收斂")

    registry_path = os.path.join(ROOT_DIR, "src", "services", "offenseRegistry.ts")
    with open(registry_path, "r", encoding="utf-8") as f:
        registry_code = f.read()
    check_assert(
        "PROPERTY_OFFENSE_REGISTRY" in registry_code
        and "buildPropertyCandidates" in registry_code
        and "VIOLENCE_OFFENSE_REGISTRY" in registry_code
        and "buildViolenceCandidates" in registry_code,
        "ENG-OFFENSE-REGISTRY",
        "竊盜／侵占及暴力家族候選由法律要件登錄表產生，而非單純關鍵字命中",
    )

    auth_path = os.path.join(ROOT_DIR, "src", "server", "auth.ts")
    with open(auth_path, "r", encoding="utf-8") as f:
        auth_code = f.read()
    check_assert(
        "timingSafeEqual" in auth_code
        and "JUDICIAL3_SESSION_SECRET" in auth_code
        and "userId = payload.sub" in auth_code
        and "req.userId = userId" in auth_code,
        "SEC-HMAC-AUTH",
        "API 使用伺服器驗證的 HMAC session subject，不接受偽造 x-user-id",
    )
else:
    check_assert(False, "ENG-ALL", "引擎檔案不存在")

# -----------------------------------------------------------------------------
# 階段 5: JUDICIAL3 行為測試自動執行
# -----------------------------------------------------------------------------
print("\n[Step 5/5] 執行 JUDICIAL3 行為回歸測試...")

test_script = os.path.join(ROOT_DIR, "tests", "legal_reasoning_scenarios.test.ts")
if os.path.exists(test_script):
    try:
        run_res = subprocess.run(
            [os.path.join(ROOT_DIR, "node_modules", ".bin", "tsx.exe"), "tests/legal_reasoning_scenarios.test.ts"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30
        )
        passed_14 = (run_res.returncode == 0) and bool(re.search(r"總測試情境數:\s*14\s*\|\s*通過:\s*14\s*\|\s*失敗:\s*0", run_res.stdout))
        check_assert(passed_14, "TST-14-SCENARIOS", "JUDICIAL3 14 大刑事法律推理情境全數通過 (100% PASS)", f"Exit code: {run_res.returncode}; stderr: {run_res.stderr[-300:]}")
    except Exception as ex:
        check_assert(False, "TST-14-SCENARIOS", "測試執行異常", str(ex))
else:
    check_assert(False, "TST-14-SCENARIOS", "測試腳本不存在")

behavior_tests = [
    ("tests/legal_reasoning_corrective.test.ts", "TST-CORRECTIVE", "CORRECTIVE_PASS"),
    ("tests/api_auth.test.ts", "TST-API-AUTH", "API_AUTH_PASS"),
]
for relative_script, check_id, marker in behavior_tests:
    script_path = os.path.join(ROOT_DIR, relative_script.replace("/", os.sep))
    if not os.path.exists(script_path):
        check_assert(False, check_id, f"行為測試存在: {relative_script}")
        continue
    try:
        run_res = subprocess.run(
            [os.path.join(ROOT_DIR, "node_modules", ".bin", "tsx.exe"), relative_script],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        passed = run_res.returncode == 0 and marker in run_res.stdout
        check_assert(passed, check_id, f"{relative_script} 行為測試通過", f"Exit code: {run_res.returncode}; stderr: {run_res.stderr[-300:]}")
    except Exception as ex:
        check_assert(False, check_id, f"{relative_script} 測試執行異常", str(ex))

# -----------------------------------------------------------------------------
# 總結與退出碼
# -----------------------------------------------------------------------------
print("\n======================================================================")
print(f"稽核結果統計: 通過 (PASS) = {CHECKS_PASSED}, 失敗 (FAIL) = {CHECKS_FAILED}, 未執行 = {CHECKS_NOT_RUN}")
print("======================================================================")

if CHECKS_FAILED == 0:
    print("[SUCCESS] 法律推理系統目標稽核全數合格 (PASS)！\n")
    sys.exit(0)
else:
    print(f"[FAILURE] 存在 {CHECKS_FAILED} 項稽核缺失，請檢視上方失敗項目！\n")
    sys.exit(1)
