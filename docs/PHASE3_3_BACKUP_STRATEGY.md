# Phase 3.3 Backup Strategy

## 目標與策略

基準 SHA `9f55ab8c47e4f8287b436986a2a3a7e036a2c219`。A：依實際付費方案使用 Render native backup/PITR；B：以 `pg_dump --format=custom` 建立一致性 logical backup，`pg_restore --list` 驗證後以 age 加密並產生 SHA-256 manifest；C：異地 object storage 採最小權限、版本控制與 retention lock。

## 保留與排程

建議 Daily 14、Weekly 8、Monthly 12 份，最終須由法規、資料量與費用核准。UTC 排程需在通知中同時標 Asia/Taipei。失敗不得刪除上一份有效備份，檔名含 UTC timestamp 且禁止覆寫。

## 實作與限制

`python tools/postgres_backup.py --help` 可檢查本機介面；URL 轉為 `PG*` 環境而不出現在 command line。遠端上傳刻意 fail closed。實際 backup、native PITR、object storage 與費用為 `NOT_RUN/BLOCKED`，因沒有 Staging DB 與儲存授權。免費 Render PostgreSQL 不可作為可復原 Production 策略。
