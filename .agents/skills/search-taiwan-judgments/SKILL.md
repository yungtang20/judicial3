---
name: search-taiwan-judgments
description: |
  搜尋司法院公開裁判。必須呼叫 taiwan_law_mcp___search_taiwan_judgments；全文用 get_taiwan_judgment。
  無 JID 不得當成確定裁判見解；MCP 成功 ≠ 見解可直接適用本案。
---

# 搜尋台灣裁判（強制 MCP）

1. 呼叫 search_taiwan_judgments；需要全文再 get_taiwan_judgment(jid)。
2. 保留法院、案號、日期、案由、JID；verification status 同上。
3. 無 JID 僅供瀏覽；無結果 NOT_FOUND；不可用 MCP_UNAVAILABLE fail closed。
