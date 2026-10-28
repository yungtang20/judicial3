# LEGAL-FACT-CANDIDATE-SHADOW-006 影子測試報告

## 結論

整體狀態：`PARTIAL_PASS`

本輪已完成本機、離線、可重播的事實模型與初始候選影子測試，並保留實際 JSON trace。尚未找到原始 `第337條 CANDIDATE / 第320條 NEEDS_FACTS` 輸出的唯一根因；本報告不把影子測試結果升格為正式 Runtime 結論。

- `FACT`：正式本機入口由 `start.ps1 → app.server → app.workflow` 組成；本機預設 `EphemeralCaseStore`。證據：`README.md:225-226`、`app/server.py:90`、`app/storage.py:24`。
- `FACT`：本輪實際呼叫 `app.rules.analyze_gate1(use_ai=False)`、`app.rules.candidate_offenses(...)`、`app.rules.build_questions(...)`，未呼叫 LLM、資料庫、HTTP 或前端。
- `FACT`：三個情境均觀察到現有事實路徑與標準化 fixture 路徑在 `facts` 階段首次不同；三個情境的初始候選均為 `theft / NEED_REVIEW / ELIGIBLE_CANDIDATE`。
- `INFERENCE`：在本影子輸入下，初始候選產生仍主要由案情文字與關鍵字命中控制；追加的持有／遺失標準化事實沒有使 `candidate_offenses` 產生第337條候選。
- `UNKNOWN`：這不能證明原始輸出使用同一版本、同一入口、同一案情或同一資料庫／歷史 revision。

## 一、完整測試兩項失敗

執行基線：`pytest -q` → `660 passed, 2 failed`。本輪未修改這兩項失敗所涉及的測試或 fixture。

### 1. Human Gate runtime surface hash

- 測試：`tests/test_legal_retrieval_human_gate_packet.py::test_runtime_surfaces_are_hash_stable_and_unreachable`
- 斷言：`tests/test_legal_retrieval_human_gate_packet.py:90` 的 `assert sha256(path) == surface["sha256"]`。
- 實際 hash：`0df3905af439bf3d725bca190668410885bb68cf597e3405c85fad57acb6c807`
- 預期 hash：`be721c613c24b28efe11c790743247cc73bc6432e24bc87cf75859da05924232`
- 測試依賴：`docs/evidence/legal_retrieval_human_gate_packet.json` 及其 runtime surface 設定。
- 分類：`BASELINE_FAILURE_CONFIRMED`；`FACT`。這是 frozen hash 與目前 dirty worktree 檔案不一致，非引用契約或影子工具的執行失敗。`app/workflow.py`、`app/rules.py`、`app/server.py` 均無 `citation_contract` import。

### 2. Question family generated template mismatch

- 測試：`tests/test_question_family_catalog.py::test_every_family_has_a_current_readable_markdown_file`
- 斷言：`tests/test_question_family_catalog.py:253`，比較 `data/question_family_catalog.json` 產生的預期 Markdown 與 `docs/family_templates` 現存內容。
- 觀察到差異：至少一個 family template 的現存 Markdown 內容與由目前 catalog 產生的 expected output 不一致；完整 traceback 顯示差異發生在逐檔文字 equality 斷言。
- 分類：`BASELINE_FAILURE_CONFIRMED`；`FACT`。這是 catalog／template fixture 不一致，非 citation parser 或影子重播引起；本輪不依賴單一終端編碼下的差異行文字判斷根因。

兩項失敗均沒有被修正；本輪不以修正基線為目的，也未將它們標成整體測試通過。

## 二、正式入口與實際呼叫鏈

| 階段 | 實際位置 | 本輪是否呼叫 |
|---|---|---|
| 啟動／HTTP | `start.ps1` → `app.server` | `NOT_RUN`；本輪避免啟動服務 |
| 本機案件分析 payload | `app.server._local_analysis_payload` | `NOT_RUN`；僅作靜態入口證據 |
| Gate 1 事實 | `app.rules.analyze_gate1(intake, use_ai=False)` | `OBSERVED` |
| 初始候選 | `app.rules.candidate_offenses(summary, bank, gate1)` | `OBSERVED` |
| 問句 | `app.rules.build_questions(...)` | `OBSERVED` |
| 案件 workflow | `app.workflow.create_case` / `apply_action` | `NOT_RUN`；影子測試不修改案件狀態 |
| 儲存／revision | `app.storage.EphemeralCaseStore` | `NOT_RUN` |

影子工具：`tools/legal_fact_candidate_shadow.py`。可直接執行：

```powershell
cd D:\工作用\judicial1\legal-case-web
python tools\legal_fact_candidate_shadow.py
pytest -q tests\test_legal_fact_candidate_shadow.py
python -m py_compile tools\legal_fact_candidate_shadow.py tests\test_legal_fact_candidate_shadow.py
```

輸出 trace：`LEGAL_FACT_CANDIDATE_SHADOW_TRACE.json`。該檔案記錄 Git HEAD、工作樹狀態、輸入、事實、候選、問句及未使用外部服務的明確標記。

## 三、逐情境實際結果

| 情境 | 現有事實路徑初始候選 | 標準化事實路徑初始候選 | 首次差異 | 問句階段 |
|---|---|---|---|---|
| BASELINE | `theft / NEED_REVIEW / ELIGIBLE_CANDIDATE` | `theft / NEED_REVIEW / ELIGIBLE_CANDIDATE` | `facts` | 兩路 `OBSERVED` |
| A 仍可支配 | `theft / NEED_REVIEW / ELIGIBLE_CANDIDATE` | `theft / NEED_REVIEW / ELIGIBLE_CANDIDATE` | `facts` | 兩路 `OBSERVED` |
| B 已離開／遺失 | `theft / NEED_REVIEW / ELIGIBLE_CANDIDATE` | `theft / NEED_REVIEW / ELIGIBLE_CANDIDATE` | `facts` | 兩路 `OBSERVED` |

### 事實差異

- 現有路徑：`analyze_gate1(use_ai=False)` 產生以 `intake.summary` 為來源的規則式 facts；可觀察到部分 `fact_key` 為空字串，並帶有 `EXPLICIT_SOURCE_ASSERTION`、`UNKNOWN`、`HUMAN_REVIEW_REQUIRED` 等欄位。
- 標準化路徑：由 `LEGAL_TRACE_FIXTURE.json` 經獨立 adapter 傳入 `ASSERTED`、`ADMITTED`、`UNKNOWN` 及 `verification_status`；adapter 未自行填入 `fact_key`、未把 UNKNOWN 轉成已知。
- A 追加 `fact:shadow-a-possession`；B 追加 `fact:shadow-b-lost` 與 `fact:shadow-b-not-present`。這些 facts 在 trace 中實際存在，但沒有改變初始候選清單。

## 四、候選與問句追蹤

- 初始候選產生函式：`app/rules.py:2033` 的 `candidate_offenses`。
- 影子測試實際取得的初始候選只有 `theft`；沒有觀察到 `lost_property`／第337條候選被加入。
- 候選狀態實際輸出為 `status=NEED_REVIEW`、`candidate_state=NEED_REVIEW`、`candidate_eligibility=ELIGIBLE_CANDIDATE`；這些欄位被分開記錄，未在影子工具中互換。
- 排序／要件的欄位若由現有候選提供，原樣保留；若某層沒有欄位，trace 標示 `NOT_OBSERVED`，不補推測值。
- 問句由 `app/rules.py:2735` 的 `build_questions` 產生；本輪可執行並保留完整輸出，但沒有把問句文字當成候選成立證據。

## 五、差異層級判定

| 分類 | 判定 | 證據與限制 |
|---|---|---|
| `FACT_EXTRACTION` | `RISK_NOT_REPRODUCED` | 現有抽取確實與 fixture 結構不同，但本輪沒有證明抽取錯誤；原始執行未追溯。 |
| `FACT_MAPPING` | `CONTRIBUTING_FACTOR` | 影子 adapter 與現有 facts 的欄位／狀態不同，且首次可觀察差異在 facts；adapter 未修改正式模型。 |
| `CANDIDATE_GENERATION` | `CONTRIBUTING_FACTOR` | `candidate_offenses` 在三個反事實輸入下均只產生 theft；顯示初始候選未反映追加標準化 facts，但尚不能解釋原始第337條輸出。 |
| `ELEMENT_ASSESSMENT` | `NOT_TESTED` | 本輪沒有正式法律要件矩陣／資料庫／LLM 端到端執行證據。 |
| `RANKING` | `NOT_OBSERVED` | 未觀察到第337與第320並列的排序；因此不能判定排序造成原始組合。 |
| `ROUTE_STATUS` | `NOT_OBSERVED` | 本輪未跑 parent／child route 的正式 workflow；不能用影子結果推論 UI/API 狀態。 |
| `QUESTION_GENERATION` | `RISK_NOT_REPRODUCED` | 函式可執行且輸出已保存，但未證明其影響原始候選偏差。 |
| `DATABASE/LLM/HTTP` | `NOT_TESTED` | 依任務限制未連線；trace 明確記錄 `NOT_USED`。 |

## 六、已確認、風險與未知

### 已確認的觀察

1. 新增 citation parser 沒有被正式 `workflow.py`、`rules.py` 或 `server.py` import；本輪不會把它當成候選偏差修復。
2. 既有規則式事實抽取與標準化 fixture 的第一個可觀察差異在 facts，不是最後顯示階段。
3. 現有初始候選函式在本影子案例中沒有因 A／B 的新增 facts 產生候選變化；其輸出仍是單一 theft。
4. 未知事實在標準化路徑仍保留 `UNKNOWN`，測試 3 項通過。

### 尚未證實

- `第337條 CANDIDATE / 第320條 NEEDS_FACTS` 的原始輸入、Git 版本、revision、檢索結果、LLM prompt、API response 及 UI trace。
- 是否有歷史分析結果、不同專案輸出混用、最後映射覆寫或快取造成原始組合。
- 原始輸出是否來自 `legal-case-web` 正式入口；本輪只確認架構入口，未追溯該次執行紀錄。

## 七、最小修正建議（本輪未執行）

最小下一步不是直接增加第337條關鍵字，而是建立一個隔離的、固定 revision 的候選生成診斷入口，將 `gate1.facts`、候選初始清單、要件矩陣、route 狀態及最終 API payload 同時保存；以同一 request ID 重播正式入口。只有當該 trace 證明差異在正式候選函式後才進一步檢查排序／映射；若差異在輸入，先修正事實契約與 provenance。

開始修改正式程式的條件尚未具備：缺少原始執行 trace，且 LLM、資料庫、HTTP、前端及歷史 revision 尚未測試。

## 八、驗證摘要

- 影子工具：PASS（exit 0）。
- 影子測試：`3 passed`。
- Python compile：PASS。
- 完整 pytest（加入本輪 3 項影子測試後）：`663 passed, 2 failed`；兩項失敗已分類為既有 hash／fixture 基線失敗，未修正。此前未加入影子測試時為 `660 passed, 2 failed`。
- 正式候選規則、Prompt、Schema、資料庫及案件流程：本輪未修改。
- LLM、正式資料庫、HTTP、前端、雲端、歷史 revision：`NOT_RUN`／`BLOCKED`。
