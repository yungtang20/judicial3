# Phase 2 重建後測試證據

環境：Windows、Node `v24.17.0`、Bun `1.4.2`。依賴安裝使用 `bun install --frozen-lockfile` → exit 0。`npm install --ignore-scripts` 曾因 Vite 8.3.5 與直接 `esbuild ^0.25.0` peer resolution 衝突 exit 1，因此未產生或提交不可靠的 npm lock。

| 驗證 | 命令 | Exit | 結果 |
|---|---|---:|---|
| TypeScript | `bun run lint` | 0 | PASS |
| 14 法律情境 | `bunx tsx tests/legal_reasoning_scenarios.test.ts` | 0 | PASS，14/14 |
| Corrective | `bunx tsx tests/legal_reasoning_corrective.test.ts` | 0 | PASS |
| API auth | `bunx tsx tests/api_auth.test.ts` | 0 | PASS |
| Production route auth | `bunx tsx tests/api_route_auth.test.ts` | 0 | PASS，未登入 401／AI 關閉 503 |
| PGlite 流程／revision | `bunx tsx tests/mvp_complete_flow.test.ts` | 0 | PASS |
| Owner isolation | `bunx tsx tests/api_owner_isolation.test.ts` | 0 | PASS |
| Production build | `bun run build` | 0 | PASS；Vite native config warning 不影響輸出 |
| Production start | `bunx tsx tests/production_start.test.ts` | 0 | PASS；在 build 後重跑 |
| Phase 2 audit | `python tools/judicial3_mvp_audit.py` | 2 | `33 PASS / 0 FAIL / 3 NOT_RUN / 2 BLOCKED`；exit 2 代表保留環境阻擋 |
| Predeploy audit | `python scripts/audit_predeploy.py` | 0 | PASS（8 PASS，2 NOT_RUN/BLOCKED） |
| Legal goal audit | `python tools/legal_reasoning_goal_audit.py` | 0 | PASS（33/33） |
| Diff whitespace | `git diff --check` | 0 | PASS |

Production start 首次在尚未 build 時執行，因缺少 `dist` 而失敗；完成 production build 後依正確順序重跑 exit 0。此失敗與重跑均保留，不把前次失敗隱藏為 PASS。

Phase 2 audit 的 `NOT_RUN`：可重跑 browser E2E、真實 PostgreSQL、Render。`BLOCKED`：正式 auth/revoke、外部法律檢索。這些限制與原 Phase 2 報告一致，未以本機測試升級成 production readiness。
