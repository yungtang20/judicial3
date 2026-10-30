# JUDICIAL3 Phase 2 驗收基準

- 任務：`JUDICIAL3-ACCEPTANCE-PHASE-2`
- 日期：民國115年10月30日
- Branch：`main`
- HEAD：`6505a2c776187706f6b987b4d2d1afc87170d230`
- Node.js：`v24.17.0`
- npm：`11.13.0`
- Bun：`1.4.2`
- Python：`3.14.6`
- 執行模式：`REVIEWED_PIPELINE`（H1、H2：UI/API/資料庫/部署與認證安全）
- Runtime model identity：`UNVERIFIED`

## 工作目錄保護

驗收開始時已有 Phase 1 未提交修改及未追蹤報告。本階段保留這些內容，未執行 reset、clean、checkout、commit、push 或部署。所有資料庫行為只使用 `%TEMP%` 下隔離 PGlite 目錄；未連線正式資料庫。

## 實際工具與邊界

- UI：Codex 內建瀏覽器，`http://127.0.0.1:3210`，合成手機案。
- 本機資料庫：PGlite 持久化目錄；不是實體 PostgreSQL server。
- PostgreSQL client：`psql` 不存在。
- Container runtime：`docker` 不存在。
- Render：repository 無 `render.yaml`，未提供 Render 唯讀連線，未部署。
- 正式認證：不存在；本機測試使用明確開關且限 loopback 的 dev session。

## 基準差異

Phase 2 開始前的 Phase 1 修改包含 migration 0010、server/API、前端快照還原、法律推理、測試、稽核與 MVP 報告。本階段在其上追加最小修復；因此本報告不把整個 dirty diff 都宣稱為 Phase 2 新增內容。
