# 刑事偵查輔助系統 - Migration 遷移執行計畫 (MIGRATION_PLAN.md)

- **版本**: v2.0-DB
- **前置狀態**: 本機檔案完成，未連線正式或測試資料庫 (純離線交付)

---

## 一、遷移檔案依序清單 (Migration Sequence)

所有 Migration 檔案存放於 `database/migrations/`，檔名具備前綴排序，必須嚴格依序套用：

| 序號 | 檔案名稱 | 核心內容與建置對象 | 相依性 |
| :---: | :--- | :--- | :--- |
| **0001** | `0001_extensions_enums.sql` | `uuid-ossp`, `pgcrypto` 擴充套件，所有狀態與流程 Enums | 無 |
| **0002** | `0002_identity_cases.sql` | `user_roles`, `users`, `user_sessions`, `cases`, `case_revisions` | 0001 |
| **0003** | `0003_facts_evidence.sql` | `facts`, `fact_relations`, `evidence_items`, `evidence_sources`, `behaviors` | 0002 |
| **0004** | `0004_analysis_legal.sql` | `statute_references`, `precedent_references`, `legal_candidates`, `constituent_elements`, `element_fact_mappings`, `core_issues` | 0003 |
| **0005** | `0005_interview_workflow.sql`| `interview_sessions`, `interview_questions`, `interview_answers`, `fact_update_logs`, `workflow_stages` | 0004 |
| **0006** | `0006_documents_prompts.sql` | `review_approvals`, `document_outputs`, `llm_prompt_templates` | 0005 |
| **0007** | `0007_integrity_indexes_triggers.sql`| 效能索引、不可竄改觸發器、雜湊校驗、連鎖無效化 (Stale) 觸發器 | 0006 |
| **0008** | `0008_rls_policies.sql` | 啟用 24 表 RLS、工作階段身分判定函式、細部 SELECT/INSERT/UPDATE 政策 | 0007 |
| **0009** | `0009_validation.sql` | 結構驗收函式 `verify_schema_integrity()` 與系統相容性檢查 | 0008 |

---

## 二、部署與執行規範 (Execution Protocol)

### 2.1 執行前置條件 (Preconditions)
1. 目標資料庫必須為 PostgreSQL 15.0 以上版本。
2. 執行帳號必須具有 `SUPERUSER` 或具備建立 Extension 與指定 RLS 之權限。
3. 必須在單一資料庫交易或嚴密監控的階段性交易區塊中執行。

### 2.2 部署指令範例 (待獲授權後之標準執行流程)
```bash
# 循序執行所有 Migration (示範命令，本階段禁止執行)
for file in database/migrations/*.sql; do
    echo "Applying $file..."
    psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f "$file"
done
```

---

## 三、復原與回滾策略 (Rollback Strategy)

若在執行途中發生意外中斷，應採倒序復原（Drop in Reverse Order）：
1. 移除觸發器與 RLS 政策 (`0008`, `0007`)
2. 依序刪除 Documents/Prompts (`0006`), Interview/Workflow (`0005`), Legal Analysis (`0004`), Facts/Evidence (`0003`), Cases/Users (`0002`)
3. 移除 Enums 與擴充 (`0001`)

---

## 四、驗收檢驗項目 (Verification Checklist)

遷移成功後，應透過以下指令驗證：
```sql
SELECT * FROM verify_schema_integrity();
```
驗收標準：
1. 24 張核心業務資料表全數存在。
2. 所有表皆已 `ENABLE ROW LEVEL SECURITY`。
3. 關鍵複合外鍵 `(case_id, revision_id)` 均完整綁定。
4. 鎖定版本保護觸發器正常運作。
