# LEGAL-PIPELINE-FIX-005 未決問題

## 根因狀態

- `UNKNOWN`：原始「第337條 CANDIDATE／第320條 NEEDS_FACTS」沒有可識別 request ID、revision、完整模型輸入或 API trace，尚不能宣稱已找到歷史輸出的唯一根因。
- `FACT`：正式 `legal-case-web` 的目前本機規則鏈是 `create_case → analyze_gate1(use_ai=False) → candidate_offenses → build_questions`；CIA 不在此呼叫鏈。
- `FACT`：關鍵詞目前仍可觸發檢索候選，但本次已將候選次序主要依構成要件矩陣的回查支持數，並保留未知事項與人工審核狀態。
- `CONTRIBUTING_FACTOR`：兩套專案仍有不同資料模型與 status enum；本次沒有為了表面一致修改 CIA。

## 尚未確認

1. 正式案件是否曾讀取歷史 revision 或舊候選結果。
2. 第337條是否來自另一個未納入 `legal-case-web` 的 API、UI 或舊版服務。
3. 外部 LLM、法律檢索或 cache 是否參與原始結果。
4. `source_type` 是否需要由日後正式證據表提供更細的來源分類；目前摘要分段只安全地保留為陳述／未知。

## 最小下一步

在隔離環境建立一筆固定 `case_id/revision_id` fixture，啟用持久化 store 的讀回比對，並保存 API request、candidate intermediate list、route states 與 final response；同時以固定 Prompt/model/retrieval 做三次 replay。完成前不得修改正式 DB 或宣稱原始根因已確認。

## 修正前不得破壞

既有舊欄位、題庫版本、人工 Gate、歷史 snapshots、`fact_key` 空值語義、候選 route review 及前端相容 API。

## Citation contract 未決事項

- `app/citation_contract.py` 目前只使用小型人工核准法規簡稱表；未接入 `law_reference_cache.json` 或正式法源服務，避免把離線 parser 誤當法源適用判斷。
- `同法` 只在同一輸入且前文可解析到已核准法規名稱時解析；跨段落或跨文件 context 仍回報不完整，不能猜測。
- parser 不處理否定／肯定立場；`stance_status=NOT_ANALYZED`，需由獨立語句分析流程處理。
- `LEGAL_TRACE_FIXTURE.json` 是人工定義的 fixture，不是實際案件、LLM、DB 或 API trace。
- 尚未建立正式整合 adapter；若日後整合，需先完成 citation contract 的法律人工審核、法源版本綁定與 read-only trace export。

## Trace-first 評估器未決事項

- `FACT`：5 案重播的首個差異均在 facts；來源句段雖被保留，但 `original_possession`、`intent` 等 typed key 與 `UNKNOWN` 語義沒有完整進入下游契約。
- `FACT`：D 案的 `DENIED` 與監視器 evidence summary 未被抽取成兩個可追溯且互相矛盾的事實。
- `FACT`：baseline 與 B 未保留第337條 parent route 為 required candidate；這是本版規則輸出與 draft gold 的差異，不等於已證明歷史輸出的根因。
- `UNKNOWN`：5 案 gold 尚待法律人工覆核；目前只能作初始回歸基線，不能作整體法律正確性證明。
- `UNKNOWN`：行為時間與歷史法版本適用性；離線來源 metadata 不足以判定 applicable law version。
- `NOT_RUN`：正式 HTTP、資料庫 revision、LLM、檢索、前端映射及歷史輸出重播。

最小後續修改應先針對 Gate 1 typed fact contract 與矛盾保留，新增人工核准案例後再調整候選／要件邏輯；在此之前不應把 sidecar 接入正式 Runtime 或讓檢索命中提高候選順位。
