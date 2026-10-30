# Phase 3.2 Render Staging 報告

## 判定：BLOCKED

- **FACT**：`render.yaml` 目前只有 `judicial3-web` 與 `judicial3-db`，且 `autoDeployTrigger: off`；沒有獨立 staging service/database 定義。
- **FACT**：repository 沒有 Render API token、staging URL 或 staging database connection string。
- **BLOCKED**：未執行 Render API、部署、migration、測試帳號建立、production database 操作或 Browser live acceptance。
- **UNKNOWN**：Render dashboard 是否另有未提交至 repository 的 staging 資源；不能從 `render.yaml` 推定存在。

## 完成所需外部資料

1. 獨立 Render staging Web Service 與 staging PostgreSQL。
2. `DATABASE_URL`、`MIGRATION_DATABASE_URL`、`JUDICIAL3_PROVISIONING_DATABASE_URL` 三組 staging-only URL。
3. staging HTTPS URL、Render read-only/deploy 權限與對應 GitHub Actions run。
4. 經確認的 rollback 版本與操作權限。

本報告不使用 production URL 替代，也不把本機或 embedded PostgreSQL 結果升級為 Render PASS。
