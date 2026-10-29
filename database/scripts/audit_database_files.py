#!/usr/bin/env python3
"""
Static Database Audit Script
System: 刑事偵查輔助系統 (Criminal Investigation Analysis System v2.0)
Task: DB-P0-1

Verifies that all required documentation, migration SQL scripts, schemas,
triggers, RLS policies, and test scripts are present and conformant.
Does NOT require an active database connection.
"""

import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

EXPECTED_DOCS = [
    "README.md",
    "ARCHITECTURE.md",
    "DATA_DICTIONARY.md",
    "SECURITY.md",
    "MIGRATION_PLAN.md",
]

EXPECTED_MIGRATIONS = [
    "0001_extensions_enums.sql",
    "0002_identity_cases.sql",
    "0003_facts_evidence.sql",
    "0004_analysis_legal.sql",
    "0005_interview_workflow.sql",
    "0006_documents_prompts.sql",
    "0007_integrity_indexes_triggers.sql",
    "0008_rls_policies.sql",
    "0009_validation.sql",
]

EXPECTED_TABLES = [
    "user_roles", "users", "user_sessions", "cases", "case_revisions",
    "facts", "fact_relations", "evidence_items", "evidence_sources", "behaviors",
    "statute_references", "precedent_references", "legal_candidates", "constituent_elements",
    "element_fact_mappings", "core_issues", "interview_sessions", "interview_questions",
    "interview_answers", "fact_update_logs", "workflow_stages", "review_approvals",
    "document_outputs", "llm_prompt_templates"
]

EXPECTED_ENUMS = [
    "classification_level_enum",
    "fact_status_enum",
    "element_status_enum",
    "candidate_status_enum",
    "source_status_enum",
    "workflow_stage_enum",
    "workflow_status_enum",
    "approval_status_enum",
]

EXPECTED_TESTS = [
    "schema_validation.sql",
    "constraint_tests.sql",
    "version_integrity_tests.sql",
    "rls_positive_tests.sql",
    "rls_negative_tests.sql",
    "test_data.sql",
]

def main():
    print("=" * 70)
    print("  刑事偵查輔助系統 - PostgreSQL 資料庫靜態稽核 (DB-P0-1)")
    print("=" * 70)

    errors = []
    passes = []

    # 1. 檢查核心架構與設計文件
    print("\n[Step 1/5] 檢查架構設計與規格文件...")
    for doc in EXPECTED_DOCS:
        p = BASE_DIR / doc
        if p.is_file() and p.stat().st_size > 100:
            passes.append(f"文件存在且內容充足: {doc} ({p.stat().st_size} bytes)")
        else:
            errors.append(f"缺少文件或內容過短: {doc}")

    # 2. 檢查 Migration 檔案循序性
    print("\n[Step 2/5] 檢查 Migration 檔案清單與可讀性...")
    combined_sql = ""
    for mig in EXPECTED_MIGRATIONS:
        p = BASE_DIR / "migrations" / mig
        if p.is_file():
            content = p.read_text(encoding="utf-8")
            combined_sql += "\n" + content
            passes.append(f"Migration 檔案存在: {mig}")
        else:
            errors.append(f"缺少 Migration 檔案: {mig}")

    # 3. 檢查 24 張核心業務資料表建立語句
    print("\n[Step 3/5] 檢查 24 張核心資料表與 Enums 定義...")
    for tbl in EXPECTED_TABLES:
        pattern = rf"CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?{tbl}\b"
        if re.search(pattern, combined_sql, re.IGNORECASE):
            passes.append(f"資料表宣告驗證通過: {tbl}")
        else:
            errors.append(f"未找到資料表宣告: {tbl}")

    for enm in EXPECTED_ENUMS:
        if enm in combined_sql:
            passes.append(f"列舉型別驗證通過: {enm}")
        else:
            errors.append(f"未找到列舉型別: {enm}")

    # 4. 檢查安全控制：不可竄改觸發器與 RLS
    print("\n[Step 4/5] 檢查安全觸發器、不可竄改性與 RLS 政策...")
    # 檢查 RLS 政策
    for tbl in EXPECTED_TABLES:
        pattern = rf"ALTER\s+TABLE\s+{tbl}\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY"
        if re.search(pattern, combined_sql, re.IGNORECASE):
            passes.append(f"RLS 啟用設定驗證通過: {tbl}")
        else:
            errors.append(f"資料表未啟用 RLS: {tbl}")

    # 檢查觸發器
    if "fn_prevent_locked_revision_mutation" in combined_sql:
        passes.append("歷史版本鎖定與不可竄改防護觸發器存在")
    else:
        errors.append("缺少不可竄改防護觸發器: fn_prevent_locked_revision_mutation")

    if "fn_invalidate_downstream_on_fact_change" in combined_sql:
        passes.append("事實更新下游連鎖過期 (STALE) 觸發器存在")
    else:
        errors.append("缺少下游連鎖過期觸發器: fn_invalidate_downstream_on_fact_change")

    # 5. 檢查測試套件檔案
    print("\n[Step 5/5] 檢查測試套件 SQL 檔案...")
    for tst in EXPECTED_TESTS:
        p = BASE_DIR / "tests" / tst
        if p.is_file() and p.stat().st_size > 50:
            passes.append(f"測試檔案存在: {tst}")
        else:
            errors.append(f"缺少測試檔案: {tst}")

    print("\n" + "=" * 70)
    print(f"稽核結果統計: 通過項目 = {len(passes)}, 缺失項目 = {len(errors)}")
    print("=" * 70)

    if errors:
        print("\n[ERROR] 發現以下不符項目:")
        for err in errors:
            print(f"  ❌ {err}")
        return 1

    print("\n[SUCCESS] 所有靜態驗證項目全數通過 (PASS)！")
    print("注意: 由於本任務禁止連線實體資料庫，實體資料庫執行測試依規範標記為 NOT_RUN。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
