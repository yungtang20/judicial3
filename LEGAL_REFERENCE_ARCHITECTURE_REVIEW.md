# LEGAL-REFERENCE-AUDIT-001 外部法律 AI 專案流程借鑑評估

## 0. 稽核範圍與結論

本次為唯讀架構稽核。未修改 `legal-case-web` 正式程式、Prompt、Schema、資料庫或既有工作樹；未下載 CAIL 資料集、未連線外部資料庫或 LLM。

整體判定：`PARTIAL_PASS`

原因：兩個外部專案的主要設計與指定檔案均已取得足夠證據作為參考，但 `judicial-search-tool/SEARCH_REDESIGN.md` 自身標示為 `Spec — 待實作`，且其中部分指定測試並非完整測試；本機正式案件流程也沒有把法律檢索 PoC 接入 runtime。因此只能提出有界的移植建議，不能宣稱外部流程已驗證或可直接移植。

## 1. 實際檢查證據

### 1.1 本機 `legal-case-web`

目前工作樹是 dirty，包含既有未提交變更；本次只讀取，沒有清理或覆蓋。主要檢查：

- `README.md`：正式入口、Ephemeral／Supabase 儲存、法律檢索 PoC 與 Human Gate 邊界。
- `app/server.py`：`/api/analyze`、案件 API、儲存 provider 選擇及 revision 檢查。
- `app/workflow.py`：`create_case`、`apply_action`、Gate 狀態機、快照、`set_offenses`、回答後重評估。
- `app/rules.py`：`analyze_gate1`、`candidate_offenses`、`classify_candidates`、`build_questions`、法律路由檢核。
- `app/questions.py`：`enrich_question_metadata`、`build_property_taking_questions`、`reevaluate_candidates_from_answers`。
- `app/law_reference.py`、`app/law_version.py`：離線法源快取及版本稽核。
- `app/storage.py`：`cases(case_id, revision, state, updated_at, payload)`、SQLite／Supabase revision save。
- `tests/test_candidate_semantic_safety.py`、`tests/test_workflow.py`、`tests/test_question_logic.py`、`tests/test_legal_retrieval_human_gate_packet.py`、`tests/test_pipeline_contract_and_regression.py`。

### 1.2 CAIL

檢查：`README.md`、資料欄位說明、任務說明、評估方法、基線說明，以及 repository 所列的 `CAIL2018`／`CAIL2019` 子專案入口；沒有下載資料集或執行其訓練程式。

CAIL README 說明資料來自中國裁判文書，任務一是罪名預測、任務二是法條推薦、任務三是刑期預測；資料標記包含 `fact`、`accusation`、`relevant_articles` 等欄位，並以 Micro-F1、Macro-F1 評估前兩項任務；README 所列基線為 LibSVM。參考：[CAIL README](https://github.com/china-ai-law-challenge/CAIL)。

### 1.3 `judicial-search-tool`

實際檢查：

- `src/pipeline/search.py`
- `src/pipeline/analyze.py`
- `src/pipeline/citation_normalizer.py`
- `src/pipeline/citation_extractor.py`
- `src/pipeline/filter.py`
- `src/pipeline/synonym_expander.py`
- `src/utils/anomaly_log.py`
- `schema.sql`
- `tests/test_citation.py`
- `tests/test_analyze.py`
- `tests/test_judgment_structure_regression.py`
- `README.md`
- `SEARCH_REDESIGN.md`

參考：[README](https://github.com/ksliao0314/judicial-search-tool)、[SEARCH_REDESIGN.md](https://github.com/ksliao0314/judicial-search-tool/blob/main/SEARCH_REDESIGN.md)。

## 2. 外部專案的實際能力與限制

### 2.1 CAIL：可借鑑的是評估方法，不是法律標籤

**已證實的工程概念：**

- 罪名預測與法條推薦是分開的任務，可分別計算多標籤分類指標。
- 有固定資料欄位、訓練／驗證／測試切分及競賽評估器。
- Micro-F1 適合觀察整體標籤命中，Macro-F1 可發現少數罪名類別表現被平均掩蓋的問題。

**限制：**

- CAIL 的標籤是中國裁判結果中的罪名與法條，屬判決後標籤；本機是臺灣偵查初期，輸出應是「候選方向＋未知要件＋人工審核」，不是判決結果。
- CAIL `fact` 多為裁判文書案情／事實，不能直接對應本機的報案人陳述、嫌疑人辯解、證據及系統推論等 provenance 層級。
- 中國法律法條、罪名、司法用語與臺灣刑法條文、法源版本、程序階段不同。

**結論：**只採用「罪名與法條分離的固定多標籤評估框架」；不採用 CAIL 的中國罪名清單、法條編號、裁判標籤或訓練資料作為臺灣模型目標。

### 2.2 `judicial-search-tool`：實作與規格必須分開看

#### 已由程式／測試支持的部分

- `citation_normalizer.py` 將法名、條、之、項、款、目轉為 `Citation(law, article, sub, paragraph, item, subitem)`；`covers()` 允許粗粒度查詢命中較細引用，但不把不同法名或不同項目混為同一引用。
- `citation_extractor.py` 處理複合條號、範圍、`同法` context，產生結構化引用列表；`schema.sql` 的 `task_judgments.extracted_citations` 保存該資料。
- `tests/test_citation.py` 有中文／阿拉伯條號、法名簡稱、項款、複合引用及 `covers()` 的正反例。
- `tests/test_judgment_structure_regression.py` 使用五個 parsed JSON fixture，對法院、案號、全文長度、法條數、outline 結構設下界。
- `filter.py` 現行不是原本的批次字串過濾器，而是單筆全文取得入口與全域 rate limit；檔案註記舊 `fetch_and_filter` 已移除，改由 worker stage 2.5／3 使用。
- `anomaly_log.py` 以 JSONL 記錄空欄位、長行、引號不平衡、outline 異常等 parser 訊號；寫入失敗不阻塞抓取。
- `synonym_expander.py` 將 LLM discovery、corpus hit 驗證及 `confirmed/candidate/likely_typo/rejected` tier 分離；只有人工確認的 `confirmed` 進自動搜尋。
- `analyze.py` 將 per-judgment score 與 synthesis 分開，使用不同模型／token bucket，並保留重試與錯誤結果。

#### 不能當成已完成能力的部分

`SEARCH_REDESIGN.md` 第 192 行明確寫 `Status: Spec — 待實作`。其 Stage 1 廣搜、Stage 2 純前端收斂、Stage 3 精讀、`task_search_hits` 及 worker 拆分，應視為設計方向；不能因文件描述完整就宣稱目前 runtime 已實作全部流程。文件自己也列出 Stage 2 狀態持久化、cache、超過 5000 筆 UX 等後續事項。

此外，`tests/test_analyze.py` 目前只有測試模組說明字串，沒有可用來證明 Claude 分析完整行為的實質 assertion。故 `analyze.py` 的程式設計可列為靜態證據，但不能把該測試檔列為完整 runtime regression proof。

## 3. 本機端到端流程與差距

目前正式流程可概括為：

```text
HTTP /api/analyze 或案件建立
  → workflow.create_case
  → rules.analyze_gate1(use_ai=False)
  → Gate 1 facts / acts
  → rules.candidate_offenses
  → legal route / element matrix / candidate status
  → Gate 2 set_offenses
  → rules.build_questions + questions.enrich_question_metadata
  → interviews / answers
  → questions.reevaluate_candidates_from_answers
  → workflow snapshots / approvals / documents
  → SQLite 或 Supabase payload（依部署設定）
```

### 3.1 Fact／Evidence

- `analyze_gate1` 會產生 deterministic facts，保留 `fact_id`、`source_ref`、`source_excerpt`、`assertion_status`、`machine_status`、`review_status`；目前 `FACT` 仍表示來源文字有明示內容，不等於已查證為真。
- 本機已有 typed Gate facts 與來源陳述欄位，但來源類型、主張類型、證據查證狀態仍需以一致契約解讀；空 `fact_key` 不應被補成推測分類。
- 本次看到的 `analysis_contract.py` 是工作樹中的相容適配層，並非已部署或外部獨立服務；其存在不能替代正式資料庫／API trace 的端到端證據。

### 3.2 Candidate／route／review

- `candidate_offenses` 先用規則／關鍵詞建立候選，再連結 route element matrix、支持／未知要件及 `legal_route_states`。
- `ELIGIBLE_CANDIDATE` 是路由可進入分析的狀態，不是犯罪成立；`NEED_REVIEW` 是候選待審狀態；`HUMAN_REVIEW_REQUIRED` 多處是法源／路由人工覆核狀態。
- parent offense、child legal route、candidate status 與 human review 在資料結構中已有不同欄位，但歷史兩套專案的 enum 仍不完全相容；這正是先前第337／第320輸出無法僅靠名稱比較的原因。
- 現有規則已加入構成要件矩陣與候選排序因素，但來源候選仍可由關鍵詞提示觸發；因此關鍵詞只能是 recall 入口，不能作為成立或唯一順位依據。

### 3.3 LegalNorm retrieval／validation

- `law_reference.py` 使用離線 `data/law_reference_cache.json`；`law_version.py` 提供版本快照／條文稽核。
- README 明確把法律檢索／罪章關聯標為離線 PoC，未完成 Human Gate 不接入 runtime。這表示目前有法源版本與人工覆核邊界，但沒有外部專案那樣的通用 citation extractor + persisted extracted citation pipeline。

### 3.4 問句與回答重評估

- `questions.py` 已有 `fact_target`、`legal_targets`、`target_elements`、`purpose`、`trigger_condition`、`evidence_to_verify`。
- `reevaluate_candidates_from_answers` 會依答案更新 candidate unknown／supported elements；workflow 另保存 interviews、route overlays、snapshots。
- 目前最接近外部專案的優點是「問句指向事實缺口」；尚缺的是把每次回答、觸發條件、候選狀態變化與 revision 以同一 trace envelope 固定保存，讓第一個差異階段能被 API／UI 重播直接觀察。

### 3.5 儲存、版本、測試追溯

- SQLite `cases` 表以整個 encrypted payload 保存一筆案件及 revision；Supabase gateway 也以 revision compare-and-save 防止競態。
- `snapshots`、`audit`、`approvals` 在案件 payload 內保存，但不是外部專案那種「每個搜尋 hit／全文／分析結果分表且可重用」的查詢資料模型。
- 現有測試覆蓋候選語義安全、workflow、問句、法律 Human Gate、fixture regression；先前新增的 replay／diff 工具可定位純函式差異，但原始歷史輸出仍無 request／revision／模型輸入 trace。

## 4. 借鑑評估表

| 項目 | 外部專案的實際實作或規格 | 本機現況 | 適用程度 | 建議 |
|---|---|---|---|---|
| 法條結構化比對 | `Citation` 六欄、`covers()`、複合引用 extractor；有 `test_citation.py` | 有法源 cache／版本稽核，但沒有同等通用 citation tuple pipeline | 高 | 沿用概念，做臺灣法名／條項款格式的本機適配；先測試再接 runtime |
| 法源檢索 | search adapter、citation normalization、extracted citations、來源 domain adapter | 檢索 PoC 與 Human Gate，尚未接正式 runtime | 中高 | 先建立離線 retrieval bundle，通過 Human Gate 後才接候選分析 |
| 候選罪名產生 | CAIL 是判決後多標籤預測；judicial tool 是關鍵字召回，不是罪名判定 | 規則候選＋要件矩陣＋route review | 中 | 只借鑑候選／法條分離與離線評估；不把外部 score 當法律機率 |
| 問句生成 | judicial tool 主要是法律檢索 AI 精讀，不是偵查筆錄問句系統 | 已有 fact target、element、trigger、回答重評估 | 低中 | 不移植其 prompt；借鑑可追蹤 evidence excerpt 與 stage trace |
| 來源追溯 | `task_search_hits`、`task_judgments`、`analysis_results`、extracted citations | facts、snapshots、payload revision 已有，但缺端到端 trace envelope | 高 | 新增只讀 trace/export 契約；保存原文、版本、候選、問句、回答與狀態變更 |
| 回歸測試及異常紀錄 | citation unit tests、五案結構 fixture、JSONL anomaly log | 多數 workflow／question regression 已有；第一差異 trace 尚未正式 runtime 化 | 高 | 引入固定案件 fixture、逐階段 snapshot、異常事件 ID；不要只測最終候選名稱 |
| 資料庫及版本 | 外部 schema 分離 tasks/hits/judgments/analyses/results，含 unique/index/cache key | 本機 cases payload + revision，安全與 revision 控制較集中 | 中 | 不直接改 schema；先以 export/read model 驗證是否需要分表 |

## 5. 建議採用與不採用

### 建議採用前三項

1. **法條 citation 結構化正規化與精確核對**：把法律檢索的 recall 與 citation precision 分離，並保留命中／未命中的理由與原文摘錄。
2. **罪名與法條分離的固定多標籤評估集**：建立臺灣法域、偵查初期語境、含未知／矛盾／人工 Gate 的 fixture；至少報告 Micro-F1、Macro-F1、候選召回、未知保留率及錯誤首次階段。
3. **可重播的分階段 trace 與異常紀錄**：借鑑 `task_search_hits`／`analysis_results` 的分層思路及 JSONL anomaly log，但以本機 `case_id/revision_id`、fact／candidate／route／question IDs 為主鍵。

### 明確不採用

- 不採用 CAIL 的中國罪名、法條、裁判結果標籤或資料集作臺灣訓練目標。
- 不把 judicial-search-tool 的 0–10 分、支持／反對標籤直接當候選罪名順位、犯罪成立程度或法律機率。
- 不把 `SEARCH_REDESIGN.md` 的待實作 Stage 1–3 當現成 runtime。
- 不以 LLM 同義詞 discovery 自動新增罪名關鍵字、法條規則或候選順位；只允許人工確認後進入檢索詞庫。
- 不直接移植其 MCP／Claude／外部 cache／API adapter 到正式案件分析流程。

## 6. 最小修改順序（本次未執行）

1. **先建立臺灣法條 citation contract**：輸入法名、條、之、項、款、目；輸出 canonical citation、來源文字 span、parser version、validation status。
2. **建立離線 retrieval bundle**：查詢、原始結果、正規化引用、法源版本、人工核准狀態、hash；不接正式案件候選。
3. **擴充固定回歸 fixture**：基準案、持有狀態變化、主觀意圖未知、來源矛盾、法條否定句、複合引用；每一階段保存 JSON snapshot。
4. **把 trace 接到 workflow 邊界**：`case_id/revision_id/request_id` 貫穿 facts、candidates、routes、questions、answers、documents；禁止用自由文字理由取代結構化狀態變更。
5. **再做候選評估**：先比較 recall／unknown preservation／route review，不先追求與外部專案的最終名稱一致。
6. **最後才評估 schema read model**：若查詢與重播需要，再將 facts／candidate events／retrieval hits 分離讀模型；保留現有 encrypted payload 與 snapshots 相容性。

## 7. 建議回歸測試

- `test_citation_normalization_taiwan.py`：阿拉伯／中文條號、條之、項款目、`同法`、複合條號、否定句。
- `test_candidate_fact_provenance.py`：報案人陳述、嫌疑人辯解、客觀證據、推論、未知不得互相升格。
- `test_candidate_route_contract.py`：候選、法條 route、parent、review status 不得混用；`ELIGIBLE_CANDIDATE` 不等於核准。
- `test_trace_first_divergence.py`：比較 raw input → facts → candidate → route → questions → answer reevaluation → output，定位第一次差異。
- `test_revision_replay.py`：同一案件不同 revision 不得讀錯候選／問句／法源版本。
- `test_retrieval_anomaly_regression.py`：空全文、長行、引用不平衡、parser version 漂移必須留下 anomaly，不能靜默通過。
- `test_metric_report.py`：臺灣 fixture 報告 Micro-F1、Macro-F1、候選召回、未知保留率、route precision；這些是工程評估，不是法律正確率證明。

## 8. 尚未核實事項

- 未執行 CAIL 訓練、評估器或任何資料集操作；因此只核實 README／評估規格，未核實模型實際表現。
- 未執行 `judicial-search-tool` 外部 MCP、Claude、worker、資料庫 migration 或完整 API；外部網頁原始碼與指定測試已讀取，但 runtime 行為未在本機重播。
- `tests/test_analyze.py` 缺少實質 assertion，不能證明 `analyze.py` 的 API retry、score、synthesis 在所有路徑都通過。
- 本機正式案件的歷史 request、UI/API trace、LLM prompt、法源檢索結果及 revision 混用問題仍未取得端到端證據。
- 未驗證任何外部設計對臺灣刑事偵查筆錄的法律適切性；需要法律專業人工 Gate。

## 9. 是否具備進入修改階段

**具備進入「離線 citation contract／trace fixture 設計」階段的條件；不具備直接修改候選罪名規則或把外部 AI pipeline 接入正式 runtime 的條件。**

進入下一階段前仍應取得：固定臺灣法源資料與版本、人工核准的測試標籤、隔離 retrieval fixture、完整 request/revision trace，以及法律專業對候選與問句契約的審核。
