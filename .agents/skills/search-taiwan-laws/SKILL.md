---
name: search-taiwan-laws
description: |
  查詢台灣現行法規。必須實際呼叫 taiwan_law_mcp___search_taiwan_laws，不得憑記憶撰寫條文。
  呼叫成功 ≠ 法律適用正確；需標 VERIFIED / NOT_FOUND / MCP_UNAVAILABLE / VERSION_UNVERIFIED。
---

# 查詢台灣法規（強制 MCP）

1. 呼叫 `taiwan_law_mcp___search_taiwan_laws`（query 必填；可選 article_number、limit、include_history）。
2. 依回傳整理法規、條號、要旨、source_url；寫入 verification 紀錄（provider、tool、status、retrieved_at、source_url、case_revision）。
3. 無結果 → NOT_FOUND + `[待檢索]`；工具不可用 → MCP_UNAVAILABLE，**fail closed**（不得用模型記憶補條文）。
4. 有條文但未對事件日核對沿革 → VERSION_UNVERIFIED。
5. 輸出必須附 source_url，提醒人工核對最新版本。
