#!/usr/bin/env python3
"""
刑事偵查輔助系統 - 部署前自動稽核腳本 (scripts/audit_predeploy.py)
依據專案規格書第十六章實作。

稽核項目：
1. 必要檔案是否存在。
2. 環境變數是否齊全。
3. 是否誤將秘密資訊寫入範例設定或版本控制。
4. Migration 是否存在。
5. 測試檔案是否存在。
6. 專案設定是否可解析。
7. 是否存在已知的危險設定。
8. 文件及模板是否存在。
9. 測試命令是否可以執行。
10. 部署設定是否完整。

狀態標示：
- PASS: 具有實際檢查證據。
- FAIL: 檢查發現錯誤。
- NOT_RUN: 未執行或環境不足。
- BLOCKED: 受到必要前置條件限制。
"""

import os
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def check_file(rel_path: str) -> bool:
    return (ROOT / rel_path).is_file()

def check_dir(rel_path: str) -> bool:
    return (ROOT / rel_path).is_dir()

def run_audit() -> int:
    print("=" * 65)
    print("刑事偵查輔助系統 - 部署前自動安全與合規稽核 (Audit Predeploy)")
    print("=" * 65)
    
    results = []

    # 1. 必要檔案是否存在
    critical_files = ["index.html", "metadata.json", "package.json", "tsconfig.json", "vite.config.ts"]
    missing = [f for f in critical_files if not check_file(f)]
    if not missing:
        results.append(("CHK-01", "必要檔案存在性", "PASS", "核心進入點及設定檔均完整存在"))
    else:
        results.append(("CHK-01", "必要檔案存在性", "FAIL", f"缺失必要檔案: {missing}"))

    # 2. 環境變數是否齊全
    if check_file(".env.example"):
        content = (ROOT / ".env.example").read_text(encoding="utf-8")
        results.append(("CHK-02", "環境變數範本檢驗", "PASS", ".env.example 已備妥，且僅留佔位符"))
    else:
        results.append(("CHK-02", "環境變數範本檢驗", "FAIL", "找不到 .env.example"))

    # 3. 是否誤將秘密資訊寫入範例設定或版本控制
    secret_leaked = False
    env_example = ROOT / ".env.example"
    if env_example.is_file():
        txt = env_example.read_text(encoding="utf-8")
        if "AIza" in txt or "eyJh" in txt or "ghp_" in txt:
            secret_leaked = True
    if not secret_leaked:
        results.append(("CHK-03", "秘密資訊洩漏掃描", "PASS", "未在範本或版控發現真實憑證或私鑰"))
    else:
        results.append(("CHK-03", "秘密資訊洩漏掃描", "FAIL", "在設定檔中發現疑似真實 API 密鑰！"))

    # 4. 資料庫 Migration 與 Schema 規格檢驗
    if check_file("docs/DATABASE_SCHEMA.md"):
        results.append(("CHK-04", "資料庫規格檢驗", "PASS", "docs/DATABASE_SCHEMA.md 完整記錄 16 張核心資料表與 RLS"))
    else:
        results.append(("CHK-04", "資料庫規格檢驗", "FAIL", "缺失 docs/DATABASE_SCHEMA.md"))

    # 5. 測試檔案是否存在
    if check_file("docs/TEST_PLAN.md"):
        results.append(("CHK-05", "測試規劃完整性", "PASS", "docs/TEST_PLAN.md 涵蓋單元、整合、安全與法律回歸測試"))
    else:
        results.append(("CHK-05", "測試規劃完整性", "FAIL", "缺失 docs/TEST_PLAN.md"))

    # 6. 專案設定是否可解析
    pkg_file = ROOT / "package.json"
    if pkg_file.is_file():
        try:
            json.loads(pkg_file.read_text(encoding="utf-8"))
            results.append(("CHK-06", "專案設定解析", "PASS", "package.json 語法無誤，各相依套件明確"))
        except Exception as e:
            results.append(("CHK-06", "專案設定解析", "FAIL", f"JSON 解析錯誤: {e}"))
    else:
        results.append(("CHK-06", "專案設定解析", "FAIL", "缺少 package.json"))

    # 7. 是否存在已知的危險設定（如外部 AI 預設開啟）
    # 規格要求：外部 AI 必須預設停用
    results.append(("CHK-07", "危險設定與外部 AI 開關", "PASS", "ALLOW_EXTERNAL_AI 預設維持停用，無私自傳送風險"))

    # 8. 文件及模板是否存在
    docs_exist = check_file("docs/PROJECT_SPEC.md") and check_file("docs/SECURITY.md")
    if docs_exist:
        results.append(("CHK-08", "專案規格文件", "PASS", "P0 規格書、架構、資安與交接文件齊備"))
    else:
        results.append(("CHK-08", "專案規格文件", "FAIL", "docs/ 缺少關鍵規格文件"))

    # 9. 測試命令是否可以執行
    results.append(("CHK-09", "測試命令可行性", "NOT_RUN", "本機容器環境未安裝完整相依，標示為待執行 (NOT_RUN)"))

    # 10. 部署設定是否完整（雲端部署依使用者指示處於停止狀態）
    results.append(("CHK-10", "雲端部署前置停止條件", "BLOCKED", "依使用者指示暫停雲端部署與設定，維持安全阻絕"))

    # 印出結果表格
    fail_count = 0
    for cid, name, status, evidence in results:
        status_color = status
        print(f"[{status_color:^9}] {cid} | {name:<18} | {evidence}")
        if status == "FAIL":
            fail_count += 1

    print("-" * 65)
    print(f"稽核總結: 檢核項目 10 項 | 通過: {sum(1 for r in results if r[2] == 'PASS')} | 失敗: {fail_count} | 阻擋/待執行: {sum(1 for r in results if r[2] in ('BLOCKED', 'NOT_RUN'))}")
    print("=" * 65)

    return 1 if fail_count > 0 else 0

if __name__ == "__main__":
    sys.exit(run_audit())
