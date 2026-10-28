# LEGAL-ROOT-CAUSE-002：候選罪名偏差實際來源追蹤報告

## 0. 執行摘要

**整體狀態：`PARTIAL_PASS`。**

本輪完成前次報告覆核、工作樹／版本確認、兩個本機專案的函式級同案情重播、候選產生與 parent/child 路由追蹤、資料庫 schema／查詢設計檢查、Prompt／LLM 入口檢查、輸出與前端映射檢查，以及原始結果字串與相關產物搜尋。

目前沒有取得原始那次 API response、request id、執行 log、歷史 revision payload 或可識別的 UI/API trace。因此不能把目前程式中存在的關鍵字、代理分數或 parent→child 設計直接宣稱為「原始輸出唯一根因」。

可直接重現的結果是：

| 路徑 | 精確使用「拿取」摘要的目前輸出 | 與題示輸出 |
|---|---|---|
| `criminal-investigation-assistant` | parent `embezzlement/NEEDS_FACTS/50`；包含 `embezzlement_337_lost_property` child，但 child 為 `HUMAN_REVIEW_REQUIRED`；沒有 `theft` | 不一致 |
| `legal-case-web` rules path | `theft/NEED_REVIEW`；`theft_320_1_movable` 為 `ELIGIBLE_CANDIDATE`；沒有第337條 | 不一致 |

因此，本輪確認的是「目前兩套 runtime 不是同一條產生題示結果的可重現路徑」，而非題示結果的原始來源。`RULE_OR_RANKING` 與 `PIPELINE_LOGIC` 是目前可見的貢獻因素／風險；原始輸出的確切根因維持 `UNKNOWN`。

## 1. 證據分級與範圍

- `FACT`：由目前工作樹檔案、命令輸出、函式重播或測試輸出直接證明。
- `INFERENCE`：由上述證據推導，但未直接連到原始執行。
- `UNKNOWN`：目前沒有足夠輸入、log、payload 或重播證據。
- 本輪執行模式：`SINGLE_AGENT_MODE`；實際模型身分未由執行環境提供，故不宣稱雙模型審查。
- 允許的寫入只有本報告檔；未修改程式、Prompt、資料庫、部署、Git commit 或 push。
- 未連接正式資料庫、既有 SQLite 資料庫、雲端或外部 LLM。

題示的原始候選結果本身只作為本輪的待追蹤輸出規格，不作為已取得的 runtime artifact。若沒有原始 request/response 或 log，不能將使用者提供的結果反向當成程式執行證據。

## 2. 前次稽核報告覆核

`LEGAL_ROOT_CAUSE_AUDIT.md` 可讀取。前次報告記載的主要範圍為：

1. `criminal-investigation-assistant`：`server.py:165-170` → `make_case` → `domain.py:512` 附近的 `analyze_candidates`，並檢查 `QuestionBank.child_routes`、revision schema、前端顯示。
2. `legal-case-web`：`server.py:793-800` 的 local analysis、`workflow.py` 的 AI/rules merge、`rules.py` 的規則候選、Prompt、storage、retrieval metadata cache 與前端映射。
3. 前次執行過規則函式級重播、靜態 compile、既有 CIA audit tool／測試；沒有執行外部 LLM、正式 DB、雲端或固定模型三次重播。

前次報告的直接證據與推測有清楚區分：

| 前次結論 | 本輪覆核 |
|---|---|
| `criminal-investigation-assistant` 有 parent keyword／score 機制，並會展開含第337條的 child route | `FACT`，本輪以目前 source 與重播再次確認；但不能單獨解釋題示的 child `CANDIDATE` |
| `legal-case-web` 目前 rules replay 未得到題示精確組合 | `FACT`，本輪以兩個明確輸入變體再次確認；不能推論歷史版本必然相同 |
| LLM、正式 DB、歷史 revision、原始檢索結果未實測 | `FACT`，本輪仍未取得這些 artifact |
| parent→child 可能造成狀態外溢 | `INFERENCE`／`CONTRIBUTING_FACTOR`，目前沒有 child 被升為題示 `CANDIDATE` 的重播證據 |

前次曾觀察到 `criminal-investigation-assistant/app/domain.py:196` 的 `IndentationError`，之後檔案已被修改，最後讀取／compile 為成功。這表示前次重播期間工作樹不是固定 snapshot；它會影響可重現性，但沒有證據證明該 syntax error 造成題示原始輸出。分類：`CONTRIBUTING_FACTOR`（工作樹狀態漂移）／原始根因 `UNKNOWN`。

## 3. 實際專案、分支與版本

### 3.1 工作樹

| 項目 | FACT |
|---|---|
| 工作目錄 | `D:\工作用\judicial1` |
| Git branch | `codex/sim-case-remediation` |
| HEAD | `e5d8e95ea59292e5464114ba6b804165e9511ce8` |
| HEAD commit | `feat: add criminal investigation assistant`，2026-10-28 18:42 +08:00 |
| 未提交狀態 | 有大量既有 modified/untracked 檔案；本輪未清理或覆蓋 |
| CIA `domain.py` | SHA-256 `71D3CDC0E016C5782768E782BD2E4961A875DE5B07ED1E5395C5CCA8896C1DAD`；mtime 2026-10-28 19:12:32 |
| CIA runtime question bank | SHA-256 `0AC9E0CD5C3A1A7796B285AC25D1056FB00A8AFF2A2D67302AA6114E9BCBFDB6` |
| legal-case-web `rules.py` | SHA-256 `240BB3BC7AA468EC03BC67ED137713C1EB7278F77EA49044102BACDB44A97AA4`；mtime 2026-10-26 06:56:43 |
| legal-case-web question bank | SHA-256 `D16C2D95DBAB2FC89647C115720EBAE74CA8E1C086B4CFA096DE4D9246D179F4` |

Git history顯示 CIA 目前只有加入該專案的單一 commit，沒有可供本輪追溯的較早 committed runtime history。`legal-case-web` 則有多個歷史 commit；其中 `a1e63a6` 曾明確處理「拿取」 coverage，`5e6c080` 曾修正弱關鍵字造成的 false-positive candidate。這些是版本演變證據，不是原始輸出執行紀錄。

### 3.2 不同 runtime 的初步結論

`criminal-investigation-assistant` 使用：

```text
POST /api/cases
  -> app.server.Handler.do_POST
  -> app.domain.make_case
  -> app.domain.analyze_candidates
  -> QuestionBank.child_routes
  -> RevisionStore.create
  -> public_case
```

`legal-case-web` 使用：

```text
POST /api/analyze
  -> app.server._local_analysis_payload
  -> app.workflow / app.rules
```

或：

```text
POST /api/cases
  -> app.server.create_case
  -> app.workflow AI/rules merge
  -> STORE.create
  -> workflow.public_case
```

兩套的 candidate id、狀態名稱、parent/child 模型與 revision schema 不同。不得把其中一套的重播結果當作另一套的原始輸出證據。

## 4. 實際呼叫鏈與資料追蹤

### 4.1 `criminal-investigation-assistant`

| 階段 | 函式／檔案 | 輸入→輸出 | 狀態／排序轉換 | 是否證明為原始路徑 |
|---|---|---|---|---|
| 輸入 | `app/server.py:165-170` `Handler.do_POST` | JSON intake → `make_case` | 沒有外部請求；`QuestionBank` 在本機載入 | `UNKNOWN`；只證明目前入口 |
| 案件建構 | `app/domain.py` `make_case` | `event_time/location/summary/case_kind` → case dict | 建立 revision 前的 candidates、facts、parties、events | `UNKNOWN` |
| 事實抽取 | `app/domain.py` `extract_facts` | summary → `facts[]` | 時間／地點為 `FACT`；全文為 `NARRATIVE`；甲乙為 `INFERENCE`；物品及構成要件多為 `UNKNOWN` | `FACT`（目前函式）；非原始執行證明 |
| 角色／事件 | `_initial_parties`, `_initial_behavior_events` | 甲乙及句子 → `parties[]`, `events[]` | 乙身份為 `UNKNOWN`／`INFERRED_TOKEN`；事件為 `REPORTED`，actor 未直接綁定 | `FACT`（目前函式） |
| parent 候選 | `app/domain.py` `analyze_candidates` | summary + bank → parent candidates | ROUTE_RULES substring hits、semantic adjustment、score、threshold；`遺留` 可使 embezzlement 命中，`拿取`／`拿起` 可使 theft 命中 | `FACT`（目前程式）；非原始執行證明 |
| child 路由 | `app/question_bank.py:75-106` `QuestionBank.child_routes` | parent route id → child routes | 依 `parent_route_id` 聚合並按 route id 排序；child 未取得獨立 candidate score | `FACT`；目前重播中實際發生 |
| parent 狀態 | `analyze_candidates` | score／contrary → parent status | `CANDIDATE`、`NEEDS_FACTS` 或 `LOWERED`；child 預設 `NEEDS_FACTS`／source review 狀態 | `FACT`；題示組合未重現 |
| 寫入 | `app/storage.py` `RevisionStore.create` | case dict → `case_head`、`case_revision` 及 normalized tables | revision=1、digest、command log；本輪未連線現有 DB | `FACT`（schema／函式）；沒有 runtime DB 證據 |
| API／UI | `app/server.py:48-61` `public_case`；`app/static/app.js:14` `renderCandidates` | case dict → JSON → badge／child details | `public_case` 未把 child 狀態升級；UI 顯示 parent `item.status`，child 顯示 `review_status` | `FACT`；無原始 HTTP trace |

重要事實：目前 CIA 的 parent→child 連接確實會讓 `embezzlement_337_lost_property` 出現在 parent candidate 的 `child_routes`，但本輪重播 child 是 `HUMAN_REVIEW_REQUIRED`，不是題示 `CANDIDATE`。因此「存在 child route」不能被升級成「第337條原始取得 CANDIDATE」。

### 4.2 `legal-case-web`

| 階段 | 函式／檔案 | 輸入→輸出 | 狀態／排序轉換 | 是否證明為原始路徑 |
|---|---|---|---|---|
| local API | `app/server.py:793-800` | `case_text`／`summary` → `_local_analysis_payload` | 不讀歷史 case；以目前 rules/AI 設定分析 | `UNKNOWN` |
| rules 候選 | `app/rules.py:2033` `candidate_offenses` | summary + bank → candidate list | phrase／element guard、source evidence matrix、`candidate_eligibility`、`NEED_REVIEW` | `FACT`（目前 rules replay） |
| rules summary | `app/rules.py:2463` `classify_candidates` | raw candidates → candidates + status | 保留 element unknown／status；依規則結果分類 | `FACT` |
| AI／rules merge | `app/workflow.py:1138-1217` | clean summary、catalog、revision、source hashes → AI result + rule candidates | AI candidates 先依 AI order，再接 remaining；寫入 `candidate_analysis_contract` | `FACT`（靜態）；未實際呼叫外部 AI |
| case persistence | `app/storage.py`、`app/server.py:801-825` | case → store | Ephemeral、SQLite 或 Supabase 依設定；revision optimistic check | `FACT`（設計）；原始 store 未知 |
| output | `app/workflow.py:1285-1299` `public_case` | case → API JSON | deep copy，補 default route fields；沒有證據將 337 升級 | `FACT`（目前函式）；無原始 HTTP trace |
| frontend | `app/static/app.js:514-639` | API candidates → candidate analysis cards | `candidate_eligibility` 決定 tier；route state 另行顯示 | `FACT`；無原始畫面 trace |

### 4.3 事實角色是否被錯誤扁平化

目前 CIA 的 `extract_facts` 保留部分來源與 confidence，但摘要仍以一個 `NARRATIVE` fact 保存全文；`_initial_behavior_events` 把句子標成 `REPORTED`，沒有把「乙稱／乙認為」建立成獨立的 assertion-to-evidence link。這支持以下有限結論：

- `FACT`：目前資料結構沒有把每一個敘述角色完整分成可查證的證據鏈；甲乙 token 的角色有推論標記。
- `FACT`：目前重播沒有把「乙認為是遺留物」直接寫成「客觀上已脫離甲持有」的 `FACT`；相關物品／持有／意圖欄位仍有 `UNKNOWN`。
- `INFERENCE`：若另一版本的抽取器把整段摘要或辯解直接送進 keyword scorer，可能造成規則誤用；本輪沒有該版本的完整輸入／輸出，不能確認發生。
- 分類：`FACT_EXTRACTION` 為 `RISK_NOT_REPRODUCED`，不是 `CONFIRMED_ROOT_CAUSE`。

## 5. 同案情逐階段重播比較

為避免把不同文字誤當同一案，本輪分開記錄：

- **F1（拿起變體）**：前次測試 fixture 使用「乙拿起手機離開」，並包含甲表示／乙稱及未確認持有與意圖。這是 CIA 既有 remediation fixture 的可重播輸入。
- **F2（題示拿取版）**：`甲將手機放在便利商店櫃檯旁，乙拿取手機離開。乙表示原本以為是他人遺留、不要的手機。現有資料尚不能確定手機當時是否仍在甲的持有範圍，以及乙是否具有不法所有意圖。`

### F2 目前函式級結果

| 階段 | `legal-case-web` | `criminal-investigation-assistant` | 差異 |
|---|---|---|---|
| 事實抽取 | 此 isolated `candidate_offenses` replay 不建立 CIA 式 facts；classified status 為 `subject_identified=true, has_victim=true, is_solved=unknown` | `F-TIME/F-PLACE=FACT`；全文 `NARRATIVE`；甲乙 `INFERENCE`；物品、行為、意圖等多為 `UNKNOWN` | 是；資料模型不同 |
| 初始候選清單 | 1 個 `theft` | 1 個 parent `embezzlement`；本次精確 F2 未產出 theft | 是 |
| parent/child | `theft_320_1_movable` 為 suggested route；第337不存在 | embezzlement parent 展開 335、336-1、336-2、337、338 | 是 |
| 規則／評分 | source evidence matrix；theft supported 3/4，`candidate_eligibility=ELIGIBLE_CANDIDATE` | embezzlement score 50，supporting text 為遺留線索；child 沒有獨立 score | 是 |
| 狀態 | parent/candidate `NEED_REVIEW`；route `ELIGIBLE_CANDIDATE` | parent `NEEDS_FACTS`；child 337 `HUMAN_REVIEW_REQUIRED` | 是 |
| 最終輸出 | theft／第320方向 | embezzlement parent／含第337 child | 是 |

此表的兩邊均為目前函式級輸出，不是原始執行的 API trace。它確認差異最早在「候選產生／事實資料模型」階段出現；不能確認題示偏差最早在哪個歷史版本階段出現。

### F1 目前結果補充

CIA 的 F1 replay 產出兩個 parent：`embezzlement/NEEDS_FACTS/35` 與 `theft/NEEDS_FACTS/35`，兩者 `candidate_role=UNRESOLVED`；embezzlement child 包含第337條但 child 不是 `CANDIDATE`。legal-case-web 使用「拿起」的同樣字面變體時 raw／classified candidates 為空。這個差異進一步證明不能只比較罪名名稱，也不能把前次的「拿取」重播與「拿起」重播混為同一輸入。

## 6. 第337條與第320條狀態形成追蹤

### 6.1 第337條

目前 CIA 的可追蹤路徑是：

```text
summary 中的遺留／遺失／拾得等字串
  -> ROUTE_RULES embezzlement parent hit
  -> score / status 形成 embezzlement parent
  -> QuestionBank.child_routes("embezzlement")
  -> embezzlement_337_lost_property
  -> child review_status
```

`FACT`：第337條 child 由 parent route 關聯取得，且資料記錄三項待確認要件；目前 `analyze_candidates` 沒有以該 child 的各要件重新計算一個可升級 `CANDIDATE` 的獨立分數。

`CONTRIBUTING_FACTOR`：parent keyword／代理分數與 child 展開的設計可能把「遺留」線索帶到第337方向，造成候選方向過早出現。

`RISK_NOT_REPRODUCED`：本輪沒有重現第337 child 狀態為題示 `CANDIDATE`，也沒有重現第337單獨出現在最終清單而第320為 `NEEDS_FACTS`。

### 6.2 第320條

目前 CIA 的可追蹤路徑是：

```text
summary 中的拿取／拿起／偷等字串
  -> ROUTE_RULES theft parent hit
  -> score / status 形成 theft parent
  -> QuestionBank.child_routes("theft")
  -> theft_320_1_movable
  -> child review_status
```

F1 中 `theft` parent 是 `NEEDS_FACTS`，但 F2 中「拿取」受到同時出現的遺留／不要等內容與目前 semantic 規則影響，只保留 embezzlement parent。這是目前程式邏輯差異的直接證據，不是題示歷史輸出的證據。

legal-case-web F2 則由 `candidate_offenses` 直接形成 theft candidate，狀態為 `NEED_REVIEW`；這不是題示的 CIA 名稱 `NEEDS_FACTS`，也不是同一 status vocabulary。

## 7. 規則、排序與輸出映射

### 7.1 規則／排序

`criminal-investigation-assistant/app/domain.py` 的 `analyze_candidates` 使用 substring route hits、semantic adjustments、score clamp，以及 `score < 65` 的狀態門檻；最後依 `(-score, candidate_id)` 排序。這是 `FACT`。目前 audit tool 的四組反事實測試也重現：

- 加入「甲一直坐在、伸手即可取回」時，theft score 上升並排前。
- 加入「甲離開、手機遺失；乙拾得、不在現場」時，embezzlement score 上升並排前。
- 加入「立即交店員、尋找失主」時，兩方向仍保留為待確認。
- 衝突敘述仍保留 disputed facts／assertions。

這支持 `RULE_OR_RANKING`／`PIPELINE_LOGIC` 為 `CONTRIBUTING_FACTOR`，但不是原始輸出 `CONFIRMED_ROOT_CAUSE`。

`legal-case-web/app/rules.py` 使用路線要件矩陣與 candidate eligibility；F2 產生 theft 的原因是目前 phrase／element matrix 命中，而非 CIA 的 parent score。`a1e63a6`、`5e6c080` 顯示歷史規則曾調整「拿取」coverage 與弱關鍵字 false positive，足以說明版本差異可能改變輸出，但沒有原始執行版本與 payload，故分類為 `RISK_NOT_REPRODUCED`。

### 7.2 LLM／Prompt

靜態可確認：

- `legal-case-web/app/workflow.py:1138-1217` 會組合 clean summary、offense catalog、case revision、source snapshot hashes；AI 結果可能先於 rules candidates 排序，並寫入 `candidate_analysis_contract`。
- `legal-case-web/app/ai.py` 的 Prompt 路徑可包含 system message、summary、facts、catalog、rules；目前未發現本輪可識別的原始 request envelope、實際 model response 或完整 prompt log。
- CIA 的目前 `POST /api/cases` 不呼叫外部 LLM；但不能以目前 source 排除原始輸出來自其他 runtime、舊版或未提供入口。

分類：`LLM_OR_PROMPT = NOT_TESTED`／原始作用 `UNKNOWN`。API 回應理由「遺留、失主、拾得」只能作為輸出文字，不能反推模型實際採用該原因。

## 8. 資料庫、revision、快取與歷史結果

### 8.1 CIA storage

`criminal-investigation-assistant/app/storage.py` 的 schema 有 `case_head`、immutable `case_revision`、`command_log`、`case_fact`、`case_candidate`、`element_gap` 等表；`case_candidate` 以 `(case_id, revision, candidate_id)` 為 key。`RevisionStore.get` 先由 `case_head.current_revision` 取得 revision，再以 `(case_id, revision)` 讀 `case_revision.payload_json`。

`FACT`：設計上有 case/revision 條件、foreign key、CAS 與 digest。

`NOT_TESTED`：本輪未連接 `var/cases.sqlite3` 或 `var/audit.sqlite3`，未執行 SQL read-back，也沒有原始 DB query log。因此不能宣稱實際資料庫讀寫正確，也不能判定 DB 不是原始根因。

### 8.2 legal-case-web storage

`server.py` 依設定選擇 `EphemeralCaseStore`、SQLite store 或 Supabase store；SQLite 的 `get` 以 `case_id` 讀單一 row，`save` 以 `case_id + expected revision` 做 optimistic update。`workflow.public_case` 對目前 case deep copy 並補預設欄位。

`FACT`：目前設計有 revision 條件與不使用歷史清單作候選分析的 local path。

`UNKNOWN`：原始輸出使用哪一種 store、哪個 case id/revision、是否有舊 payload 被送入 API，沒有執行紀錄可證明。

### 8.3 retrieval／cache

目前 retrieval cache 的靜態設計主要保存法律 metadata／hash，文件標示未接入 Gate 2；但本輪沒有原始檢索 request、命中結果、排序分數或 cache hit log。

分類：`RETRIEVAL_OR_CACHE = NOT_TESTED`（非 `RULED_OUT`）。沒有證據可以把 cache 指定為根因，也沒有足夠證據排除原始舊資料影響。

## 9. 對照測試與執行狀態

| 測試 | 狀態 | 實際證據與限制 |
|---|---|---|
| A. 直接呼叫 LLM | `NOT_RUN / BLOCKED` | 指令禁止外部服務；沒有本機 mock response fixture。無法判斷模型／Prompt 是否造成原始排序。 |
| B. 完整 app、排除歷史分析 | `PARTIAL_PASS` | 完成兩套本機函式級 replay；未啟動完整 HTTP + isolated store trace。兩套目前輸出均不等於題示精確組合。 |
| C. 寫入隔離 DB 後逐欄 read-back | `NOT_RUN / BLOCKED` | 未建立或連接測試 DB；現有 DB 不作測試目標。無法判斷實際 serialization／read-back。 |
| D. 固定模型／Prompt／retrieval 三次重播 | `NOT_RUN / BLOCKED` | 無固定模型、Prompt envelope、檢索 snapshot 與 model response fixture。 |
| CIA audit tool | `PASS`（限定本機規則範圍） | `tools/legal_reasoning_audit.py` 四個 baseline／反事實檢查通過；不代表原始輸出重現。 |
| Python compile | `PASS`（最後狀態） | 目前兩套相關 Python 檔案 compile exit 0；前次曾有 `domain.py:196` syntax error，之後工作樹已漂移。 |
| 原始字串／產物搜尋 | `PASS`（搜尋完成，未找到） | 搜尋 `337`、`320`、`CANDIDATE`、`NEEDS_FACTS`、`embezzlement`、`theft`、route、storage、Prompt、API；未找到可識別的原始 response/log。 |

## 10. 發現分級

| 發現 | 分類 | 直接證據 | 影響範圍／信心 |
|---|---|---|---|
| 原始輸出沒有可識別 runtime artifact | `NOT_TESTED`／原始根因 `UNKNOWN` | 搜尋未找到 request id、response、log、revision payload；兩條目前 replay 均不相符 | 影響整個根因結論；信心高 |
| CIA parent keyword／score 可受「遺留」等文字影響 | `CONTRIBUTING_FACTOR` | `domain.py` ROUTE_RULES、semantic score、threshold；F2 replay embezzlement parent score 50 | 影響候選方向形成；信心高，但不能單獨解釋原始 child status |
| CIA parent→child 展開缺少 child-specific ranking gate | `CONTRIBUTING_FACTOR` | `analyze_candidates` + `QuestionBank.child_routes`；child 337 在重播為 review required | 可能造成方向外溢；信心中高 |
| legal-case-web 與 CIA 是不同候選 vocabulary／路徑 | `RULED_OUT`（兩者目前不是同一輸出鏈） | 不同入口、資料模型、status、candidate id；F2 結果不同 | 排除「直接把兩套結果當同一 runtime」；信心高 |
| 事實角色與 assertion link 不完整 | `RISK_NOT_REPRODUCED` | CIA 保留部分 provenance/status，但事件 actor 與證據 link 未完整建立 | 可能影響下游解釋；信心中 |
| 歷史規則版本可能改變「拿取」及弱 keyword 結果 | `RISK_NOT_REPRODUCED` | `a1e63a6`、`5e6c080` commit diff；沒有原始版本 payload | 影響重播可比性；信心中高 |
| DB stale revision／錯案混入 | `NOT_TESTED` | schema 有 revision 條件，但未連 DB、無原始 query log | 影響歷史結果假設；信心無法判定 |
| LLM／Prompt 直接產生偏差 | `NOT_TESTED` | 無完整 prompt、model response、設定或 request trace | 影響 AI merge／排序假設；信心無法判定 |
| UI/API 將第337 `NEEDS_FACTS` 改為 `CANDIDATE` | `RISK_NOT_REPRODUCED` | 前端目前顯示 parent status、child review_status；無原始 HTTP/UI trace | 不能排除其他版本；目前未證明 |
| 前次 `IndentationError` 是根因 | `RULED_OUT`（作為已證實因果） | error 發生時與目前可 compile 工作樹不同；無錯誤輸出鏈 | 只保留為 replay validity risk；信心中 |

## 11. 對八個必答問題的回答

1. **是否找到原始輸出的確切執行入口？** `UNKNOWN`。找到兩套目前入口，但沒有證據指向題示那次執行。
2. **是否找到第337條取得 `CANDIDATE` 的確切程式路徑？** `UNKNOWN`。目前只找到 CIA parent 展開第337 child 的路徑；重播 child 並非 `CANDIDATE`。
3. **是否找到第320條取得 `NEEDS_FACTS` 的確切程式路徑？** `UNKNOWN`（針對原始輸出）。CIA F1 可產生 theft parent `NEEDS_FACTS`，但 legal-case F2 是 `NEED_REVIEW`，不能當成原始路徑。
4. **兩個狀態是否來自不同候選階段？** `UNKNOWN`。目前設計確實存在 parent status、child review status、AI candidate status、UI tier 等多層狀態，但沒有原始中間清單可證明題示兩個狀態跨階段混合。
5. **是否有證據顯示舊資料、不同 revision 或 UI/API mapping 影響結果？** 沒有直接證據；屬 `NOT_TESTED`／`UNKNOWN`。設計上有 revision 與映射風險，但沒有原始 payload／trace。
6. **目前能否判定資料庫是根因？** 不能，`UNKNOWN`／`NOT_TESTED`。也不能因未連線就宣稱 DB 正常或排除 DB。
7. **目前能否判定 LLM 或 Prompt 是根因？** 不能，`UNKNOWN`／`NOT_TESTED`。沒有完整 prompt、模型設定或 response log。
8. **下一個最小驗證動作是什麼？** 取得原始那次輸出的完整 HTTP request／response 或含 request id 的 log，至少包含：原始摘要、case id、revision、source／commit hash、candidate intermediate list、status、完整理由、model／Prompt hash。若原始 artifact 已不存在，建立不連外的 isolated replay harness，以 F2 精確字串同時捕捉 input→facts→parent candidates→child routes→API JSON，並固定兩套 source snapshot後再比對。

## 12. 是否具備開始修正程式的證據

**不具備針對原始錯誤輸出的充分證據。** 目前可開始的是「另立修正任務前的驗證設計」，不是直接修改候選排序：

1. 先取得／保存原始 artifact，確認是哪個 project、commit、entry point、case/revision 與 status vocabulary。
2. 以原始 snapshot 重播，逐層保存 facts、assertions、retrieval、candidate list、child route list、API response。
3. 僅在該重播重現 `337 CANDIDATE / 320 NEEDS_FACTS` 後，才判定修正點屬 `FACT_EXTRACTION`、`RULE_OR_RANKING`、`PIPELINE_LOGIC`、`LLM_OR_PROMPT`、`DATABASE_WRITE_READ`、`RETRIEVAL_OR_CACHE` 或 `OUTPUT_MAPPING`。

不得在這些證據取得前，依目前可見的 `ROUTE_RULES` 或 `related_hint` 前端過濾就宣稱唯一根因。

## 13. 修正前不得破壞的既有功能與資料

以下為後續修正時的保護界線，非本輪修改內容：

- 不得把報案人陳述、涉嫌人辯解、客觀證據及系統推論合併成同一個已證實 fact。
- 不得遺失 `provenance`、`status`、`confidence`、assertion、evidence link、case id、revision、source fingerprint。
- 不得以 parent candidate 的存在替代 child route 各構成要件的確認。
- 不得讓 AI order 覆蓋 rules status，除非契約明確記錄來源、狀態與版本。
- 不得改變現有 immutable revision、CAS、request digest、source pin 與人工覆核狀態的資料完整性。
- 不得把 `HUMAN_REVIEW_REQUIRED`、`NEEDS_FACTS`、`NEED_REVIEW`、`ELIGIBLE_CANDIDATE` 直接視為同義；後續必須先建立跨 runtime 的狀態對照契約。

## 14. 最終結論

### 已確認

- `FACT`：兩個目前專案是不同 runtime，入口、資料模型、候選狀態與 parent/child 流程不同。
- `FACT`：CIA 目前對相關摘要存在 parent keyword／score 路徑，並會展開包含第337條的 child；但目前重播沒有把第337條升為 `CANDIDATE`。
- `FACT`：legal-case-web 目前 F2 rules replay 產生第320方向而非第337方向，狀態是 `NEED_REVIEW`／route `ELIGIBLE_CANDIDATE`，不是題示的 `NEEDS_FACTS`。
- `FACT`：工作樹曾在前次重播期間漂移，`domain.py` 先出現 syntax error，後續已變更並 compile PASS。

### 尚未證實的風險

- `RULE_OR_RANKING` 與 `PIPELINE_LOGIC` 可能讓遺留線索外溢到第337方向；分類為 `CONTRIBUTING_FACTOR`，不能升級為原始唯一根因。
- `FACT_EXTRACTION` 的敘述角色／assertion link 不完整可能影響下游，但本輪未重現為題示輸出。
- `DATABASE_WRITE_READ`、`RETRIEVAL_OR_CACHE`、`LLM_OR_PROMPT`、`OUTPUT_MAPPING` 仍無原始執行證據，維持 `UNKNOWN`／`NOT_TESTED`。

### 未執行

直接 LLM、固定模型三次重播、正式或隔離 DB write/read-back、原始 HTTP/UI trace、歷史 revision payload 比對均未執行或不可執行；原因是缺少固定依賴且本輪明確禁止外部／正式資源。

### 最小下一步

先取得原始 response／log artifact 與 request id；沒有 artifact 時，再建立不連外的 isolated trace harness。只有重現原始狀態組合後，才開始修改程式。

**結論：`PARTIAL_PASS`；原始候選偏差的唯一根因仍為 `UNKNOWN`。**
