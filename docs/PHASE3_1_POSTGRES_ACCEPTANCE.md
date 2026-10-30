# Phase 3.1 PostgreSQL Acceptance

執行：

```powershell
$env:JUDICIAL3_TEST_DATABASE_URL = 'postgresql://migration_role@host:5432/judicial3_test'
$env:JUDICIAL3_TEST_PROVISIONING_DATABASE_URL = 'postgresql://judicial3_provisioner@host:5432/judicial3_test'
$env:JUDICIAL3_TEST_APP_DATABASE_URL = 'postgresql://judicial3_app@host:5432/judicial3_test'
python tools/judicial3_postgres_acceptance.py
```

三個 URL 必須指向隔離的 test/staging/sandbox/disposable database，且不得等於正式 `DATABASE_URL`。測試檢查 migration ledger、角色 `NOSUPERUSER/NOBYPASSRLS`、provisioner 建立帳號、provisioner 更新／刪除／案件／session 拒絕，以及 app role provisioning 拒絕。URL 不會輸出。

目前本機沒有提供這三組隔離 PostgreSQL 連線，因此本輪為 `BLOCKED`，不以 PGlite 取代正式驗收。
