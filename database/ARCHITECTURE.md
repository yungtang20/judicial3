# 刑事偵查輔助系統 - 資料庫架構與狀態機規格書 (ARCHITECTURE.md)

- **版本**: v2.0-DB
- **架構角色**: 資深 PostgreSQL 架構師 / 安全工程師

---

## 1. 核心實體關聯與版本架構 (ER & Versioning Model)

系統採用「主表指針 + 不可變歷程版本快照 (Master Pointer + Immutable Revision Snapshot)」架構：

```
+-------------------------------------------------------------+
|                          users                              |
|  id (UUID), username, role_id, is_active, security_stamp    |
+------------------------------+------------------------------+
                               |
                               | 1:N (owns)
                               v
+-------------------------------------------------------------+
|                          cases                              |
|  id (UUID), case_number, title, lead_investigator_id,       |
|  current_revision_id (FK -> case_revisions.id DEFERRABLE),  |
|  classification_level, is_archived, created_at              |
+------------------------------+------------------------------+
                               |
                               | 1:N (historical revisions)
                               v
+-------------------------------------------------------------+
|                      case_revisions                         |
|  id (UUID), case_id (FK), revision_number (INT),            |
|  revision_hash (SHA-256), parent_revision_id (FK),          |
|  change_summary, is_locked (BOOLEAN), created_by (FK)       |
+------------------------------+------------------------------+
                               |
                               | 複合外鍵 (case_id, revision_id) 關聯至所有子表
        +----------------------+----------------------+
        |                      |                      |
        v                      v                      v
+---------------+      +---------------+      +---------------+
|     facts     |      |   behaviors   |      |legal_candidate|
+---------------+      +---------------+      +---------------+
        |                      |                      |
        v                      |                      v
+---------------+              |              +---------------+
|evidence_items |              |              |constituent_elm|
+---------------+              |              +---------------+
        |                      |                      |
        +----------------------+                      v
                                              +---------------+
                                              |  core_issues  |
                                              +---------------+
                                                      |
                                                      v
                                              +---------------+
                                              |interview_quest|
                                              +---------------+
                                                      |
                                                      v
                                              +---------------+
                                              |document_output|
                                              +---------------+
```

### 1.1 版本一致性保證 (Revision Snapshot Integrity)
1. **複合外鍵約制**: 案件子表（如 `facts`, `behaviors`, `legal_candidates`）皆包含 `(case_id, revision_id)` 雙鍵，並以複合外鍵參照 `case_revisions(case_id, id)`。此設計防止子表資料跨案件混淆或孤立。
2. **唯讀鎖定機制**: 當 `case_revisions.is_locked = TRUE`（例如已完成階段審核），觸發器 `trg_prevent_locked_revision_mutation` 會直接 `RAISE EXCEPTION`，禁止對該版本及該版本之所有子表進行 `INSERT`, `UPDATE`, `DELETE`。
3. **版本防竄改雜湊**: `case_revisions.revision_hash` 儲存此版本關鍵事實與分析之 SHA-256 數位指紋，由資料庫觸發器或簽核函式校驗，若版本有任何非正規異動即導致校驗失敗。
4. **主表指標延遲更新**: `cases.current_revision_id` 設為 `INITIALLY DEFERRED` 外鍵，允許在同一交易中建立新版本快照後將案件目前指針指向新版本。

---

## 2. 狀態機與約束規範 (State Machines & Constraints)

### 2.1 事實狀態機 (Fact Status)
- 定義: `fact_status_enum`
- 狀態值:
  - `ASSERTED`: 告訴人或證人主觀陳述，尚未有客觀佐證。
  - `ADMITTED`: 犯罪嫌疑人/被告自白或承認之事實。
  - `DENIED`: 犯罪嫌疑人/被告否認之事實（**不可視同客觀事實不存在**）。
  - `INFERRED`: 經由其他事實推論而得之事實。
  - `UNKNOWN`: 待查證事實（**絕對禁止自動視同 FALSE 或否定**）。
- 約束: 必須具有關聯來源或陳述人；若為 `INFERRED`，必須在 `fact_relations` 中存在推論來源依據。

### 2.2 構成要件狀態機 (Constituent Element Status)
- 定義: `element_status_enum`
- 狀態值:
  - `SUPPORTED`: 有足夠客觀證據或自白支持該要件。
  - `CONTRADICTED`: 現有客觀證據與該要件相悖。
  - `UNRESOLVED`: 證據不足或爭點尚待釐清。
  - `NOT_APPLICABLE`: 該條文排除要件或不適用。
- 約束: 若無任何 `element_fact_mappings` 關聯，狀態必須為 `UNRESOLVED`，禁止逕自標示為 `SUPPORTED`。

### 2.3 候選法律方向狀態機 (Legal Candidate Status)
- 定義: `candidate_status_enum`
- 狀態值:
  - `PRIMARY`: 主要偵查或起訴罪名方向。
  - `ALTERNATIVE`: 備位或可能競合之罪名方向（防範隧道視野）。
  - `LOW_CONFIDENCE`: 證據弱或法規見解分歧之方向。
  - `UNRESOLVED`: 構成要件尚未分析完畢。
  - `REJECTED`: 經事實排除或要件明確不符已淘汰之方向。
- 約束: 單一案件版本中，至少應容納多重法律方向評估，禁止系統強制僅能建立單一方向。

### 2.4 證據與來源狀態機 (Source Status)
- 定義: `source_status_enum`
- 狀態值:
  - `VERIFIED`: 經比對正本或公信紀錄確認無誤。
  - `UNVERIFIED`: 尚未核對原始出處或數位簽章。
  - `UNAVAILABLE`: 來源已滅失或調取不能。
  - `VERSION_UNCERTAIN`: 法規或見解生效版本有疑義。

### 2.5 流程與審核狀態機 (Workflow & Approval Status)
- 定義: `workflow_status_enum` / `approval_status_enum`
- 流程階段:
  - `FACTS_INTAKE` (案情與事實整理)
  - `BEHAVIOR_ANALYSIS` (行為拆解)
  - `LEGAL_RESEARCH` (法律規範與裁判查證)
  - `ELEMENT_EVALUATION` (構成要件與爭點分析)
  - `INTERVIEW_PREP` (筆錄擬定)
  - `INTERVIEW_EXECUTION` (筆錄詢問與事實更新)
  - `DOCUMENT_GENERATION` (條陳與函稿製作)
  - `COMPLETED` (已核定完成)
- 階段狀態: `DRAFT` -> `IN_REVIEW` -> `APPROVED` | `CHANGES_REQUESTED` | `STALE` | `ARCHIVED`
- **下游無效化串接 (Stale Invalidation)**:
  當上游 `facts` 被修改或產生新 revision 時，下游已產生的 `legal_candidates`, `constituent_elements`, `interview_questions`, `document_outputs` 狀態會由觸發器自動標記為 `STALE`，提示承辦人必須重新評估。

---

## 3. 人工審核防護機制 (Human-in-the-Loop Gate)

1. **強制關聯約束**: `document_outputs` 若標示 `is_final = TRUE`，其 `approval_id` 欄位必須非空且參照 `review_approvals`，且該審核記錄的 `status` 必須為 `APPROVED`。
2. **審核不可反向修改**: 審核紀錄包含簽核人員 ID、核定時間戳記、審核意向以及對被審核物件版本產生的快照雜湊值。

---

## 4. 階梯式架構演進：單使用者至多使用者 (Multi-Tenancy Readiness)

第一階段（目前環境）雖然為單一指定人員操作，但資料庫底層設計已具備企業級多租戶防護：
1. 每筆案件皆具備 `lead_investigator_id` 及所屬機關/單位欄位。
2. 所有查詢皆受 PostgreSQL RLS (Row-Level Security) 限制。
3. 未來新增多使用者時，只需新增 `users` 與 `user_roles` 筆數，無需對資料表結構進行任何破壞性遷移。
