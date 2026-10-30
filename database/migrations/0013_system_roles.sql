BEGIN;

-- Production role dictionary only. No test users, passwords or default admin
-- accounts are created here.
INSERT INTO user_roles (id, role_code, role_name, permissions, description)
VALUES
  ('11111111-1111-1111-1111-111111111101', 'LEAD_INVESTIGATOR', '主辦偵查官', '["case:create", "case:edit", "fact:edit", "interview:conduct", "document:draft"]'::jsonb, '主辦刑案偵查與事實整理人員'),
  ('11111111-1111-1111-1111-111111111102', 'REVIEWER', '審核長官', '["case:review", "document:approve", "revision:lock"]'::jsonb, '專案督導長官與簽核主管'),
  ('11111111-1111-1111-1111-111111111103', 'ANALYST', '犯罪分析員', '["case:read", "legal:research"]'::jsonb, '法規研究與智慧研析輔助人員')
ON CONFLICT (role_code) DO NOTHING;

-- Roles are a system dictionary, not case data. They are readable without an
-- authenticated case owner so the controlled provisioning CLI can resolve a
-- role before the first user exists. No write policy or write grant is added.
DROP POLICY IF EXISTS p_user_roles_read ON user_roles;
CREATE POLICY p_user_roles_read ON user_roles FOR SELECT TO PUBLIC
  USING (TRUE);
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON user_roles FROM PUBLIC;

-- Render should pre-create these non-login roles. Conditional grants keep a
-- fresh local database migratable while documenting the production boundary.
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'judicial3_app') THEN
    GRANT SELECT ON user_roles TO judicial3_app;
  END IF;
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'judicial3_provisioner') THEN
    GRANT SELECT ON user_roles TO judicial3_provisioner;
  END IF;
END $$;

COMMIT;
