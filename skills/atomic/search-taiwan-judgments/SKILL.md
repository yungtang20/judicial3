---
name: search-taiwan-judgments
description: |
  搜尋司法院公開裁判。觸發於需要實務見解、類似案由、主文關鍵字時。
  必須實際呼叫 MCP 工具（見下方工具名），取全文再用 get_taiwan_judgment / get_judgment。
---

# 搜尋台灣裁判（強制 MCP）

本技能可用兩個 MCP 來源，依可用性擇一：
- 遠端 `legaltech.org.tw/mcp`：`search_taiwan_judgments`、`get_taiwan_judgment`。
- 本地 `mcp-taiwan-legal-db`（stdio，需設 `JUDICIAL3_MCP_LOCAL`）：`search_judgments`、`get_judgment`。

## 步驟

1. 整理 query（案由關鍵字）、可選 court、case_type（民事／刑事／行政）、year、case_word + case_number、main_text。
2. **呼叫工具**（任一可用即可）：
   - 遠端：`search_taiwan_judgments`，參數：query、court、case_type、year_from、year_to、case_word、case_number、main_text、limit。
   - 本地：`search_judgments`，參數：keyword、court、case_type、year_from、year_to、case_word、case_number、main_text、limit。
3. 結果按法院層級整理；每筆保留法院、案號、日期、案由、JID（若有）。
4. 需要全文時再呼叫 `get_taiwan_judgment`（遠端）或 `get_judgment`（本地）（jid 必填）。
5. 無 JID 的候選僅供瀏覽，**不得**直接當成確定裁判見解引用。
6. 無結果時標 `[待檢索]` 並說明。

## 輸出要點

- 列 3–10 筆精選，附 JID／官方可追溯資訊
- 明確區分「檢索命中」與「已讀全文」
- 不將裁判寫成具普遍拘束力的「判例」除非使用者特別要求並核實
- MCP 不可用時回報 MCP_UNAVAILABLE，fail closed，不得以模型記憶補裁判要旨。
