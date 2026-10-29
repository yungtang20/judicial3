# JUDICIAL3 MVP 測試結果

日期：2026-10-29。以下為本次修改後實際執行結果。

| 命令 | 結果 |
|---|---|
| `node_modules/.bin/tsc.exe --noEmit` | PASS，exit 0 |
| `node_modules/.bin/tsx.exe tests/legal_reasoning_scenarios.test.ts` | PASS，14/14 |
| `node_modules/.bin/tsx.exe tests/legal_reasoning_corrective.test.ts` | PASS |
| `node_modules/.bin/tsx.exe tests/api_auth.test.ts` | PASS |
| `node_modules/.bin/tsx.exe tests/api_route_auth.test.ts` | PASS；實際啟動 `server.ts` 驗證 route |
| `node_modules/.bin/tsx.exe tests/mvp_complete_flow.test.ts` | PASS；PGlite 隔離資料庫完整流程 |
| `npm run build -- --emptyOutDir` | PASS，Vite build exit 0；有既有 config native warning |
| `python tools/judicial3_mvp_audit.py` | PASS；`24 PASS / 0 FAIL / 0 NOT_RUN` |

## 完整流程實際斷言

- 建立案件及 revision 1。
- 保存並讀取 `raw_text`。
- 保存 3 筆 Fact，保留 `ASSERTED`、`DENIED`、`UNKNOWN`。
- 保存 1 筆 `PENDING_SEARCH` Evidence，不提升為 `OBTAINED`。
- 保存候選、構成要件、Fact refs、待查事項及問句 metadata。
- 同案保存 revision 2，讀取目前 revision。
- 其他 owner 讀取同一案件回傳 `null`。

## 仍未執行／限制

- 真實 PostgreSQL、Render、正式登入服務：`NOT_RUN`，未取得授權也未連線。
- TaiLexi：本次讀取逾時；LawBank：本次工具不可存取，研究文件標示 `NOT_VERIFIED`。
