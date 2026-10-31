# Agent Verification Loop（對齊 poteto/pstack 精神）

> 狀態：**骨架已落地，完整自主多 Agent 循環尚未宣稱完成。**
> CI 通過 = 工程證據，不是法律正確或影片級產線已達成。

## 影片核心 vs 本專案

| 作法 | 本專案 | 說明 |
|------|--------|------|
| 工作方法 → Skills | ✅ | `AGENTS.md`、`.agents/skills/`、`skills/playbooks/` |
| 可判定工作 → 程式 | 🟡 | MCP 狀態分類、quality_gate、traceability、competing_hypotheses |
| Agent 執行並驗證 | 🟡 | 本文件 + `agent_loop.py` 定義步驟；**live MCP 呼叫仍依執行環境** |
| 錯誤 → 修正環境／規則 | 🟡 | `error_sediment` 紀錄；人工核准後才改 skill/test |
| 多 Agent 分工 | ❌ 未完整 | 僅角色建議，無內建 orchestrator |
| 人工抽查 | ✅ | Human Gate、revision fail-closed 保留 |

## 強制循環（單次任務）

```text
1. PLAN     選 skill / playbook（taiwan-law-mode）
2. EXECUTE  呼叫工具或模組（MCP / pytest / 腳本）
3. OBSERVE  讀取可觀察結果（回傳、exit code、log）
4. VERIFY   mcp_verification / quality_gate / tests
5. DECIDE   PASS | RETRY | FAIL_CLOSED | NEEDS_HUMAN
6. SEDIMENT 若同一 pattern ≥ N 次 → 提案 skill/test（不自動 merge）
```

### Fail closed 規則

- `MCP_UNAVAILABLE`：不得用模型記憶補法條。
- 測試失敗：不得刪測或把 BLOCKED 改 PASS。
- 法律結論：永遠 NEED_REVIEW / 人工。

## 程式入口

- `legal-case-web/app/agent_loop.py` — 步驟狀態機與 sediment 紀錄結構
- `legal-case-web/app/mcp_verification.py` — 法源查證狀態
- `tools/check_skill_discovery.py` — Skills 是否可被發現
- `tools/run_agent_verify_subset.sh` — 本機／CI 子集驗證

## 多 Agent 角色（建議，非 runtime）

| 角色 | 職責 |
|------|------|
| Planner | 選 playbook、拆任務 |
| Worker | 執行檢索／模組 |
| Verifier | 只跑檢查，不改業務結論 |
| Sediment reviewer | 人類：是否把錯誤變成 skill/test |

同一時間僅一個 agent 改同一組核心檔；變更走 branch + PR。

## 下一步（未完成）

1. 在真實 MCP adapter 呼叫點寫入 `mcp_verification_log`。
2. 本機 agent（Cursor/Codex）固定以 `verify-and-sediment` skill 收尾。
3. Gold dataset + 指標，避免只靠 Gate 走完。
4. 可選：輕量 orchestrator（仍須 Human Gate）。
