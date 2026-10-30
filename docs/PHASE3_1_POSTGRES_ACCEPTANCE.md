# Phase 3.1 PostgreSQL Acceptance

執行：

```powershell
$env:JUDICIAL3_TEST_DATABASE_URL = 'postgresql://migration_role@host:5432/judicial3_test'
$env:JUDICIAL3_TEST_PROVISIONING_DATABASE_URL = 'postgresql://judicial3_provisioner@host:5432/judicial3_test'
$env:JUDICIAL3_TEST_APP_DATABASE_URL = 'postgresql://judicial3_app@host:5432/judicial3_test'
python tools/judicial3_postgres_acceptance.py
```

三個 URL 必須指向同一個、名稱以 `_test`、`_disposable` 或 `_staging` 結尾的隔離 database，且不得等於正式 `DATABASE_URL` 或 `MIGRATION_DATABASE_URL`。測試檢查 migration ledger、角色屬性、LOGIN→SET ROLE、provisioner 建立帳號、provisioner 更新／刪除／案件／session／DDL／migration ledger 拒絕、app role provisioning 拒絕、失敗交易 rollback、RLS A/B 與 pool context。URL 不會輸出。

本機透過 `embedded-postgres` 啟動 PostgreSQL 16.13（`--locale=C`）完成上述實際 SQL 驗收；測試資料庫與資料夾在 finally 清理。這是 disposable PostgreSQL 證據，不等同 Render staging 或正式資料庫驗證。
