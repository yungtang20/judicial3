# Architecture Gap Report

日期：2026-10-31  
基準：`70c036b` + `feat/agent-verification-loop`

## 與 poteto 影片對照（誠實狀態）

| 作法 | 狀態 |
|------|------|
| Skills 可重複 | ✅ 根 AGENTS + `.agents/skills/` |
| 可判定工作程式化 | 🟡 MCP 分類、gate、trace、hypotheses |
| Agent 執行並驗證 | 🟡 `agent_loop.py` + verify-and-sediment skill；**live 全自動循環未宣稱** |
| 錯誤沉澱為規則 | 🟡 僅提案結構，人工核准 |
| 多 Agent 協調 | ❌ 未完整 |
| 人工抽查 | ✅ Human Gate |

## Stage2 已合併

- mcp_verification、competing_hypotheses、question_traceability 擴充、RUNTIME_STORAGE_BOUNDARY、skill discovery 腳本

## Agent loop 分支新增

- `docs/AGENT_VERIFICATION_LOOP.md`
- `app/agent_loop.py` + tests
- `.agents/skills/verify-and-sediment`
- CI 增加 skill discovery + stage2/agent_loop pytest 子集

## 仍未完成

- 生產路徑強制寫入 mcp_verification_log
- Gold dataset 與法律推理指標
- 多 agent orchestrator
- README 測試數字與最新 CI 對齊（須等 Actions 跑完再改）

測試通過 ≠ 法律驗收。
