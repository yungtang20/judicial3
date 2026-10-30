# Phase 3 RLS 設計與修復

案件及關聯表維持 FORCE ROW LEVEL SECURITY，使用 transaction-local app.current_user_id 隔離 owner；runtime role 不得為 superuser 或 BYPASSRLS。user_roles 是系統字典，0013 只增加 SELECT policy，不關閉 RLS，也不授予一般寫入。

角色 provisioning 不依賴任意使用者 ID 假冒身分；CLI 必須使用專用 `JUDICIAL3_PROVISIONING_DATABASE_URL`，並以資料庫回傳的 `current_user=judicial3_provisioner` fail closed；不得退回 migration 或 app connection，HTTP 沒有 provisioning endpoint。正式 PostgreSQL 必須在 staging 實測 role grants、RLS、connection pool context 與 provisioning。

目前 PGlite role-based RLS 與 owner health 測試 PASS；真實 PostgreSQL role 權限及跨使用者隔離為 BLOCKED。
