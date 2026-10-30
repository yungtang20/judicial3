# Phase 3.3 Restore Runbook

## 安全流程

基準 SHA `9f55ab8c47e4f8287b436986a2a3a7e036a2c219`。只允許還原到名稱結尾為 `_restore`、`_staging`、`_disposable` 或 `_test` 的獨立 DB；Production target 會被拒絕。

1. 驗證 manifest SHA-256 與檔案大小。
2. 用 age 解密到受限暫存目錄。
3. `pg_restore --no-owner --no-privileges` 還原。
4. 驗證 schema、table/index/constraint、migration ledger、資料量、RLS 與 role bootstrap。
5. 連接 Staging Web 驗證 login/session，再記錄 RPO/RTO。
6. 經確認後清理一次性資源。

## 命令與狀態

介面：`python tools/postgres_restore.py --help`；單元測試：`python -m unittest discover -s tools/tests`。實際 restore、資料驗證、RPO/RTO 為 `NOT_RUN`，因沒有核准的 encrypted backup 與 restore DB。禁止對 Production 執行。
