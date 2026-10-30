# Phase 3.2.2 Render Staging Setup

## 盤點

盤點基準 SHA `9f55ab8c47e4f8287b436986a2a3a7e036a2c219`。目前可見 Render Workspace 為 `twse`（ID `tea-d5aacqbuibrs73bo0vo0`）；未找到 judicial3 service 或 PostgreSQL。Workspace 方案、可用免費額度、通知與付款狀態為 `UNKNOWN`。

## 設計

`render.staging.yaml` 定義獨立 `judicial3-staging-web` 與 `judicial3-staging-db`；資料庫與 Production 不共用，auto deploy 關閉，不載入 production data。`render.migration-runner.yaml` 與 `render.acceptance-runner.yaml` 分別定義 migration 與一次性驗收 runner，避免讓 GitHub runner 直接開放連入 private DB。建議部署順序：DB → role bootstrap → migrator → migration ledger → Web → private acceptance → health → browser。

## 狀態與下一步

沒有建立或修改任何 Render 資源，Service ID、DB ID、HTTPS URL、版本與部署時間均為 `BLOCKED`。原因是 Workspace plan 無法確認，兩個 `0.5c-512mb` private runner 依 2026-10-30 官方價格各約 USD 7/月（合計約 USD 14/月），最小付費 PostgreSQL 約 USD 6/月另加儲存，最低持續成本約 USD 20/月起；免費 PostgreSQL 又不具可靠備份／復原能力。取得費用核准與安全傳遞的 Render token 後再套用 Staging；Production 禁止變更。
