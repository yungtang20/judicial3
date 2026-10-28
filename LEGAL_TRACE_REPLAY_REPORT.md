# LEGAL-TRACE-REPLAY-003：候選罪名端到端追蹤測試報告

## 1. 結論摘要

**整體狀態：`PARTIAL_PASS`。**

本輪建立並執行獨立隔離追蹤器：

- 腳本：[tools/legal_trace_replay.py](D:\工作用\judicial1\tools\legal_trace_replay.py)
- 實際 JSON trace：[LEGAL_TRACE_REPLAY_TRACE.json](D:\工作用\judicial1\LEGAL_TRACE_REPLAY_TRACE.json)

腳本以兩個獨立 subprocess 載入兩套專案，避免同名 `app` package 互相污染；未啟動 HTTP server、未連接資料庫／雲端、未呼叫 LLM、未修改正式候選邏輯。

受控重播的最早可觀察差異在**候選產生／事實資料模型階段**：

| 專案 | 實際入口 | 候選產生結果 |
|---|---|---|
| `criminal-investigation-assistant` | `app.domain.make_case` | parent `embezzlement/NEEDS_FACTS/50`；child 第337條為 `HUMAN_REVIEW_REQUIRED` |
| `legal-case-web` | `app.rules.candidate_offenses` → `classify_candidates` | `theft/NEED_REVIEW`；第320條 route 為 `ELIGIBLE_CANDIDATE` |

兩套目前輸出都不是題示的「第337條 `CANDIDATE`、第320條第1項 `NEEDS_FACTS`」。因此本輪確認了目前版本的可觀察差異及其首次出現階段，但**沒有取得原始執行紀錄，不能標記 `CONFIRMED_ROOT_CAUSE`**。

## 2. 原始執行紀錄搜尋

### 搜尋範圍

本輪唯讀搜尋：

- `LEGAL_ROOT_CAUSE_AUDIT.md`、`LEGAL_ROOT_CAUSE_TRACE.md`
- `criminal-investigation-assistant` 與 `legal-case-web` 全部程式、測試、docs、review、data 產物
- `337`、`320`、`CANDIDATE`、`NEEDS_FACTS`、`NEED_REVIEW`、`ELIGIBLE_CANDIDATE`
- `embezzlement`、`theft`、parent／child route、candidate status、revision、request id、Prompt、API、cache、log
- Git branch、HEAD、歷史 commit、未提交狀態

### 搜尋結果

| 項目 | 結果 | 證據狀態 |
|---|---|---|
| 原始完整案情 | 找到使用者提供的模擬案情及目前 fixture 變體；沒有原始執行保存檔 | `NOT_OBSERVED` |
| 原始執行命令／入口 | 找到目前兩套程式入口；沒有能識別題示輸出的原始 command log | `NOT_OBSERVED` |
| 原始 request／response | 未找到含 request id 的 API JSON | `NOT_OBSERVED` |
| 原始 revision／case id | 未找到可連結題示輸出的 revision payload | `NOT_OBSERVED` |
| 原始候選中間清單 | 未找到 | `NOT_OBSERVED` |
| 原始應用程式 log | 未找到可識別題示輸出的 log | `NOT_OBSERVED` |
| 測試 fixture／snapshot | 找到目前 CIA remediation fixture、audit tool 與 legal-case-web tests；它們不是原始輸出快照 | `FACT`，但非原始 trace |
| 機密資訊 | 本輪未輸出、複製或寫入 API key、password、token；trace 只記錄非機密 metadata 與案情測試資料 | `FACT` |

因此，本輪沒有假裝追溯原始執行；原始輸出來源仍是 `UNKNOWN`。

## 3. 重播環境與安全界線

### 3.1 工作樹與版本

| 項目 | 實際值 |
|---|---|
| 根目錄 | `D:\工作用\judicial1` |
| Git branch | `codex/sim-case-remediation` |
| Git HEAD | `e5d8e95ea59292e5464114ba6b804165e9511ce8` |
| HEAD message | `feat: add criminal investigation assistant` |
| 工作樹 | 有既有 modified/untracked 檔案；本輪未清理、還原或覆蓋 |
| CIA `app/domain.py` | SHA-256 `71D3CDC0E016C5782768E782BD2E4961A875DE5B07ED1E5395C5CCA8896C1DAD` |
| CIA runtime bank | SHA-256 `0AC9E0CD5C3A1A7796B285AC25D1056FB00A8AFF2A2D67302AA6114E9BCBFDB6` |
| legal-case-web `app/rules.py` | SHA-256 `240BB3BC7AA468EC03BC67ED137713C1EB7278F77EA49044102BACDB44A97AA4` |
| legal-case-web question bank | SHA-256 `D16C2D95DBAB2FC89647C115720EBAE74CA8E1C086B4CFA096DE4D9246D179F4` |

上述 metadata 由 `LEGAL_TRACE_REPLAY_TRACE.json` 的 `projects.*.metadata` 實際記錄。工作樹是 dirty snapshot；因此這是**目前狀態的可重播證據**，不是歷史原始版本證據。

### 3.2 測試安全狀態

| 項目 | 狀態 |
|---|---|
| 外部網路 | `NOT_USED` |
| LLM | `NOT_RUN` |
| 正式資料庫／雲端 | `NOT_RUN` |
| HTTP server | `NOT_RUN`；只呼叫純函式入口 |
| 正式推理邏輯 | 未修改 |
| Prompt／Schema | 未修改 |
| 追蹤腳本 | 獨立新增，與正式 runtime 分離 |

## 4. 實際輸入與呼叫入口

### 4.1 測試案情

本輪使用單一精確輸入識別碼 `F2_exact_take_variant`：

> 甲將手機放在便利商店櫃檯旁，乙拿取手機離開。乙表示原本以為是他人遺留、不要的手機。現有資料尚不能確定手機當時是否仍在甲的持有範圍，以及乙是否具有不法所有意圖。

結構化 intake：

```json
{
  "event_time": "2026-10-28T10:00:00+08:00",
  "location": "便利商店櫃檯旁",
  "summary": "F2 exact take variant",
  "case_kind": "WITH_VICTIM"
}
```

實際完整摘要與 intake 已保存在本機 `LEGAL_TRACE_REPLAY_TRACE.json`，未包含秘密資訊。

### 4.2 CIA 實際入口

追蹤腳本直接呼叫：

```text
app.domain.make_case(intake, QuestionBank())
  -> extract_facts
  -> _initial_parties / _initial_behavior_events
  -> analyze_candidates
  -> QuestionBank.child_routes
```

對應正式 HTTP 呼叫鏈（本輪未啟動）：

```text
app.server.Handler.do_POST
  -> app.domain.make_case
  -> app.storage.RevisionStore.create
  -> app.server.public_case
```

本輪實際觀察入口是 `app.domain.make_case`；HTTP、store、API response 層為 `NOT_RUN`，不是已觀察的端到端 HTTP 輸出。

### 4.3 legal-case-web 實際入口

追蹤腳本直接呼叫：

```text
app.rules.candidate_offenses(summary, bank)
  -> app.rules.classify_candidates(summary, bank)
```

對應正式 HTTP 呼叫鏈（本輪未啟動）：

```text
app.server:793-800 ANALYZE_ROUTE
  -> _local_analysis_payload
  -> rules / optional AI workflow
```

本輪實際觀察入口是 rules-only 函式；workflow merge、store、API response、frontend renderer 為 `NOT_RUN`／`NOT_OBSERVED`。

## 5. 逐階段追蹤結果

### 5.1 CIA：實際觀察

| 階段 | 候選識別 | 原始狀態 | 分數 | 輸出狀態 | 實際來源 |
|---|---|---:|---:|---|---|
| 初始產生 | `embezzlement` parent | `NEEDS_FACTS` | 50 | `NEEDS_FACTS` | `app.domain.analyze_candidates`；trace `projects.criminal_investigation_assistant.replay.candidates[0]` |
| 初始產生 | `theft` | 未產生 | N/A | N/A | 同一函式；F2 結果中不存在 |
| 法律要件評估 | `embezzlement` | `NEEDS_FACTS` | 50 | `NEEDS_FACTS` | parent 的 `supporting_facts` 有遺留文字線索；要件 gap 為 `UNKNOWN` |
| parent route | `embezzlement` | `NEEDS_FACTS` | 50 | `NEEDS_FACTS` | `ROUTE_RULES` 命中及 semantic score |
| child route | `embezzlement_337_lost_property` | `HUMAN_REVIEW_REQUIRED` | N/A | `HUMAN_REVIEW_REQUIRED` | `QuestionBank.child_routes`；article 第337條 |
| 最終映射 | parent `embezzlement` | `NEEDS_FACTS` | 50 | `NEEDS_FACTS` | 本輪未執行 `public_case`；case dict 的候選已觀察 |
| 最終映射 | child 第337條 | `HUMAN_REVIEW_REQUIRED` | N/A | `HUMAN_REVIEW_REQUIRED` | 本輪未執行 HTTP／UI；child route dict 已觀察 |

### 5.2 CIA 事實與來源

追蹤器實際保存的 facts 顯示：

| Fact 類型 | 實際狀態 | 來源／信心 |
|---|---|---|
| 時間、地點 | `FACT` | `INTAKE:event_time`、`INTAKE:location` |
| 全文敘事 | `NARRATIVE` | `INTAKE:summary`，confidence 1.0 |
| 甲、乙身份 token | `INFERENCE` | summary-token，confidence 0.6 |
| 物品 | `UNKNOWN` | inference summary-keyword，confidence 0.4 |
| 行為、心理、持有、意圖、證據等 | `UNKNOWN` | `SYSTEM:GATE1` |

這表示本次實際 CIA facts 沒有把「乙認為是遺留物」直接轉成已確認「手機已脫離甲持有」；但全文敘事仍被送進 parent keyword scorer。這是可觀察的資料流，不等於已確認是原始題示輸出的根因。

### 5.3 legal-case-web：實際觀察

| 階段 | 候選識別 | 原始狀態 | 分數 | 輸出狀態 | 實際來源 |
|---|---|---:|---:|---|---|
| 初始產生 | `theft` | `NEED_REVIEW` | N/A | `NEED_REVIEW` | `app.rules.candidate_offenses` |
| 初始產生 | `embezzlement` | 未產生 | N/A | N/A | 同一函式 raw list 無 embezzlement |
| 法律要件評估 | `theft_320_1_movable` | route state `ELIGIBLE_CANDIDATE` | N/A | `ELIGIBLE_CANDIDATE` | element matrix：3/4 source-supported，intent／相關要件留在 unknown |
| parent route | `theft` | `NEED_REVIEW` | N/A | `NEED_REVIEW` | candidate object `candidate:theft` |
| child route | `theft_320_1_movable` | `HUMAN_REVIEW_REQUIRED`／route review | N/A | route eligibility `ELIGIBLE_CANDIDATE` | candidate `legal_routes`／`legal_route_states` |
| 最終映射 | `candidate:theft` | `NEED_REVIEW` | N/A | `NEED_REVIEW` | `classify_candidates` raw output；未執行 API／frontend |

`NEEDS_FACTS`、`NEED_REVIEW`、`ELIGIBLE_CANDIDATE`、`HUMAN_REVIEW_REQUIRED` 在目前兩套程式中不是同一 status vocabulary，不能直接互換。

## 6. 首次出現差異的階段

### 6.1 在兩套目前 runtime 之間

首次差異發生在**初始候選產生／事實資料模型階段**，不是資料庫寫入、API 最後映射或前端畫面：

1. CIA `make_case` 先建立 typed facts，再由 `analyze_candidates` 以 parent route keyword／score 產生 `embezzlement`。
2. legal-case-web rules path 沒有 CIA 式 facts pipeline，直接以 summary 與 legal element matrix 產生 `theft`。
3. 因為兩邊在初始 candidate list 已不同，後續 child route 與狀態也必然不同。

這是**目前兩個受控 replay 的 FACT**。它不證明原始輸出也在同一階段產生差異，因為原始入口未知。

### 6.2 在 CIA 單一路徑內

CIA 的第337條首次出現於 `parent route → child route` 展開階段：

```text
embezzlement parent / NEEDS_FACTS / 50
  -> QuestionBank.child_routes("embezzlement")
  -> embezzlement_337_lost_property / HUMAN_REVIEW_REQUIRED
```

`FACT`：child route 有被新增到候選資料。

`FACT`：本次 child 沒有被升級為 `CANDIDATE`。

`CONTRIBUTING_FACTOR`：child route 以 parent 關聯取得，沒有在此段看到獨立 child score／candidate threshold；這可能造成方向外溢，但不能解釋題示的 `CANDIDATE` 狀態。

### 6.3 legal-case-web 單一路徑內

legal-case-web 的第320方向首次出現於 `candidate_offenses` 的 raw candidate generation；`candidate_eligibility=ELIGIBLE_CANDIDATE` 與 `status=NEED_REVIEW` 同時存在於 candidate object 的不同欄位／層級。未執行 workflow／API／frontend，因此本輪沒有觀察到它被改寫成 `NEEDS_FACTS`。

## 7. parent／child 與狀態轉換證據

### CIA

- parent candidate：`candidate_id=embezzlement`、`status=NEEDS_FACTS`、`score=50`。
- child：`route_id=embezzlement_337_lost_property`、`article_no=第337條`、`review_status=HUMAN_REVIEW_REQUIRED`。
- child elements：遺失／脫離持有、取得與後續處分、不法所有意圖，均保留待確認／人工審查。
- 排序：目前 parent 清單由 score 再以 candidate id 排序；本次只有 embezzlement parent，因此沒有觀察到第337 child 被獨立排序。

### legal-case-web

- raw candidate：`id=theft`、`candidate_id=candidate:theft`、`status=NEED_REVIEW`。
- route：`theft_320_1_movable`、`candidate_eligibility=ELIGIBLE_CANDIDATE`。
- unknown facts：`original_possession`、`consent`、`intent`。
- 排序：本次 raw list 只有 theft；未觀察到第二候選排序或 API 重排。

### 尚未觀察的轉換

以下沒有執行證據，不以推測補填：

- CIA `RevisionStore.create` 寫入後的 API response：`NOT_RUN`。
- legal-case-web `workflow.py:1138-1217` AI/rules merge：`NOT_RUN`。
- legal-case-web `public_case` 到 frontend `app.js`：`NOT_RUN`。
- 任何歷史 revision／cache 回填：`NOT_OBSERVED`。

## 8. 資料庫、LLM、Prompt、排序、輸出映射查證

| 層級 | 狀態 | 實際證據 |
|---|---|---|
| 資料庫寫入／讀取 | `NOT_RUN`／`BLOCKED` | 本輪未連接正式或隔離 DB；追蹤器只呼叫純函式，沒有 case id／revision read-back |
| LLM | `NOT_RUN`／`BLOCKED` | 兩個 replay 均沒有 LLM 呼叫；沒有固定模型或 response fixture |
| Prompt | `NOT_OBSERVED` | 沒有實際 model request；只能靜態知道 legal-case-web workflow 有 AI contract path |
| 規則／排序 | `FACT`（目前程式） | CIA `analyze_candidates` 實際產生 parent score 50；legal-case-web rules 實際產生 theft candidate |
| parent→child | `FACT`（CIA） | 第337 child 實際出現在 embezzlement parent 下，狀態為 HUMAN_REVIEW_REQUIRED |
| API output mapping | `NOT_RUN` | 沒有啟動 server 或實際 HTTP request |
| 前端 mapping | `NOT_RUN` | 沒有瀏覽器／UI trace |
| cache／歷史資料 | `NOT_OBSERVED` | 未讀取既有 DB、cache payload 或歷史 revision |

## 9. 原始根因分級

| 觀察 | 分類 | 理由 |
|---|---|---|
| CIA parent keyword／score 使遺留線索形成 embezzlement parent | `CONTRIBUTING_FACTOR` | 有本次實際 replay 證據，但未形成題示第337 `CANDIDATE` |
| CIA parent→child 展開讓第337方向出現 | `CONTRIBUTING_FACTOR` | 有本次實際 replay 證據；child 狀態仍是 HUMAN_REVIEW_REQUIRED |
| legal-case-web 與 CIA 初始候選不同 | `CONTRIBUTING_FACTOR` | 有本次實際 replay 證據；只能說明兩套 runtime 差異 |
| 第337 `CANDIDATE` 原始狀態由上述機制直接造成 | `UNKNOWN` | 缺少原始版本、輸入、中間清單與 response |
| 第320 `NEEDS_FACTS` 原始狀態由某個狀態轉換造成 | `UNKNOWN` | 目前 CIA 可產生 parent NEEDS_FACTS，但沒有與第337 CANDIDATE 同時出現 |
| 資料庫造成原始偏差 | `NOT_TESTED`／`BLOCKED` | 沒有安全隔離 DB replay 或原始 query log |
| LLM／Prompt 造成原始偏差 | `NOT_TESTED`／`BLOCKED` | 沒有實際 LLM call、Prompt envelope 或 response |
| API／前端把狀態重新映射成題示結果 | `NOT_TESTED` | 未執行 HTTP／browser；目前沒有直接輸出證據 |

本輪沒有任何項目符合 `CONFIRMED_ROOT_CAUSE`。

## 10. 測試結果與錯誤處理

### 已執行

```text
python tools/legal_trace_replay.py --output LEGAL_TRACE_REPLAY_TRACE.json
```

結果：`TRACE_EXIT=0`；JSON trace 產生成功，包含兩套 metadata、輸入、facts、候選、child route、`NOT_RUN`／`NOT_OBSERVED` 標記。

```text
python -m py_compile tools/legal_trace_replay.py
```

結果：`COMPILE_EXIT=0`。

追蹤器首次執行曾遇到 Windows console UTF-8 decode error；該錯誤發生於獨立診斷腳本的 subprocess output reader，尚未形成任何候選結論。腳本已改為以 bytes 讀取並以 replacement decode，再重新執行成功。這不是正式推理邏輯的修改。

### 未執行／阻塞

- 完整 HTTP API replay：`NOT_RUN`；本輪避免啟動 server。
- 隔離資料庫 write/read-back：`BLOCKED`；沒有必要的安全 fixture DB，且不使用既有 DB。
- 直接 LLM：`BLOCKED`；無可用本機固定 model fixture，且禁止外部服務。
- 固定 Prompt／model／retrieval 三次 replay：`NOT_RUN`。
- 前端 browser trace：`NOT_RUN`。

## 11. 下一個最小必要驗證動作

最小動作不是先改規則，而是取得一份原始輸出 artifact，至少包含：

1. 原始完整案情與結構化 input。
2. 執行入口、專案路徑、Git HEAD／build fingerprint。
3. case id、revision id、source version。
4. 初始 facts／assertions／evidence provenance。
5. 初始候選清單、parent／child route、分數與狀態。
6. API response 或 UI payload；若有 LLM，還要有非機密 Prompt 組裝摘要、model 設定與 response hash。

若原始 artifact 不存在，下一個最小可執行測試是把本輪追蹤器擴充為**完整 HTTP isolated server + ephemeral store trace**，仍不接外部 DB／LLM，並保留：

```text
request -> facts -> candidate_offenses/analyze_candidates
        -> parent -> child -> store payload -> public_case -> response
```

該測試完成前，不得把目前 `CONTRIBUTING_FACTOR` 升格為 `CONFIRMED_ROOT_CAUSE`。

## 12. 最終判定

- **已觀察差異**：兩套目前 runtime 在初始候選產生階段即分叉；CIA 的第337方向在 child 展開時出現，但不是 `CANDIDATE`；legal-case-web 的第320方向在 rules candidate generation 出現，但不是 `NEEDS_FACTS`。
- **尚未證實原因**：原始版本、原始 request／response、DB revision、LLM／Prompt、API／UI mapping、歷史 cache。
- **已確認根因**：無。
- **是否可以開始修正式邏輯**：否；目前證據適合建立下一個 isolated HTTP trace，不足以支持針對某個正式規則的根因修正。

**結論：`PARTIAL_PASS`；目前差異已被實際重播定位至目前兩套 runtime 的候選產生階段，但原始輸出的唯一根因仍為 `UNKNOWN`。**
