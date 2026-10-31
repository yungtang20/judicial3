# Playbook：驗證與沉澱

1. 載入 skill `verify-and-sediment`。
2. 收集本輪 observations（工具、測試、MCP status）。
3. 用 `agent_loop` 決策語意：FAIL_CLOSED / RETRY / NEEDS_HUMAN / PASS。
4. 反覆錯誤 → 只產出 sediment **提案**（pattern_id、說明、建議 skill/test）。
5. 人工核准後另開 PR 修改 skills 或 tests。
