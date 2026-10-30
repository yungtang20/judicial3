# Phase 3.2.2 Environment Configuration

## 目標

基準 SHA `9f55ab8c47e4f8287b436986a2a3a7e036a2c219`。每個執行面只取得必要 Secret；Blueprint 不含 Secret value。

## 變數矩陣

| 執行面 | 允許 | 禁止 |
|---|---|---|
| Web | application `DATABASE_URL`, `JUDICIAL3_PUBLIC_ORIGIN` | migration/provisioning URL 或 mode |
| Migrator | migration `DATABASE_URL`, `JUDICIAL3_EXPECTED_DATABASE_ROLE` | provisioning URL、Web session secret |
| Admin CLI | staging provisioning URL、stdin password | production URL、命令列 password |

Web 固定 `NODE_ENV=production`、PostgreSQL engine、dev session=false、test seed=false、external AI=false。GitHub `staging` environment 儲存 Render API key 與測試帳密，變數只存 resource ID/URL。執行 `python tools/secret_scan.py` 檢查 tracked files。

## 限制

Live key 刪除／查詢為 `BLOCKED`；Blueprint 省略 key 不視為已刪除。必須以 Render Dashboard/API 對指定 key 刪除後重新查詢。不得在文件或對話貼值。
