BEGIN;

-- Roles and passwords are created by a controlled deployment bootstrap, never
-- by a migration. The login role is separate from the NOLOGIN group.
DO $$
DECLARE
  role_record RECORD;
  membership_count INTEGER;
BEGIN
  -- PGlite has no real role boundary. Real PostgreSQL acceptance must execute
  -- the role checks and grants below.
  IF version() LIKE '%PGlite%' THEN
    RAISE NOTICE '0014 role grants require real PostgreSQL; skipped in PGlite';
    RETURN;
  END IF;
  IF to_regrole('judicial3_provisioner') IS NULL
     OR to_regrole('judicial3_provisioner_login') IS NULL THEN
    RAISE EXCEPTION 'required provisioning roles are missing; pre-create judicial3_provisioner and judicial3_provisioner_login before migration';
  END IF;

  FOR role_record IN
    SELECT expected_name
    FROM (VALUES
      ('judicial3_app'),
      ('judicial3_provisioner'),
      ('judicial3_provisioner_login')
    ) AS required(expected_name)
    WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = required.expected_name)
  LOOP
    RAISE EXCEPTION 'required PostgreSQL role % is missing; run the reviewed role bootstrap before migration 0014', role_record.expected_name;
  END LOOP;

  IF EXISTS (
    SELECT 1 FROM pg_roles
    WHERE rolname = 'judicial3_provisioner'
      AND (rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls OR rolinherit)
  ) THEN
    RAISE EXCEPTION 'judicial3_provisioner must be NOLOGIN, NOSUPERUSER, NOCREATEDB, NOCREATEROLE, NOREPLICATION, NOBYPASSRLS, NOINHERIT';
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_roles
    WHERE rolname = 'judicial3_provisioner_login'
      AND (NOT rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls OR rolinherit)
  ) THEN
    RAISE EXCEPTION 'judicial3_provisioner_login must be LOGIN, NOSUPERUSER, NOCREATEDB, NOCREATEROLE, NOREPLICATION, NOBYPASSRLS, NOINHERIT';
  END IF;

  IF EXISTS (
    SELECT 1 FROM pg_roles
    WHERE rolname = 'judicial3_app'
      AND (NOT rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls)
  ) THEN
    RAISE EXCEPTION 'judicial3_app must be LOGIN, NOSUPERUSER, NOCREATEDB, NOCREATEROLE, NOREPLICATION, NOBYPASSRLS';
  END IF;

  SELECT COUNT(*) INTO membership_count
  FROM pg_auth_members membership
  JOIN pg_roles member ON member.oid = membership.member
  WHERE member.rolname = 'judicial3_provisioner_login';
  IF membership_count <> 1 OR NOT EXISTS (
    SELECT 1
    FROM pg_auth_members membership
    JOIN pg_roles member ON member.oid = membership.member
    JOIN pg_roles granted ON granted.oid = membership.roleid
    WHERE member.rolname = 'judicial3_provisioner_login'
      AND granted.rolname = 'judicial3_provisioner'
  ) THEN
    RAISE EXCEPTION 'judicial3_provisioner_login must have exactly one membership: judicial3_provisioner';
  END IF;

  EXECUTE 'GRANT USAGE ON SCHEMA public TO judicial3_provisioner';
  EXECUTE 'REVOKE CREATE ON SCHEMA public FROM judicial3_provisioner';
  EXECUTE 'REVOKE ALL ON ALL TABLES IN SCHEMA public FROM judicial3_provisioner';
  EXECUTE 'REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM judicial3_provisioner';
  EXECUTE 'GRANT SELECT (id, role_code) ON user_roles TO judicial3_provisioner';
  EXECUTE 'GRANT INSERT (username, email, password_hash, full_name, role_id) ON users TO judicial3_provisioner';
  EXECUTE 'GRANT SELECT (id) ON users TO judicial3_provisioner';
END $$;

COMMIT;
