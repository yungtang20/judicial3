# Playbook：驗證與沉澱

1. 載入 skill `verify-and-sediment`。
2. 收集 observations（工具、測試、MCP status）。
3. 決策：FAIL_CLOSED / RETRY / NEEDS_HUMAN / PASS。
4. 反覆錯誤 → sediment 提案；人工核准後另開 PR。
