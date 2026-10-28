# LEGAL-PIPELINE-FIX-005 修復計畫

## 執行邊界

- `FACT`：正式入口為 `start.ps1 → app.server → app.workflow`；`/api/analyze` 使用 `workflow._local_analysis_payload`，案件建立使用 `workflow.create_case`。
- `FACT`：`legal-case-web` 未 import 或呼叫 `criminal-investigation-assistant`。本次不修改 CIA。
- `FACT`：現有規則、事實及問句資料已在工作樹中有未提交變更；本計畫只新增必要檔案與最小整合，不覆蓋或清理既有變更。
- `UNKNOWN`：正式歷史案件的原始第337條／第320條輸出沒有 request、revision、模型輸入或 DB trace，不能以本次本機測試宣稱已重現該次輸出。

## 相容性契約

### 事實

沿用 `fact_id`、`fact_key`、`fact_status`、`machine_status`、`assertion_status`、`review_status` 及既有來源欄位，新增可追溯欄位：

- `source_type`：`PARTY_STATEMENT`、`EVIDENCE`、`SYSTEM_INFERENCE` 或 `UNKNOWN`。
- `assertion_class`：`ASSERTED`、`ADMITTED`、`DENIED`、`INFERRED` 或 `UNKNOWN`。只有輸入明確提供的類別才可使用 `ADMITTED`／`DENIED`；不由關鍵字推導。
- `verification_status`：`VERIFIED`、`UNVERIFIED` 或 `UNKNOWN`。
- `fact_key_status`：`CLASSIFIED` 或 `UNCLASSIFIED`；空 `fact_key` 保留，不自動補值。
- `case_id`、`revision_id`：在案件建立／動作重算後補上；未持久化的純函式結果以 `0` 表示未分配 revision。

### 候選

沿用舊的 `status`、`candidate_state`、`candidate_eligibility`、`legal_route_states`，新增分離欄位：

- `candidate_status`：`PRIMARY`、`ALTERNATIVE`、`LOW_CONFIDENCE`、`UNRESOLVED` 或 `REJECTED`。
- `readiness_status`：`NEEDS_FACTS` 或 `READY_FOR_REVIEW`。
- `candidate_review_status`：預設 `PENDING`，不等於核准或罪名成立。
- `route_status`、`status_change_reason`、`fact_refs`、`evidence_refs`、`case_id`、`revision_id`。

本次不改變既有候選排序及 API 舊欄位意義；契約欄位只呈現目前規則已有的要件、未知及路由證據。

### 問句

沿用既有 `meta.fact_target`、`legal_targets`、`purpose`、`trigger_condition` 及 `target_elements`，新增契約別名：`gap_id`、`candidate_ids`、`element_ids`、`question_type`、`evidence_refs`、`follow_up_condition`、`case_id`、`revision_id`。不以罪名標籤取代事實缺口。

## 預定修改檔案

| 檔案 | 原因 | 風險／限制 |
|---|---|---|
| `app/analysis_contract.py` | 純函式建立事實、候選、問句相容欄位 | 不執行外部 I/O |
| `app/rules.py` | 在 Gate 1／候選產生時保留契約所需的現有來源資料 | 不改關鍵字命中或排序規則 |
| `app/workflow.py` | 在案件建立及動作重算後補案件／revision 關聯；驗證輸入事實狀態 | 不修改 DB Schema 或舊欄位 |
| `app/workflow.py` | 將既有問句 metadata 映射至契約欄位 | 不改題庫文字及題目選擇規則 |
| `tests/test_pipeline_contract_and_regression.py` | 基準案及測試 A-D 的契約與差異回歸 | 僅隔離本機純函式／workflow |
| `IMPLEMENTATION_REPORT.md`、`TEST_RESULTS.md`、`OPEN_ISSUES.md` | 交付證據與未測試範圍 | 不含密鑰、正式資料或外部服務紀錄 |

## 不應改動

`criminal-investigation-assistant`、正式資料庫與 migration、外部 LLM／雲端、前端顯示契約、既有法律題庫文字，以及既有未提交變更。

## 驗證門檻

1. 原有候選／workflow／問句測試保持通過。
2. 基準案保留來源陳述、未知持有及意圖，不把 `拿取` 自動轉成犯罪成立。
3. 測試 A-D 的新增事實可追溯至事實或證據欄位；矛盾不得覆寫原始陳述。
4. 問句契約欄位必須對應具體 fact gap／構成要件。
5. 明確標記 LLM、正式 DB、HTTP、前端及歷史 revision 未實測項目。

## 實際採用差異

`app/questions.py` 未修改：其既有 metadata 已提供 fact target、legal targets、purpose、trigger condition；由 `app/analysis_contract.py` 在 workflow 邊界建立不破壞舊欄位的 `contract` 映射。未持久化的 revision 0 不將隨機 `case_id` 注入逐筆純函式結果，以維持既有 deterministic regression；正式持久化 revision 才補逐筆案件關聯。
