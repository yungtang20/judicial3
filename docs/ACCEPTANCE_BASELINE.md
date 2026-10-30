# JUDICIAL3 MVP 驗收基準

驗收任務：`JUDICIAL3-MVP-ACCEPTANCE-001`
驗收基準提交：`6505a2c776187706f6b987b4d2d1afc87170d230`
驗收日期：民國115年10月30日

## 環境

- 專案：`D:\工作用\judicial3`
- 分支：`main`
- Node.js：以專案現有 `tsx`、`tsc` 及 `npm` 執行
- 資料庫：PGlite；流程測試透過 `JUDICIAL3_DATABASE_PATH` 使用一次性暫存目錄
- 正式資料庫、正式登入服務、Render 及 PostgreSQL：本次不連線
- 虛構種子資料：`database/tests/test_data.sql`

## 基準狀態

驗收開始前已確認工作區無未提交變更，HEAD 為上述基準提交。既有程式包含本機 dev-session bridge、PGlite 持久化案件儲存、案件 owner 條件查詢及候選／要件／問句追溯欄位。

## 已執行基準命令

以下命令均在驗收前獨立執行，未使用正式案件資料：

- `node_modules\\.bin\\tsc.exe --noEmit`
- `node_modules\\.bin\\tsx.exe tests\\legal_reasoning_scenarios.test.ts`
- `node_modules\\.bin\\tsx.exe tests\\legal_reasoning_corrective.test.ts`
- `node_modules\\.bin\\tsx.exe tests\\api_auth.test.ts`
- `node_modules\\.bin\\tsx.exe tests\\api_route_auth.test.ts`
- `node_modules\\.bin\\tsx.exe tests\\mvp_complete_flow.test.ts`
- `python tools\\judicial3_mvp_audit.py`
- `npm run build -- --emptyOutDir`

## 限制

- 目前沒有正式登入／登出／token revoke 服務，dev-session 只能作本機 MVP 入口，不能作正式身分驗證證據。
- 尚未發現可用的瀏覽器自動化套件，因此瀏覽器 UI 互動驗收在基準階段標示 `NOT_RUN`；React 程式碼與 API 仍另行檢查。
- 真實 PostgreSQL、RLS 實際連線、外部法律檢索及部署環境不在本次本機驗收範圍。
