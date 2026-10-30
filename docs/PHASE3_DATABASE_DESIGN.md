# Phase 3 資料庫與角色設計

正式 runtime 使用 DATABASE_URL 連線的 NOSUPERUSER、NOBYPASSRLS app role；migration 使用只在 pre-deploy／受控 CLI 使用的 migration role；provisioning 使用 LOGIN 的 `judicial3_provisioner_login`，在每個連線切換至 NOLOGIN 的 `judicial3_provisioner` group。實際 role 建立、owner、GRANT 與密碼不寫入 repository。

0013_system_roles.sql 只建立三個正式 role dictionary row：LEAD_INVESTIGATOR、REVIEWER、ANALYST。使用 role_code 冪等，既有 role 不覆蓋；不建立測試使用者、預設密碼或管理員。user_roles 維持 RLS，僅開放 SELECT policy，撤銷 PUBLIC 寫入。

provisionUser 使用 withTransaction(null)，角色查詢與 users insert 原子提交；users 的 server-side auth boundary 依 0011 設計不允許 HTTP client 直接 provisioning。CLI 只接受 `JUDICIAL3_PROVISIONING_DATABASE_URL`，並透過 `SELECT current_user` 驗證固定的 `judicial3_provisioner` 身分；不再退回 migration 或一般 app 連線。

0014_provisioner_least_privilege.sql 不建立資料庫角色或密碼。部署前必須由受控 bootstrap 建立 `judicial3_app`、NOLOGIN 的 `judicial3_provisioner` 與 LOGIN 的 `judicial3_provisioner_login`，並只建立 login→group membership，再執行 migration 套用欄位級 grant。provisioner 僅能讀取 `user_roles(id, role_code)`、插入 users 必要欄位並讀取新 id；不得更新／刪除 users、讀取案件或 sessions、修改角色、執行 DDL 或 migration。必要角色、屬性或 membership 不符時 migration `RAISE EXCEPTION`，交易 rollback 且不寫入 ledger；PGlite 僅明確跳過真實 role branch。

Migration runtime 使用同一 PoolClient 取得 advisory lock、執行外層 transaction、寫 ledger、commit 或 rollback。lexer-based parser 只移除最外層 BEGIN／COMMIT，不修改已發布 migration checksum。PGlite PASS 不取代真實 PostgreSQL PASS。
