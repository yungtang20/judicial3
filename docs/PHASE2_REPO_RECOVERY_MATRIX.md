# Phase 2 Repository Recovery Matrix

| 項目 | 基準 | Phase 2 來源 | 納入 | 測試／風險 |
|---|---|---|---|---|
| 專案根目錄 | GitHub `judicial3` / `6505a2c` | `D:\工作用\judicial3` TypeScript project | YES | 結構與 remote main一致 |
| 案件保存／重開／revision | main MVP | session 16:39–17:07 patches | YES | PGlite flow PASS |
| Fact/Evidence/element/question | main traceability | migration 0010、DB service、App | YES | 14/14、corrective、flow PASS |
| 問句回答分離 | main 無完整 acceptance fix | engine/App/DB/migration patches | YES | corrective/flow PASS |
| 320/337 statute mapping | main 初版 | statute parser與 snapshot restore | YES | flow與 UI code檢查 |
| External AI fail closed | main可設定 key | server gate/model config | YES | route 503 PASS |
| API auth/owner isolation | main HMAC初版 | route與owner regression | YES | auth/route/owner PASS |
| Production start | `node server.ts` | `tsx server.ts` | YES | build/start PASS |
| Phase 2 reports/audit | 原始工作目錄未追蹤 | 17:06 patch與 JSONL | YES | audit重新執行 |
| Phase 3 auth/DB/deploy | 不在 Phase 2 | 17:21 後 patches | NO | 明確排除 |
| `package-lock.json` | main 不存在 | Phase 2/3 混合生成物 | NO | `AMBIGUOUS`；使用 bun frozen lock |
| `legal-case-web` 等錯誤專案 | 錯誤分支 `641c2f0` | `D:\工作用\judicial1` | NO | `UNRELATED`，未混入 |

完整逐檔分類見 `PHASE2_PHASE3_FORENSIC_MATRIX.md`。
