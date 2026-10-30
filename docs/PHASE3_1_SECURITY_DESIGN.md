# Phase 3.1 Security Design

## Provisioning boundary

`tools/provision_user.ts` 只接受 `JUDICIAL3_PROVISIONING_DATABASE_URL`，不退回 `MIGRATION_DATABASE_URL` 或 `DATABASE_URL`。login role `judicial3_provisioner_login` 連線後，每個 PoolClient 都先 `SET ROLE judicial3_provisioner`；同一連線必須驗證 `session_user` 與 `current_user`，否則 fail closed。連線字串與密碼不會輸出。

`0014_provisioner_least_privilege.sql` 不建立角色或密碼。受控部署 bootstrap 必須先建立 app role、NOLOGIN 的 `judicial3_provisioner` group role 與 LOGIN 的 `judicial3_provisioner_login`，只授予 login→group membership，再套用 forward-only grant。provisioner 權限限於角色字典必要欄位、users 建立必要欄位與新 id；案件、sessions、更新、刪除、DDL、角色管理及 migration 均拒絕。必要角色或 membership 不存在時會 `RAISE EXCEPTION` 並 rollback。

## Evidence boundary

PGlite 測試只能證明 SQL／流程行為。embedded PostgreSQL 16.13 acceptance 已實測 role attributes、欄位 grant、LOGIN→SET ROLE、RLS 與拒絕操作；外部 URL 缺少或安全格式不符時才標記 `BLOCKED`。
