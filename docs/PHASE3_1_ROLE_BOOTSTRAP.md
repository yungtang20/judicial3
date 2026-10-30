# Phase 3.1 Role Bootstrap

Migration 0014 不建立角色、登入密碼或 membership。部署前由受控 PostgreSQL bootstrap 依下列順序執行，密碼只由 secret manager 或互動式 `\\password` 設定，不寫入 repository：

1. 建立 `judicial3_app`：`LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS`。
2. 建立 `judicial3_provisioner`：`NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT`。
3. 建立 `judicial3_provisioner_login`：`LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT`。
4. 只執行 `GRANT judicial3_provisioner TO judicial3_provisioner_login`，不得授予其他非必要 membership。
5. 以 migration role 執行全部 migrations；0014 會在角色不存在、屬性不符或 membership 不符時 `RAISE EXCEPTION`，因此不會留下 ledger row。
6. Provisioning CLI 使用 login role 的連線，runtime 在每個 PoolClient 上執行 `SET ROLE judicial3_provisioner`；CLI 同一連線驗證 `session_user` 與 `current_user` 後才建立帳號。

已由 embedded PostgreSQL 16.13 實際驗證：`session_user=judicial3_provisioner_login`、切換後 `current_user=judicial3_provisioner`，且 provisioner 無法執行 DDL、讀取 migration ledger、讀取案件或 sessions。
