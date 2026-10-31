---
name: search-taiwan-judgments
description: |
  搜尋司法院公開裁判。觸發於需要實務見解、類似案由、主文關鍵字時。
  必須呼叫 taiwan_law_mcp___search_taiwan_judgments；取全文再用 get_taiwan_judgment。
---

# 搜尋台灣裁判（強制 MCP）

## 步驟

1. 整理 query（案由關鍵字）、可選 court、case_type（民事／刑事／行政）、year、case_word + case_number、main_text。
2. **呼叫**：
   ```
   taiwan_law_mcp___search_taiwan_judgments
   ```
3. 結果按法院層級整理；每筆保留法院、案號、日期、案由、JID（若有）。
4. 需要全文時再呼叫 `taiwan_law_mcp___get_taiwan_judgment`（jid 必填）。
5. 無 JID 的候選僅供瀏覽，**不得**直接當成確定裁判見解引用。
6. 無結果時標 `[待檢索]` 並說明。

## 輸出要點

- 列 3–10 筆精選，附 JID／官方可追溯資訊
- 明確區分「檢索命中」與「已讀全文」
- 不將裁判寫成具普遍拘束力的「判例」除非使用者特別要求並核實
