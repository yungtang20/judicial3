# IMPLEMENTATION_REPORT

## 修正範圍

本次只修改候選罪名分析、事實主張保存、問句 metadata、反事實測試及本機稽核文件；未修改公司模板、家族 Markdown、正式法條資料或外部資料庫。

## 實際修改

### `app/domain.py`

- 保留既有 `status` 欄位，新增 `candidate_role`：`PRIMARY`、`ALTERNATIVE`、`LOW_CONFIDENCE`、`UNRESOLVED`。
- 新增 `core_issue_ids`，針對竊盜／侵占遺失物分別保存：
  - `POSSESSION_STATE`
  - `LOST_OR_OUT_OF_POSSESSION`
  - `UNLAWFUL_OWNERSHIP_INTENT`
  - `POST_TAKING_HANDLING`
- 新增 `legal_basis` 與 `element_assessments`，保存法條來源欄位、要件狀態、支持／相反事實 ID、證據 ID 及爭點 ID。
- 新增有界線的事實模式調整。它只改變待查證候選排序與理由，不產生法律成立結論。
- 新增 `ASSERTED`、`ADMITTED`、`DENIED`、`INFERRED`、`UNKNOWN` assertion status 支援；舊 `facts[].status=STATEMENT` 保留相容性。
- 問句新增 `question_type`、`issue_ids`、`generation_basis`、`follow_up_condition`。
- 矛盾資料於相容的 `disputed_facts` 之外新增 `contradiction_issues`，以 `issue_id=ROLE_CONTRADICTION:<fact_target>` 追蹤，保留原回答與新 revision。

### `tests/test_sim_case_remediation.py`

新增基準案例及 A/B/C/D 反事實測試，驗證候選順位、候選語義狀態、意圖線索、assertion 及矛盾爭點。

### `tools/legal_reasoning_audit.py`

新增離線、決定性稽核腳本，不使用外部網路、不寫入案件資料庫，直接驗證五項核心條件。

### 稽核文件

- `docs/audit/LEGAL_REASONING_AUDIT.md`
- `docs/audit/TEST_RESULTS.md`
- `docs/audit/OPEN_ISSUES.md`

## 相容性與限制

- 保留既有 `candidate.status`、`question_id`、HTTP API 及題庫格式。
- `candidate_role` 是新增語義欄位；既有前端仍可使用原 `status`。
- 本次不是法律人工核准；現行法條定位已由 `legal_sources/article_verifications.json` 保存，但行為時法、實務判決及內規仍需人工核對。
- 未將候選方向寫成正式筆錄或條陳中的犯罪結論。
