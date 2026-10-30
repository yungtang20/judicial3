# Phase 3.3 Rollback Runbook

## 原則

基準 SHA `9f55ab8c47e4f8287b436986a2a3a7e036a2c219`。Render deploy rollback 只回復應用 artifact，不會回復 PostgreSQL。Migration 先分類 ADDITIVE、BACKWARD_COMPATIBLE、DESTRUCTIVE、IRREVERSIBLE、DATA_TRANSFORM、REQUIRES_MAINTENANCE；已套用 migration 不重寫。

## 演練步驟

在 Staging 記錄 stable deploy ID/SHA 與 health/browser，部署新 SHA，注入可控應用故障，使用 Render rollback API 回到指定 deploy，再驗證 health、login/session、DB、RLS 與 schema compatibility。可逆 migration 使用審查過的 rollback SQL；不可逆採 forward fix、restore 或 expand-and-contract。

## 狀態

Workflow 已要求 exact merged SHA 與 migration-success-before-deploy。Live rollback：`NOT_RUN`，沒有 Staging deploy。Production workflow 只記錄人工 environment approval，不執行 migration/deploy；本次禁止觸發 Production。
