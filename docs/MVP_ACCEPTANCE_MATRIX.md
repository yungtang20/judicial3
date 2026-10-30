# JUDICIAL3 MVP 獨立驗收矩陣

驗收基準：`6505a2c776187706f6b987b4d2d1afc87170d230`
修正後驗收日期：民國115年10月30日

| 項目 | 實際驗證 | 結果 | 證據 |
|---|---|---|---|
| T01 建案 | PGlite 隔離庫建立案件及 revision 1 | PASS | `tests/mvp_complete_flow.test.ts` |
| T02 Fact 狀態與保存 | 實際保存／讀取 ASSERTED、ADMITTED、DENIED、UNKNOWN | PASS | `MVP_FLOW_PASS`、`tests/mvp_complete_flow.test.ts` |
| T03 Evidence／要件追溯 | 驗證 PENDING_SEARCH 不升級、element fact/evidence refs 保存 | PASS | `MVP_FLOW_PASS`、migration 0010 |
| T04 候選方向 | 14 情境及 corrective test 通過；未知不轉 FALSE | PASS（有限罪章範圍） | `legal_reasoning_scenarios.test.ts`、`legal_reasoning_corrective.test.ts` |
| T05 問句 | 後端問句 metadata、回答、UI 新增／編輯／刪除程式路徑已接入 | PARTIAL_PASS | 型別檢查、flow；瀏覽器互動未執行 |
| T06 修改／重新分析 | revision 1→2、目前版本更新、歷史版本回傳 | PASS（API／服務層） | `MVP_FLOW_PASS`、`revisionHistory` |
| T07 重新開啟 | API 重新讀取 raw text、Fact、Evidence、Candidate、Element、Question、答案 | PASS（服務層） | `MVP_FLOW_PASS` |
| T08 輸出 | 前端下載程式路徑存在；實際瀏覽器下載及檔案內容未執行 | NOT_RUN | 缺少可用瀏覽器自動化套件 |
| T09 錯誤處理 | 保存必要欄位驗證、PGlite fail-closed、API 未登入拒絕 | PARTIAL_PASS | audit 28 PASS；LLM／外部檢索失敗未端到端注入 |
| 認證／案件隔離 | production dev-session 404、未登入 chat 401、有效 token 200、兩 owner 隔離 | PASS（本機 API） | `API_ROUTE_AUTH_PASS`、`MVP_FLOW_PASS` |
| 資料庫遷移 | 一次性 PGlite migration、重複 migration、交易保存 | PASS（PGlite） | `MVP_FLOW_PASS` |
| PostgreSQL／正式登入 | 未連線正式服務 | NOT_RUN | 環境／授權限制 |
| UI 視覺／鍵盤／axe | 未執行 | NOT_RUN | 無瀏覽器執行環境 |

## 回歸命令

- `node_modules\\.bin\\tsc.exe --noEmit` → exit 0
- `node_modules\\.bin\\tsx.exe tests\\legal_reasoning_scenarios.test.ts` → 14/14 PASS
- `node_modules\\.bin\\tsx.exe tests\\legal_reasoning_corrective.test.ts` → exit 0
- `node_modules\\.bin\\tsx.exe tests\\api_auth.test.ts` → exit 0
- `node_modules\\.bin\\tsx.exe tests\\api_route_auth.test.ts` → exit 0
- `node_modules\\.bin\\tsx.exe tests\\mvp_complete_flow.test.ts` → exit 0
- `python tools\\judicial3_mvp_audit.py` → `28 PASS / 0 FAIL / 0 NOT_RUN`
- `npm run build -- --emptyOutDir` → exit 0（既有 Vite config warning）
