# LEGAL-TRACE-DIFF-004：兩套法律分析流程的初始候選差異報告

## 1. 結論

**狀態：`PARTIAL_PASS`。**

本輪使用獨立適配器與同一份標準化語義事實，比較：

- CIA：`app.domain.extract_facts` → `make_case` → `analyze_candidates`
- legal-case-web：`app.rules.analyze_gate1(use_ai=False)` → `candidate_offenses` → `classify_candidates`

本輪首次實質差異可定位為：**兩套各自完成事實轉換後，初始候選產生函式使用不同的候選規則與資料模型**。

這是目前 dirty snapshot 的可重現差異，不是原始題示輸出的唯一根因。原始題示結果仍沒有 request／response、原始 revision、完整 runtime log 或可識別入口，故不能標記 `CONFIRMED_ROOT_CAUSE`。

## 2. 本輪產物與驗證命令

新增的獨立診斷適配器：

- [tools/legal_trace_diff.py](D:\工作用\judicial1\tools\legal_trace_diff.py)
- [LEGAL_TRACE_DIFF_TRACE.json](D:\工作用\judicial1\LEGAL_TRACE_DIFF_TRACE.json)

直接執行：

```powershell
python tools/legal_trace_diff.py --output LEGAL_TRACE_DIFF_TRACE.json
```

語法驗證：

```powershell
python -m py_compile tools/legal_trace_diff.py
```

適配器將兩個專案放在不同 subprocess 執行，使用 UTF-8 stdin 傳入案情，避免 Windows 環境變數／console code page 改寫中文案情。未啟動 HTTP server、未連接 DB／雲端、未呼叫 LLM，未修改正式推理邏輯。

## 3. 實際使用的系統入口

### 3.1 `criminal-investigation-assistant`（CIA）

目前程式的正式 HTTP 入口：

```text
app.server.Handler.do_POST /api/cases
  -> app.domain.make_case
  -> app.domain.extract_facts
  -> app.domain.analyze_candidates
  -> app.question_bank.QuestionBank.child_routes
  -> app.storage.RevisionStore.create
  -> app.server.public_case
```

本輪實際執行的是純函式入口：

```text
app.domain.extract_facts
app.domain.make_case
app.domain.analyze_candidates
```

沒有執行 `RevisionStore.create`、HTTP response 或 frontend。因此：

- `FACT`：以上純函式確實產生本輪 CIA 初始候選。
- `NOT_RUN`：完整 HTTP／DB／UI 路徑。
- 原始題示輸出是否來自 CIA：`UNKNOWN`。

### 3.2 `legal-case-web`

目前程式的正式分析入口：

```text
app.server.py:793-800 /api/analyze
  -> _local_analysis_payload
  -> app.workflow / app.rules
```

建立案件的另一條入口：

```text
app.server.py:801-803 /api/cases
  -> create_case
  -> workflow candidate analysis
  -> STORE.create
  -> workflow.public_case
```

本輪實際執行的是 rules-only fact／candidate 入口：

```text
app.rules.analyze_gate1(use_ai=False)
  -> app.rules.candidate_offenses
  -> app.rules.classify_candidates
```

沒有執行 `workflow.py` 的 AI merge、store、HTTP 或 frontend。因此：

- `FACT`：以上 rules／Gate 1 函式確實產生本輪 legal-case-web 初始候選。
- `NOT_RUN`：完整 HTTP／DB／AI／UI 路徑。
- 原始題示輸出是否來自 legal-case-web：`UNKNOWN`。

## 4. 標準化測試事實

同一份 fixture `STANDARD_SEMANTIC_FACTS_V1` 包含：

| ID | 語義事實 | 來源性質 | 測試狀態 |
|---|---|---|---|
| `F-OWNERSHIP` | 甲表示手機為其所有 | 甲陳述 | `ASSERTED_NOT_VERIFIED` |
| `F-PLACEMENT` | 甲表示曾將手機暫放在便利商店櫃檯旁 | 甲陳述 | `ASSERTED_NOT_VERIFIED` |
| `F-POSSESSION` | 手機是否仍在甲的持有範圍：未確認 | 待確認事項 | `UNKNOWN` |
| `F-TAKING` | 乙承認拿取手機 | 乙陳述 | `ASSERTED_NOT_VERIFIED` |
| `F-BELIEF` | 乙表示自己以為手機是他人遺留、不要的物品 | 乙辯解 | `ASSERTED_NOT_VERIFIED` |
| `F-INTENT` | 乙是否具有不法所有意圖：未確認 | 待確認事項 | `UNKNOWN` |
| `F-RECOVERY` | 手機目前尚未尋獲 | 案件結果記載 | `ASSERTED_NOT_VERIFIED` |

適配器將同一語義事實序列化成相同的摘要輸入，再送入兩套現有 fact conversion。這不是手動偽造 API／DB 輸出；它是兩套純函式的隔離輸入適配。

## 5. 事實模型比較

### 5.1 直接終端輸出摘要

本輪命令已在終端輸出完整比較表；因 Windows console code page，中文欄名可能顯示為亂碼，但 trace JSON 使用 Unicode escape 保存原始文字。核心實際 mapping 如下：

| 比較項目 | CIA 實際模型 | legal-case-web 實際模型 | 語義差異 |
|---|---|---|---|
| 手機所有權 | `NOT_MAPPED`；CIA 產生 `F-RIGHTS`，內容是待問答確認所有／持有／授權 | `fact_key=""` 的來源陳述；沒有 ownership 專用 fact key | 是 |
| 手機放置方式 | `F-PLACE` 由 intake location 形成 `FACT`；摘要內的甲陳述另在 `F-NARRATIVE` | 來源片段為 `fact_key=""`、`EXPLICIT_SOURCE_ASSERTION`；沒有 place projection | 是 |
| 手機是否仍在甲持有範圍 | `F-RIGHTS`／相關 Gate 欄位為 `UNKNOWN` | 來源片段保留原句；`possession_state` 為空，未映射成專用欄位 | 是 |
| 乙拿取手機的陳述 | `F-NARRATIVE` 保留全文；`F-CONDUCT` 為 `UNKNOWN` | 一個 `fact_key=""` 來源片段；`action` 為空 | 是 |
| 乙對手機狀態的認知 | `F-NARRATIVE` 保留全文；`F-MENTAL-STATE` 為 `UNKNOWN` | 一個 `fact_key=""` 來源片段；`knowledge_or_intent` 為空 | 是 |
| 不法所有意圖 | `F-MENTAL-STATE`／Gate 欄位為 `UNKNOWN` | 待確認句保留為來源片段；無專用 fact key，candidate route matrix 另列 unknown element | 是 |
| 手機尚未尋獲 | `F-NARRATIVE` 保留全文；`F-RESULT`、`F-EVIDENCE` 為 `UNKNOWN` | 來源片段為 `fact_key=""`；沒有 result/evidence 專用投影 | 是 |
| 未知事項 | 有多個 typed Gate 1 facts：`F-OBJECT`、`F-CONDUCT`、`F-MENTAL-STATE`、`F-RESULT`、`F-RIGHTS`、`F-CAUSATION`、`F-EVIDENCE` | 有 `machine_status=UNKNOWN` 的 fallback facts，另有多筆 `machine_status=FACT` 的來源陳述；專用欄位未填 | 是 |

### 5.2 實際 CIA facts

由 `app.domain.extract_facts` 取得：

- `F-TIME`、`F-PLACE`：`FACT`，provenance `INTAKE:event_time`／`INTAKE:location`。
- `F-NARRATIVE`：`NARRATIVE`，provenance `INTAKE:summary`，confidence 1.0。
- `F-PERSON-1`、`F-PERSON-2`：`INFERENCE`，provenance `INFERENCE:summary-token`，confidence 0.6。
- `F-OBJECT-1`：`UNKNOWN`，provenance `INFERENCE:summary-keyword`，confidence 0.4。
- `F-CONDUCT`、`F-MENTAL-STATE`、`F-RESULT`、`F-RIGHTS`、`F-CAUSATION`、`F-EVIDENCE`：`UNKNOWN`，provenance `SYSTEM:GATE1`。

`FACT`：CIA 沒有把乙辯解直接轉成「手機客觀上已脫離甲持有」或「乙具有不法所有意圖」。

### 5.3 實際 legal-case-web Gate 1 facts

由 `app.rules.analyze_gate1(use_ai=False)` 取得：

- 甲所有、甲放置、持有未確認、乙拿取、乙辯解、意圖未確認、尚未尋獲，各自成為 `source_ref=intake.summary` 的逐句來源陳述。
- 這些主要是 `fact_key=""`、`assertion_status=EXPLICIT_SOURCE_ASSERTION`、`machine_status=FACT`、`review_status=HUMAN_REVIEW_REQUIRED`。
- `subject/action/object/possession_state/knowledge_or_intent/result` 等欄位在這個摘要變體中沒有被填入。
- 另建立 fallback facts，`machine_status=UNKNOWN`。

這表示 legal-case-web 有 fact conversion，但目前這份摘要的 candidate rules 仍可直接使用原始 summary 與 `intake.summary` source refs；不應把 Gate 1 fact 片段誤說成已確認客觀事實。

## 6. 初始候選生成比較

### 6.1 CIA 初始候選

實際結果：

```text
candidate_id: embezzlement
status: NEEDS_FACTS
score: 35
candidate_role: UNRESOLVED（由目前 candidate object 追蹤）
supporting: 文字線索：遺留
```

child route 清單：

| child route | route article | candidate child `status` | bank `review_status` |
|---|---|---|---|
| `embezzlement_335_general` | 第335條 | `NEEDS_FACTS` | `HUMAN_REVIEW_REQUIRED` |
| `embezzlement_336_1_public` | 第336條第1項 | `NEEDS_FACTS` | `HUMAN_REVIEW_REQUIRED` |
| `embezzlement_336_2_business` | 第336條第2項 | `NEEDS_FACTS` | `HUMAN_REVIEW_REQUIRED` |
| `embezzlement_337_lost_property` | 第337條 | `NEEDS_FACTS` | `HUMAN_REVIEW_REQUIRED` |
| `embezzlement_338_applicable` | 第338條 | `NEEDS_FACTS` | `HUMAN_REVIEW_REQUIRED` |

程式證據：

- `app/domain.py:388-405`：`ROUTE_RULES` hits、contrary hits、semantic adjustment、score。
- `app/domain.py:406-418`：對 parent route 呼叫 `bank.child_routes(route_id)`，並在 child dict 加上 `status="NEEDS_FACTS"` 與 element gaps。
- `app/domain.py:424-444`：建立 parent candidate、status、score、child routes、element assessments。
- `app/question_bank.py:75-106`：依 `parent_route_id` 聚合 child，route `review_status` 來自 runtime bank。

本輪的 `embezzlement` 是 CIA 的**上位 parent route／family id**，不是第337條本身。`ROUTE_LABELS` 將它標示為「侵占（含侵占遺失物）」；實際第337條是 child route id `embezzlement_337_lost_property`。不能從英文名稱自行推定，以上是由 `ROUTE_RULES`、`ROUTE_LABELS` 與 `QuestionBank.child_routes` 直接確認。

### 6.2 legal-case-web 初始候選

實際 raw 結果：

```text
id: theft
candidate_id: candidate:theft
status: NEED_REVIEW
candidate_eligibility: ELIGIBLE_CANDIDATE
matched_terms: 取走他人動產情境
```

route 結果：

| route | route status | review_status | supported count |
|---|---|---|---:|
| `theft_320_1_movable` | `ELIGIBLE_CANDIDATE` | `HUMAN_REVIEW_REQUIRED` | 3/4 |
| `theft_320_2_real_estate` | `HINT_ONLY` | `HUMAN_REVIEW_REQUIRED` | 0/4 |
| `theft_323_energy` | `HINT_ONLY` | `HUMAN_REVIEW_REQUIRED` | 0/3 |
| `theft_324_relative` | `HINT_ONLY` | `HUMAN_REVIEW_REQUIRED` | 0/3 |

程式證據：

- `app/rules.py:2033-2045`：逐 offense 讀取 summary keyword hits。
- `app/rules.py:2291-2323`：建立 candidate、寫入 `status`、`supporting_fact_refs`、`legal_routes`，並設定 `candidate_eligibility="ELIGIBLE_CANDIDATE"`。
- `app/rules.py:2323-2338`：依 `ROUTE_MIN_SUPPORTED_ELEMENTS` 設定每個 route 的 `ELIGIBLE_CANDIDATE`／`HINT_ONLY`。
- `app/rules.py:2463-2490`：`classify_candidates` 補 status summary；目前結果為 `NEED_REVIEW`。

## 7. 首次實質差異位置

### 7.1 事實轉換層的差異

兩套在事實模型就已存在可觀察差異：

| 項目 | CIA | legal-case-web | 分類 |
|---|---|---|---|
| 來源陳述 | 一個全文 `F-NARRATIVE` 加 typed Gate facts | 多筆 `fact_key=""` source statements | `FACT` |
| 專用 possession／intent 欄位 | CIA Gate facts 明確保留 `UNKNOWN` 類別 | 目前摘要變體的專用欄位為空 | `FACT` |
| unknown 狀態 | typed facts 各自有 `status`、provenance、confidence | fallback facts 有 UNKNOWN；source statements 同時是 machine FACT、human review required | `FACT` |
| candidate 使用資料 | `analyze_candidates` 直接使用 summary text；facts 未直接進入 score 參數 | `candidate_offenses` 直接使用 summary，Gate 1 僅提供 evidence refs／element evidence | `FACT` |

這是**第一個已觀察的資料模型差異**，但還不能單獨判定它是造成候選方向差異的唯一原因，因為兩套候選函式都直接讀同一語義摘要中的文字。

### 7.2 候選產生層的差異

即使將兩套都送入相同語義事實摘要，候選產生規則仍不同：

- CIA `ROUTE_RULES` 的 embezzlement parent keywords 包含 `遺留`；score formula 以 parent hit 數量、semantic adjustment、contrary hits 決定 parent status。
- legal-case-web `candidate_offenses` 使用 offense keyword／scene guard／element matrix；本次命中 theft 的「取走他人動產情境」，再以 3/4 supported route elements 設為 `ELIGIBLE_CANDIDATE`。
- 因此在目前 snapshot，初始候選清單第一個實質分叉是：CIA `embezzlement`，legal-case-web `theft`。

分類：`CONTRIBUTING_FACTOR`。這是可重現的目前規則差異，不是原始題示的 `CONFIRMED_ROOT_CAUSE`。

## 8. 特別核查

### 8.1 CIA `embezzlement` 是否等於第337條？

**否。**

`embezzlement` 是 CIA 的 parent route／family id，label 為「侵占（含侵占遺失物）」；第337條是其 child route `embezzlement_337_lost_property`。`QuestionBank.child_routes("embezzlement")` 會同時回傳第335、336、337、338等 child。這是 `FACT`。

### 8.2 第337條 `HUMAN_REVIEW_REQUIRED` 的意義

在 runtime bank 中，`review_status="HUMAN_REVIEW_REQUIRED"` 是 route／法律來源人工覆核狀態；它不是犯罪成立程度。

CIA `analyze_candidates` 另外對 child dict 寫入 `status="NEEDS_FACTS"` 與 element gaps。因此同一 child 同時可觀察：

- `status=NEEDS_FACTS`：目前案件事實／要件仍不足。
- `review_status=HUMAN_REVIEW_REQUIRED`：該法律 route／來源需要人工複核。

這兩者不是升級或降級同一狀態的直接對照。它們屬不同維度，混讀會造成「第337條狀態」的誤解。

### 8.3 四種狀態的流程層級

| 狀態 | 實際定義／位置 | 層級 |
|---|---|---|
| `NEEDS_FACTS` | CIA parent／child candidate 的事實缺口；CIA `analyze_candidates` 建立 | 案件候選／要件缺口 |
| `NEED_REVIEW` | legal-case-web candidate 的 `candidate_status`，由 `candidate_element_state`／classification 使用 | candidate summary 狀態 |
| `ELIGIBLE_CANDIDATE` | legal-case-web route eligibility，依 supported element count 判定 | route eligibility |
| `HUMAN_REVIEW_REQUIRED` | 兩套題庫／法律 route 的人工複核／來源驗證狀態 | legal source／review layer |

`FACT`：四者在目前 source 中屬不同欄位／不同函式階段，不能直接互換。

### 8.4 候選罪名、法條、罪章路由、人工審核是否混用

存在**資料呈現上容易混用、但程式欄位可區分**的情況：

- CIA parent `candidate_id=embezzlement` 是候選 family／parent route；child `article_no=第337條` 是法條 route；`review_status` 是人工複核狀態。
- legal-case-web `id=theft` 是 offense candidate；`legal_routes` 包含多個法條／定義／程序 route；`candidate_eligibility` 是 route eligibility；`review_status` 是人工複核。
- frontend 若只顯示 label、badge 或 route details，可能把這些維度併列，但本輪未執行 UI，故 UI 實際混用為 `NOT_RUN`。

### 8.5 關鍵字／代理分數是否已影響初始候選

**是，對目前 snapshot 已確認。**

- CIA：`analyze_candidates` 在候選建立前計算 `hits`、`semantic_adjustment`、`score`，並以 `score < 65` 決定 `NEEDS_FACTS`／`CANDIDATE`。
- legal-case-web：`candidate_offenses` 先以 summary keyword／scene guard 建立 candidate，再以 element matrix 設定 route eligibility。

這是 `RULE_OR_RANKING` 的 `CONTRIBUTING_FACTOR`，不是原始錯誤組合的確定根因。

### 8.6 相同語義事實下是否仍產生不同初始候選？

**是，已重現。**

- CIA：`embezzlement / NEEDS_FACTS / 35`，child 包含第337條；
- legal-case-web：`theft / NEED_REVIEW`，第320 route `ELIGIBLE_CANDIDATE`。

這證明輸出差異不是只發生在最後 UI；至少在目前兩套的初始候選產生階段已存在。

## 9. 已確認與尚未確認原因

| 發現 | 分類 | 證據 | 信心／範圍 |
|---|---|---|---|
| 兩套 facts schema 不同 | `CONTRIBUTING_FACTOR` | CIA typed Gate facts vs legal source statements／empty fact keys | 高；只針對目前 snapshot |
| 初始候選規則不同 | `CONTRIBUTING_FACTOR` | CIA `analyze_candidates` vs legal `candidate_offenses` | 高；直接重播 |
| CIA parent keyword／score 影響 embezzlement | `CONTRIBUTING_FACTOR` | `遺留` hit、score 35、parent candidate | 高；不能單獨解釋原始第337 CANDIDATE |
| legal route matrix 影響第320 eligibility | `CONTRIBUTING_FACTOR` | `candidate_offenses` 產生 theft、3/4 supported、route eligibility | 高；不能解釋原始第320 NEEDS_FACTS |
| 第337本身是 CIA parent candidate | `RULED_OUT` | 實際 parent id 與 child route id 分開 | 高 |
| `HUMAN_REVIEW_REQUIRED` 等於候選成立程度 | `RULED_OUT` | route review field 與 candidate status 分開 | 中高 |
| 原始題示結果由這兩套目前 snapshot 產生 | `UNKNOWN` | 無原始入口／log／response | 高 |
| DB／LLM／Prompt／HTTP／frontend 導致原始差異 | `NOT_TESTED`／`BLOCKED` | 本輪未執行這些層 | 無法判定 |

本輪沒有 `CONFIRMED_ROOT_CAUSE`。

## 10. 最小修正方案（本次不執行）

建議的最小修正不是把兩邊輸出強行改成相同，而是建立跨 runtime 的明確契約：

1. 先為標準事實建立共用欄位語義與 provenance／assertion status 對照表，明確標示 `NOT_MAPPED`，不得以空欄位當成已確認事實。
2. 將候選 candidate、法條 route、parent family、eligibility、human review、fact gap 分成不同 typed 欄位，禁止狀態字串跨維度直接轉換。
3. CIA child route 仍可列為待調查方向，但不可只因 parent keyword 命中就讓第337 child 看似取得 parent `CANDIDATE`。
4. legal-case-web 應在 candidate generation log 保留 fact snapshot、matched terms、element matrix、candidate status 與 route eligibility 的分離記錄。
5. 建立 isolated HTTP trace，證明 candidate list 從純函式到 API／UI 是否被重新排序或改寫後，再決定是否修改正式邏輯。

本次未執行以上修正。

## 11. 未執行與限制

- 原始題示結果的真正入口：`UNKNOWN`。
- 完整 HTTP：`NOT_RUN`。
- 正式／隔離 DB：`NOT_RUN`／`BLOCKED`。
- LLM、Prompt、AI merge：`NOT_RUN`；本輪 legal Gate 1 使用 `use_ai=False`。
- frontend：`NOT_RUN`。
- 歷史 revision、cache、原始 API payload：`NOT_OBSERVED`。
- 工作樹有既有 modified/untracked 變更；本輪未清理、覆蓋或還原。

## 12. 最終判定

1. 實際入口：已確認兩套目前純函式入口與正式 HTTP 入口；原始題示來源 `UNKNOWN`。
2. 事實模型：同一語義事實在 CIA 形成 typed Gate facts，在 legal-case-web 主要形成 source statement facts，專用欄位映射不同。
3. 初始候選：CIA 是 `embezzlement/NEEDS_FACTS/35`；legal-case-web 是 `theft/NEED_REVIEW`、第320 route `ELIGIBLE_CANDIDATE`。
4. 首次差異：目前 snapshot 在事實模型已出現差異，候選結果的第一個實質分叉發生於兩套各自的初始 candidate generation。
5. 已確認原因：目前兩套的 fact schema 與候選規則不同；分類為 `CONTRIBUTING_FACTOR`。
6. 尚未確認原因：原始版本／入口、DB、LLM／Prompt、API／UI mapping、歷史資料是否造成題示組合。
7. 最小下一步：取得原始 artifact，或執行完整 isolated HTTP + ephemeral-store trace。

**狀態：`PARTIAL_PASS`。**
