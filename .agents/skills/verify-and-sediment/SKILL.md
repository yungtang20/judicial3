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

1. **OBSERVE**：列出實際執行過的工具／指令與結果（exit code、MCP status、log 摘要）。
2. **VERIFY**：
   - 有法源引用 → 必須有 mcp_verification 狀態
   - `MCP_UNAVAILABLE` → FAIL_CLOSED，不得補造條文
   - 建議跑：`python tools/check_skill_discovery.py`、相關 pytest
3. **DECIDE**：PASS | RETRY | FAIL_CLOSED | NEEDS_HUMAN（法律結論永遠可標 NEEDS_HUMAN）
4. **SEDIMENT**（可選）：同一錯誤模式重複出現 → 寫明「建議新增的 skill 或測試」；**不要**直接改 main。

## 禁止

- 把 CI／單元測試通過寫成法律驗收
- 刪測試、把 BLOCKED 改 PASS
- 未核准就新增 skill 並宣稱已解決
