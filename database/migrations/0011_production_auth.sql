BEGIN;

-- Authentication tables (users, user_sessions, user_roles) are server-side
-- only. They intentionally do not use row-level security because login has no
-- authenticated identity yet; access must be constrained with database role
-- grants instead (see docs/PHASE3_DATABASE_DESIGN.md). Every case table keeps
-- FORCE ROW LEVEL SECURITY from 0008.

ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions DISABLE ROW LEVEL SECURITY;

ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS csrf_token_hash VARCHAR(64);
ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS security_stamp VARCHAR(64);
ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS revoked_at TIMESTAMPTZ;
ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS last_seen_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp();

CREATE INDEX IF NOT EXISTS idx_user_sessions_active_lookup
  ON user_sessions(session_token_hash, expires_at)
  WHERE is_revoked = FALSE;

COMMIT;


