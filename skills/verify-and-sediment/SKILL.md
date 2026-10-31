---
name: verify-and-sediment
description: |
  任務收尾：執行驗證循環（觀察結果 → 判定 PASS/RETRY/FAIL_CLOSED/NEEDS_HUMAN）。
  反覆錯誤僅「提案」寫入 skill/test，須人工核准，禁止自動 merge 或刪除失敗測試。
  對應 docs/AGENT_VERIFICATION_LOOP.md 與 app/agent_loop.py。
---

# verify-and-sediment

## 何時使用

任何 taiwan-law-mode 產出、MCP 呼叫、或修改程式後。

## 步驟

1. **OBSERVE**：列出實際執行過的工具／指令與結果。
2. **VERIFY**：有法源引用必須有 mcp_verification；MCP_UNAVAILABLE → FAIL_CLOSED。
3. **DECIDE**：PASS | RETRY | FAIL_CLOSED | NEEDS_HUMAN。
4. **SEDIMENT**：重複錯誤 → 只提案 skill/test，不直接改 main。

## 禁止

- 把 CI 通過寫成法律驗收
- 刪測試、把 BLOCKED 改 PASS
