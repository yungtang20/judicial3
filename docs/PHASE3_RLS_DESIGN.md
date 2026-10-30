# Phase 3 RLS 設計

案件與關聯表維持 FORCE ROW LEVEL SECURITY，政策透過 current_app_user_id() 限制 owner。api_idempotency_keys 亦以 user id 隔離；未查證法條只允許明確 [UNVERIFIED_SOURCE]、非 current、1900-01-01 的窄門 insert。

認證表在 migration 0011 保持 server-side 控制；正式環境必須以 NOSUPERUSER NOBYPASSRLS runtime role、欄位授權及 migration owner 分離補足此邊界。

PGlite role-based RLS 測試已 PASS；真實 PostgreSQL app role／connection pool／跨使用者隔離尚未執行，為 BLOCKED。
