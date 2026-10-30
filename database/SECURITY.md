# 刑事偵查輔助系統 - 安全架構與權限防護規格 (SECURITY.md)

- **版本**: v2.0-DB
- **安全標準**: 執法機關刑事偵查敏感資訊防護規範

---

## 1. 身分識別與連線階段驗證 (Authentication & Context)

系統採用「雙重執行環境相容 (Dual-Runtime Compatible)」的資料列安全 (Row-Level Security, RLS) 機制，同時相容於標準自建 PostgreSQL 與 Supabase 託管環境：

### 1.1 會話識別函式 `current_app_user_id()`
在所有 RLS 政策中，均透過自訂核心安全函式判定當前使用者：
```sql
CREATE OR REPLACE FUNCTION current_app_user_id() 
RETURNS UUID AS $$
BEGIN
    -- 1. 優先檢查標準 PostgreSQL Session 設定 (透過 SET LOCAL app.current_user_id = '...')
    IF NULLIF(current_setting('app.current_user_id', true), '') IS NOT NULL THEN
        RETURN current_setting('app.current_user_id', true)::UUID;
    END IF;

    -- 2. 備援檢查 Supabase auth.uid() (若處於 Supabase 執行環境)
    BEGIN
        IF NULLIF(current_setting('request.jwt.claim.sub', true), '') IS NOT NULL THEN
            RETURN current_setting('request.jwt.claim.sub', true)::UUID;
        END IF;
    EXCEPTION WHEN OTHERS THEN
        NULL;
    END;

    -- 3. 若皆未設定則回傳 NULL (RLS 將全面封鎖存取)
    RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
```

---

## 2. 資料列層級安全政策 (Row-Level Security, RLS)

所有涉及案件、事實、證據、法律分析與文書的 24 張資料表全部啟用 RLS (`ALTER TABLE <tbl> ENABLE ROW LEVEL SECURITY;`)，並套用 `FORCE ROW LEVEL SECURITY`。

### 2.1 案件存取控制策略
1. **案件擁有者與主辦人 (`cases`)**:
   - `SELECT`: 僅案件主辦人 (`lead_investigator_id = current_app_user_id()`) 或具備 `ADMIN` / `SUPERVISOR` 權限者可見。
   - `INSERT`: 必須將 `lead_investigator_id` 填寫為當前登入者 `current_app_user_id()`。
   - `UPDATE`: 僅限主辦人更新非封存狀態之案件。
   - `DELETE`: **全面禁止直接 DELETE 案件**；結案僅能透過更新 `is_archived = TRUE` 軟刪除。

2. **版本與子表級聯控制 (`case_revisions`, `facts`, `behaviors` 等)**:
   - 任何案件子表的 `SELECT`, `INSERT`, `UPDATE`, `DELETE` 均透過關聯至 `cases` 表檢驗：
     ```sql
     EXISTS (
       SELECT 1 FROM cases c 
       WHERE c.id = case_id 
         AND c.lead_investigator_id = current_app_user_id()
     )
     ```
   - 跨案件竄改注入攻擊（如嘗試將他人案件 ID 作為外鍵傳入）會直接在 RLS 階段被阻擋，返回 0 筆或拒絕寫入。

---

## 3. 不可竄改性與歷史鎖定 (Immutability & History Protection)

1. **版本快照鎖定 (`case_revisions.is_locked`)**:
   - 當某一審核階段完成，`case_revisions.is_locked` 設為 `TRUE`。
   - 資料庫層級觸發器 `trg_prevent_locked_revision_mutation` 會在任何對已鎖定版本或其所屬子表（`facts`, `behaviors`, `legal_candidates`, `constituent_elements`, `interview_questions`, `document_outputs`）執行 `UPDATE` 或 `DELETE` 時拋出例外：
     ```sql
     RAISE EXCEPTION 'REV_LOCKED_ERR: Revision % is locked and cannot be modified.', OLD.revision_id;
     ```
2. **防止實體刪除 (No Hard Deletes)**:
   - 關鍵稽核表（`case_revisions`, `facts`, `review_approvals`, `fact_update_logs`）禁止非管理者直接實體刪除。
3. **正式條陳防偽 (Human Approval Gate)**:
   - `document_outputs` 具有嚴格 CHECK 約束：
     `CHECK (is_final = FALSE OR (is_final = TRUE AND approval_id IS NOT NULL))`
   - 唯有經由長官正式完成簽核審核紀錄 (`review_approvals.status = 'APPROVED'`)，方可產出正式效力之條陳。

---

## 4. 角色與最小權限矩陣 (RBAC Matrix)

| 權限 / 角色 | LEAD_INVESTIGATOR (主辦偵查官) | REVIEWER (主管/審核長官) | ANALYST (分析員) |
| :--- | :---: | :---: | :---: |
| 建立與管理自己案件 | **ALLOW** | DENY | DENY |
| 編輯事實、證據、行為 | **ALLOW** (未鎖定時) | DENY | **ALLOW** (限指派) |
| 候選罪名與要件分析 | **ALLOW** | DENY | **ALLOW** |
| 擬定與記錄筆錄問答 | **ALLOW** | DENY | DENY |
| 執行階段審核簽核 | DENY | **ALLOW** | DENY |
| 產出正式條陳公文 | **ALLOW** (需審核) | **ALLOW** | DENY |
| 鎖定/解鎖版本 | **ALLOW** (提交時) | **ALLOW** | DENY |
