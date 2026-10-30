# Phase 3.1 Security Design

## Provisioning boundary

`tools/provision_user.ts` 只接受 `JUDICIAL3_PROVISIONING_DATABASE_URL`，不退回 `MIGRATION_DATABASE_URL` 或 `DATABASE_URL`。連線建立後查詢 `current_user`，必須精確等於 `judicial3_provisioner`，否則 fail closed。連線字串與密碼不會輸出。

`0014_provisioner_least_privilege.sql` 不建立角色或密碼。受控部署 bootstrap 必須先建立 `judicial3_app`、`judicial3_provisioner`，設定 `NOLOGIN`、`NOSUPERUSER`、`NOBYPASSRLS`，再套用 forward-only grant。provisioner 權限限於角色字典必要欄位、users 建立必要欄位與新 id；案件、sessions、更新、刪除、DDL、角色管理及 migration 均拒絕。

## Evidence boundary

PGlite 測試只能證明 SQL／流程行為。正式 role attributes、欄位 grant、RLS 與拒絕操作必須由 `tools/judicial3_postgres_acceptance.py` 連接隔離 PostgreSQL 實測；缺少三組隔離 URL 時狀態為 `BLOCKED`。
