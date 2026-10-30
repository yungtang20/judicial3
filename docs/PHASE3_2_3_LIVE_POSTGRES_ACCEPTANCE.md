# Phase 3.2.3 Live PostgreSQL Acceptance

## 範圍

基準 SHA `9f55ab8c47e4f8287b436986a2a3a7e036a2c219`。Live PASS 必須來自真正 Render Staging PostgreSQL，不能用 PGlite、embedded PostgreSQL 或靜態檢查替代。

## 執行方式

在一次性 Staging acceptance DB 執行 `npx tsx tools/postgres_acceptance.ts`，供應三組 Staging-only URL；驗證 role identity/attributes、migration ledger/checksum/idempotency/rollback/advisory lock、provisioning、RLS A/B、pool context 與例外後隔離。輸出需去識別化。

## 實際結果

Live PostgreSQL：`NOT_RUN`。Service/DB/runner 未建立，沒有 Staging-only credentials。Embedded acceptance 僅列為 repository regression，不能提升本文件狀態。Production DB 完全未連線或修改。下一步是取得已核准 Staging 資源後執行並保存 sanitized evidence。
