BEGIN;

-- The database roles are deliberately created outside migrations by the
-- deployment owner. This migration only applies grants after the roles exist;
-- it never creates login roles or stores credentials.
DO $$
BEGIN
  -- PGlite is a local test engine without PostgreSQL roles. It must not be
  -- mistaken for production PostgreSQL role evidence.
  IF version() LIKE '%PGlite%' THEN
    RETURN;
  END IF;
  IF to_regrole('judicial3_provisioner') IS NULL
     OR to_regrole('judicial3_provisioner_login') IS NULL THEN
    RAISE EXCEPTION 'required provisioning roles are missing; pre-create judicial3_provisioner and judicial3_provisioner_login before migration';
  END IF;

  EXECUTE 'GRANT USAGE ON SCHEMA public TO judicial3_provisioner';
  EXECUTE 'REVOKE CREATE ON SCHEMA public FROM judicial3_provisioner';
  EXECUTE 'REVOKE ALL ON user_roles FROM judicial3_provisioner';
  EXECUTE 'GRANT SELECT (id, role_code) ON user_roles TO judicial3_provisioner';
  EXECUTE 'REVOKE ALL ON users FROM judicial3_provisioner';
  EXECUTE 'GRANT INSERT (username, email, password_hash, full_name, role_id) ON users TO judicial3_provisioner';
  EXECUTE 'GRANT SELECT (id) ON users TO judicial3_provisioner';

  EXECUTE 'REVOKE UPDATE, DELETE, TRUNCATE ON users FROM judicial3_provisioner';
  EXECUTE 'REVOKE ALL ON user_sessions FROM judicial3_provisioner';
  EXECUTE 'REVOKE ALL ON cases FROM judicial3_provisioner';
  EXECUTE 'REVOKE ALL ON case_revisions FROM judicial3_provisioner';
  EXECUTE 'REVOKE ALL ON api_idempotency_keys FROM judicial3_provisioner';
  EXECUTE 'REVOKE ALL ON ALL TABLES IN SCHEMA public FROM judicial3_provisioner';

  -- The broad revoke above is intentional. Re-apply only the two required
  -- table grants after removing inherited/default table privileges.
  EXECUTE 'GRANT SELECT (id, role_code) ON user_roles TO judicial3_provisioner';
  EXECUTE 'GRANT INSERT (username, email, password_hash, full_name, role_id) ON users TO judicial3_provisioner';
  EXECUTE 'GRANT SELECT (id) ON users TO judicial3_provisioner';
END $$;

COMMIT;
