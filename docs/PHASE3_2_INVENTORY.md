# JUDICIAL3 Phase 3.2 唯讀盤點

> 盤點基線：`7ce004398533b6da243c423dd1b63f393c000c12`（目前 `origin/main`）。
> 任務文件指定的 `8df382...` 未出現在目前遠端 HEAD，兩者差異保留為可追溯風險。

## 服務架構

- **FACT / PASS**：`render.yaml` 定義一個 Node Web Service `judicial3-web`，以 `npm start` 啟動 Express/Vite 應用程式。
- **FACT / PASS**：資料層可選 PGlite 或 PostgreSQL；production 設定要求 PostgreSQL。Migration ledger 與 SQL migrations 位於 `database/migrations/`。
- **FACT / PASS**：主要健康檢查路徑為 `/api/health/ready`。
- **FACT / UNKNOWN**：目前 repository 沒有 `.github/workflows/`，尚無可由 GitHub Actions 執行紀錄證明的 CI。

## 環境變數與用途

| 變數 | 用途 | 目前證據 |
|---|---|---|
| `DATABASE_URL` | Web runtime 的 Application connection | `render.yaml` / `src/server/databaseRuntime.ts` |
| `MIGRATION_DATABASE_URL` | `tools/migrate.ts` 覆寫 `DATABASE_URL`，供 migration 流程使用 | `render.yaml` / `tools/migrate.ts` |
| `JUDICIAL3_PROVISIONING_DATABASE_URL` | Provisioning CLI 專用 connection | `render.yaml` / `tools/provision_user.ts` |
| `JUDICIAL3_DATABASE_ENGINE` | production 固定選擇 PostgreSQL | `src/server/databaseRuntime.ts` |
| `JUDICIAL3_PUBLIC_ORIGIN` | production origin/CSRF 設定 | `render.yaml` / `src/server/config.ts` |
| `JUDICIAL3_ALLOW_DEV_SESSION`、`JUDICIAL3_LOAD_TEST_SEED` | 明確關閉 production 開發 session 與測試 seed | `render.yaml` |
| `JUDICIAL3_PROVISIONING_MODE` | 目前由 CLI 設定，跳過 runtime migration ledger check | `tools/provision_user.ts` |

## 三種資料庫身分

- **Application**：應由 `DATABASE_URL` 使用 `judicial3_app`；目前設定只驗證 URL 存在，尚無 Render staging 實際 session identity 證據。
- **Migration**：由 `MIGRATION_DATABASE_URL` 僅透過 `tools/migrate.ts` 使用；目前為設定與程式碼層級隔離，尚無外部 PostgreSQL 執行證據。
- **Provisioning**：由 `JUDICIAL3_PROVISIONING_DATABASE_URL` 使用 `judicial3_provisioner_login`，再以 `judicial3_provisioner` 執行最小權限操作；目前 `provisioning.ts` 僅檢查 `current_user`，PoolClient 的 `SET ROLE` 尚未在此基線被證明。

## Migration 與 Provisioning 流程

- **FACT / PASS**：Render `preDeployCommand` 執行 `npm run db:migrate`；`tools/migrate.ts` 優先使用 `MIGRATION_DATABASE_URL`。
- **FACT / PASS**：runtime 以 migration ledger、checksum 與 advisory lock 驗證 migration；SQL migration 0014 負責 provisioning grant。
- **FACT / PARTIAL**：`tools/provision_user.ts` 僅接受 provisioning URL，密碼由 stdin 傳入，不接受 command argument；實際 role identity 仍需獨立 PostgreSQL 驗證。

## 部署與健康檢查

- **FACT / PASS**：Build 為 `npm ci --legacy-peer-deps && npm run build`；Start 為 `npm start`；部署前 migration 為 `npm run db:migrate`。
- **FACT / BLOCKED**：`render.yaml` 只有一個 `judicial3-web` 與一個 `judicial3-db`，沒有獨立命名的 staging Web Service/PostgreSQL/HTTPS URL 可供本階段驗收。
- **FACT / BLOCKED**：未取得 Render API credentials 或 staging URL，因此未執行 Render API、部署、migration、browser live validation，也未接觸 production 資料庫。

## 未解決風險與外部需求

1. **BLOCKED**：需要獨立 Render staging Web Service、獨立 staging PostgreSQL、三組非 production connection 與 staging HTTPS URL。
2. **BLOCKED**：需要 Render read-only/deploy 權限與 GitHub Actions 實際 run URL，才能完成雲端部署、rollback、browser、live PostgreSQL 驗收。
3. **UNKNOWN**：目前 Render dashboard 的實際資源與 env values 不在 repository，不能由 `render.yaml` 推定已存在。
4. **PASS（本機範圍）**：可在 CI 使用 embedded PostgreSQL 進行可重現測試，但該證據不得升級為 Render live PASS。
