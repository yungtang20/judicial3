# JUDICIAL3 MVP 差距矩陣

日期：2026-10-29。判定以程式碼及實際執行測試為準。

| MVP 能力 | 狀態 | 實際入口／檔案 | 證據 | 剩餘缺口 | 優先級 |
|---|---|---|---|---|---|
| 建立與分析案件 | `PASS` | `src/services/legalReasoningEngine.ts`、`src/App.tsx` | 14 情境及 corrective test 通過 | UI 建案仍以本機分析入口為主 | P0 |
| 原始案情保存與重新讀取 | `PASS` | `database/migrations/0010_mvp_traceability.sql`、`databaseService.ts` | `mvp_complete_flow.test.ts` 驗證 raw_text round-trip | 正式部署登入流程尚未完成 | P0 |
| Fact／Evidence 分離 | `PASS` | `src/types/index.ts`、`databaseService.ts` | 完整流程測試保存 3 Facts、1 Evidence 並保留 PENDING_SEARCH | Evidence 的文件實體與保管鏈仍是欄位級 MVP | P0 |
| 候選與要件追溯 | `PASS` | `offenseRegistry.ts`、`legalReasoningEngine.ts` | corrective test、完整流程測試 | 非 registry 舊案型仍需逐步遷移 | P0 |
| UNKNOWN／DENIED／INFERRED | `PASS` | `legalReasoningEngine.ts` | 14 情境、corrective test | 無 | P0 |
| 竊盜／侵占區辨 | `PASS` | property registry | 超商手機反事實測試 | 法律版本仍須行為時人工核對 | P0 |
| 傷害／恐嚇／殺人未遂基本方向 | `PASS` | violence registry | corrective violence test、14 情境 | 非完整罪章覆蓋 | P1 |
| 問句人工修改保存 | `PARTIAL` | `App.tsx`、`databaseService.ts` | 問句可送入保存 API，欄位已保存 | 尚缺獨立 UI 的刪除／新增問句操作測試 | P1 |
| Fact 修改與 revision | `PASS` | `invalidateDownstreamOnFactChange` | corrective test、完整流程 revision 1→2 | UI 修改後需更完整串接歷史快照顯示 | P0 |
| API 認證與 owner 隔離 | `PASS` | `src/server/auth.ts`、`server.ts` | API auth test、actual server route test、完整流程 owner isolation | 正式登入服務與 token rotation 未完成 | P0 |
| 資料庫失敗保護 | `PASS` | `databaseService.ts` | 既有 scenario 13、初始化 fail-closed 實作 | 真實 PostgreSQL 尚未測試 | P0 |
| 完整保存／讀取流程 | `PASS` | `tests/mvp_complete_flow.test.ts` | 實際臨時 PGlite：create/save/read/revise/traceability/isolation | 無 | P0 |
| Production build | `PASS` | `package.json`／Vite | `npm run build -- --emptyOutDir` exit 0 | Vite config 有 native loader warning | P1 |
| 參考研究 | `PARTIAL` | `docs/MVP_REFERENCE_RESEARCH.md` | 官方法規、CIB、GitHub 來源實際讀取 | TaiLexi timeout、LawBank inaccessible | P1 |

## 判定

目前 P0 的本機 MVP 核心流程已具備可重現證據；整體仍不是正式部署安全性 `PASS`，因正式登入、真實 PostgreSQL/RLS 與部分來源仍未驗證。
