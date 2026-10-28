# LEGAL-PIPELINE-FIX-005 測試結果

## 通過

- `pytest -q tests/test_candidate_semantic_safety.py tests/test_workflow.py tests/test_question_logic.py` → `96 passed`（基準測試）。
- `pytest -q tests/test_pipeline_contract_and_regression.py` → `7 passed`。
- `pytest -q tests/test_pipeline_contract_and_regression.py tests/test_official_case_regressions.py::test_official_regression_cases_are_deterministic_and_fresh` → `8 passed`。
- `python tools/validate_pipeline_contract.py` → `PASS`；實際輸出 8 facts、候選 `theft/NEEDS_FACTS`、29 questions、`external_services=NOT_USED`。
- `python -m compileall -q app tools/validate_pipeline_contract.py` → `PASS`。

## LEGAL-CITATION-CONTRACT-001

- 既有 103 項相關測試：`103 passed`。
- 新增 citation／trace 測試：`9 passed`。
- 合併定向測試：`112 passed`（既有 103 + 新增 9）。
- `python tools/validate_citation_contract.py` → `PASS`；12 citation cases、15 mentions、2 candidates、`llm=NOT_USED`、`database=NOT_USED`。
- `python -m compileall -q app/citation_contract.py tests/test_citation_contract.py tools/validate_citation_contract.py` → `PASS`。

新增 parser 測試不呼叫正式 workflow，因此沒有候選分析 runtime 行為變更證據，也沒有宣稱原始偏差已解決。

## 完整測試集

最後一次 `pytest -q` 的本輪完整結果：`660 passed, 2 failed`。新增 9 項離線 parser 測試均通過；已知剩餘失敗為工作樹原有的：

1. `tests/test_legal_retrieval_human_gate_packet.py::test_runtime_surfaces_are_hash_stable_and_unreachable`：既有 runtime surface hash 與檔案不同。
2. `tests/test_question_family_catalog.py::test_every_family_has_a_current_readable_markdown_file`：既有 family template 與產生內容不同。

修正前曾有 `tests/test_official_case_regressions.py::test_official_regression_cases_are_deterministic_and_fresh` 因本輪動態 case metadata 失敗；已以 revision 0 相容處理修正，定向測試通過。

## 未執行／阻擋

- `BLOCKED`：正式資料庫讀寫、歷史 revision、快取與 API trace；本輪禁止連線且沒有隔離 DB fixture。
- `BLOCKED`：LLM／Prompt 固定模型重播；正式 local path 預設 `use_ai=False`，未提供固定模型環境。
- `NOT_RUN`：正式 HTTP、前端及雲端部署整合測試。

## LEGAL-FACT-CANDIDATE-SHADOW-006

- `python tools/legal_fact_candidate_shadow.py` → `PASS`；建立 `LEGAL_FACT_CANDIDATE_SHADOW_TRACE.json`，未使用 LLM、資料庫、HTTP。
- `pytest -q tests/test_legal_fact_candidate_shadow.py` → `3 passed`。
- `python -m py_compile tools/legal_fact_candidate_shadow.py tests/test_legal_fact_candidate_shadow.py` → `PASS`。
- 基準、反事實 A、反事實 B 的首次可觀察差異均在 `facts`；三者兩條輸入路徑的初始候選均為 `theft / NEED_REVIEW / ELIGIBLE_CANDIDATE`。
- 最新完整 pytest（含本輪 3 項影子測試）：`663 passed, 2 failed`；兩項既有 hash／fixture 失敗仍未修改。
- 這些結果只代表離線影子函式行為，不代表原始第337條／第320條輸出根因已定位或已修復。
- `NOT_RUN/BLOCKED`：正式 workflow、HTTP、前端、LLM、資料庫、歷史 revision、快取與雲端整合。

## LEGAL-FACT-LINEAGE-007

- `python tools/legal_fact_lineage.py` → `PASS`；產生 `LEGAL_FACT_LINEAGE_TRACE.json`。
- `pytest -q tests/test_legal_fact_lineage.py` → `3 passed`。
- `python -m py_compile tools/legal_fact_lineage.py tests/test_legal_fact_lineage.py` → `PASS`。
- A、B 均保持原始摘要不變；新增 facts 在 Gate 1 與 candidate call 參數中可觀察，但候選／問句輸出 `UNCHANGED`。
- 診斷性 typed `intent=UNKNOWN` probe 使 `unknown_fact_keys` 與問句輸出變化，證明下游依賴特定 fact contract。
- 本輪未修改正式候選規則、Prompt、Schema、資料庫或案件流程；正式 HTTP、LLM、資料庫、歷史 revision 與前端仍 `NOT_RUN/BLOCKED`。

## Trace-first 臺灣離線評估 sidecar

- `pytest -q tests/test_legal_evaluation_replay.py` → `12 passed`。
- `python -m py_compile tools/legal_evaluation_replay.py` → `PASS`。
- `python tools/legal_evaluation_replay.py --repetitions 3` → 工具執行 `PASS`；語義 hash 三次相同，評估結果 `PARTIAL_PASS`。
- 5 個案例的首個實質差異均為 `FACT`；明示 UNKNOWN 未以 typed fact 保留，D 案的 `DENIED`／監視器矛盾未保留為可區分狀態。
- 候選 Recall@3：baseline `0.50`、A `1.00`、B `0.00`、C `N/A`、D `0.00`。
- 問句覆蓋率：baseline `0.50`、A `1.00`、B `1.00`、C `1.00`、D `0.75`；此結果來自 gold-selected question lane，不代表自動候選已經人工核准。
- `NOT_RUN`：LLM、資料庫、HTTP、前端、歷史 revision、正式端到端。

本輪最新完整測試：`678 passed, 2 failed`（`62.46s`）。失敗仍是既有的
`test_runtime_surfaces_are_hash_stable_and_unreachable` 與
`test_every_family_has_a_current_readable_markdown_file`；本次 sidecar 未修改其 runtime surface、packet、catalog 或 family template，亦未降低測試標準。
