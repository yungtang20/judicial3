# LEGAL-PIPELINE-FIX-005 實作報告

## 正式路徑

`FACT`：`legal-case-web/README.md` 指定 `start.ps1 → app.server → app.workflow`；`app/server.py` 的 `/api/analyze` 走 `_local_analysis_payload`，案件建立走 `workflow.create_case`。`legal-case-web` 沒有 import 或呼叫 `criminal-investigation-assistant`，所以本次只修改正式專案。

## 已修改

- `app/analysis_contract.py`
  - 新增純函式契約適配：事實來源、主張類型、查證狀態、空 `fact_key` 分類、provenance。
  - 分離候選 `candidate_status`、`readiness_status`、`candidate_review_status`、`route_status` 及事實／證據引用。
  - 將既有問句 metadata 映射為 `gap_id`、`candidate_ids`、`element_ids`、`question_type`、`follow_up_condition`。
- `app/workflow.py`
  - 在案件建立與每次 action 重算後套用契約。
  - `_clean_fact` 接受並驗證明確的 `ASSERTED`／`ADMITTED`／`DENIED`／`INFERRED`／`UNKNOWN`；不由文字猜測。
  - 保留舊欄位與狀態；revision 0 的純函式結果不注入隨機 case ID，避免破壞 deterministic tests。
- `app/rules.py`
  - 新增 `candidate_rank_factors`，排序先採構成要件矩陣的可回查支持數，再以未知要求數與關鍵詞數作穩定次排序。
  - 關鍵詞仍是檢索提示，沒有被提升為犯罪成立或法律機率。
- `tests/test_pipeline_contract_and_regression.py`
  - 覆蓋基準案及 A-D，並驗證 ADMITTED／DENIED 不被改寫。
- `tools/validate_pipeline_contract.py`
  - 可直接執行的隔離本機驗證腳本，不連接 LLM、DB、HTTP 或雲端。

## 未修改

未修改 CIA、資料庫 schema/migration、Prompt、外部服務、前端及既有題庫文字。

## 行為界線

本次不宣稱第320條或第337條成立，也不把 `ELIGIBLE_CANDIDATE`、`HUMAN_REVIEW_REQUIRED` 或 `NEEDS_FACTS` 互相等同。實際基準重播仍顯示 legal-case-web 規則候選為 `theft`，`readiness_status=NEEDS_FACTS`；這是目前正式本機規則輸出，不是原始歷史輸出的重現。

## LEGAL-CITATION-CONTRACT-001 離線追加

- `app/citation_contract.py`：新增獨立臺灣法條 citation mention parser；不被正式 workflow import。
- `LEGAL_CITATION_CONTRACT.md`：文件化 Citation Mention、Legal Source、Applicability Candidate、Applied Legal Basis 四層分離。
- `LEGAL_CITATION_FIXTURE.json`：12 個人工定義 citation cases、15 個預期 mentions及版本漂移案例。
- `LEGAL_TRACE_FIXTURE.json`：超商拾得手機案，明確保留來源陳述、監視器未驗證資料、未知持有／意圖、320／337候選及核心問句。
- `tests/test_citation_contract.py`：9 項離線 citation／案件 trace regression。
- `tools/validate_citation_contract.py`：可直接執行，不使用 LLM、DB、MCP、HTTP 或 cloud。

本次未修改正式候選產生、排序、Prompt、Schema 或案件 workflow；原始第337／第320偏差根因仍為 `UNKNOWN`。

## Trace-first 臺灣離線評估 sidecar

- `LEGAL_EVALUATION_CONTRACT.md`：定義 Fact → Legal Element → Candidate → Question 追蹤、六項指標、hard gates、法律來源時間與 gold/DUT 分離。
- `LEGAL_EVALUATION_FIXTURE.json`：5 個超商手機案及反事實變體；人工 gold 為 `DRAFT_INITIAL_REGRESSION_BASELINE`，審核狀態 `PENDING_HUMAN_REVIEW`。
- `tools/legal_evaluation_replay.py`：實際重播 `analyze_gate1(use_ai=False) → candidate_offenses → build_questions`；主要候選 lane 只使用 raw summary，不注入 gold facts。
- `tests/test_legal_evaluation_replay.py`：候選 K 邊界、prohibited、gold mutation、來源 span、UNKNOWN promotion、citation-only perturbation、跨 process determinism。
- `LEGAL_EVALUATION_TRACE.json`、`LEGAL_EVALUATION_REPORT.md`：保存實際中間資料、版本 hash、首個差異階段與量化結果。

問句評估使用獨立 gold-selected parent/route，避免將所有自動候選當成人工核准方向。正式 Runtime、候選規則、Prompt、Schema、題庫及資料庫均未修改。
