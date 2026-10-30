# Phase 3 資料庫與角色設計

正式 runtime 使用 DATABASE_URL 連線的 NOSUPERUSER、NOBYPASSRLS app role；migration 使用只在 pre-deploy／受控 CLI 使用的 migration role；provisioning 應使用預先建立的 judicial3_provisioner role。實際 role 建立、owner、GRANT 與密碼不寫入 repository。

0013_system_roles.sql 只建立三個正式 role dictionary row：LEAD_INVESTIGATOR、REVIEWER、ANALYST。使用 role_code 冪等，既有 role 不覆蓋；不建立測試使用者、預設密碼或管理員。user_roles 維持 RLS，僅開放 SELECT policy，撤銷 PUBLIC 寫入。

provisionUser 使用 withTransaction(null)，角色查詢與 users insert 原子提交；users 的 server-side auth boundary 依 0011 設計不允許 HTTP client 直接 provisioning。正式 staging 必須以受控 provisioner role 驗證此路徑。

Migration runtime 使用同一 PoolClient 取得 advisory lock、執行外層 transaction、寫 ledger、commit 或 rollback。lexer-based parser 只移除最外層 BEGIN／COMMIT，不修改已發布 migration checksum。PGlite PASS 不取代真實 PostgreSQL PASS。
