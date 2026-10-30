# Phase 3.2 Security Audit

- **PASS（靜態）**：三個連線設定名稱分離，migration 只由 `tools/migrate.ts` 取用 `MIGRATION_DATABASE_URL`。
- **PASS（靜態）**：Provisioning role 名稱為 `judicial3_provisioner`，login role 為 `judicial3_provisioner_login`；migration 0014 收斂 tables grants，撤銷 users update/delete 與 cases/sessions 存取。
- **PASS（靜態）**：Provisioning identity guard 同時核對 `session_user` 與 `current_user`，runtime provisioning Pool query 執行 `SET ROLE` 後 `RESET ROLE`。
- **UNKNOWN**：未連接獨立 PostgreSQL，無法證明實際 role attributes、membership、每一 PoolClient identity、RLS A/B 隔離或 rollback。
- **BLOCKED**：無 Render staging credentials/URL，未執行雲端 migration、登入、session、browser 或 network/console acceptance。

不輸出任何 connection string、password、API key 或 production data。
