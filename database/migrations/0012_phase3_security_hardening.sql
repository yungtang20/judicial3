BEGIN;

-- Phase 3 security hardening. This migration is forward-only; historical
-- migrations are not rewritten.

-- 1. Idempotency records for case-save retries. Server-side only table, but it
--    is still scoped by RLS so a restricted application role cannot read
--    another user's replay records.
CREATE TABLE IF NOT EXISTS api_idempotency_keys (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    idempotency_key VARCHAR(128) NOT NULL,
    request_hash CHAR(64) NOT NULL,
    response JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (user_id, idempotency_key),
    CONSTRAINT chk_idempotency_key_len CHECK (char_length(idempotency_key) BETWEEN 8 AND 128)
);

ALTER TABLE api_idempotency_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_idempotency_keys FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS p_idempotency_owner ON api_idempotency_keys;
CREATE POLICY p_idempotency_owner ON api_idempotency_keys FOR ALL TO PUBLIC
    USING (user_id = current_app_user_id())
    WITH CHECK (user_id = current_app_user_id());

-- 2. Unknown statute references are created as explicitly unverified
--    placeholders. Allow that narrow insert without opening the shared
--    reference table to arbitrary writes.
DROP POLICY IF EXISTS p_statute_insert_unverified ON statute_references;
CREATE POLICY p_statute_insert_unverified ON statute_references FOR INSERT TO PUBLIC
    WITH CHECK (
        current_app_user_id() IS NOT NULL
        AND is_current = FALSE
        AND effective_date = DATE '1900-01-01'
        AND content LIKE '[UNVERIFIED_SOURCE]%'
    );

-- 3. Session lifecycle indexes and format guards.
CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expiry ON user_sessions(expires_at) WHERE is_revoked = FALSE;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'chk_session_token_hash' AND table_name = 'user_sessions'
    ) THEN
        ALTER TABLE user_sessions
            ADD CONSTRAINT chk_session_token_hash CHECK (char_length(session_token_hash) = 64);
    END IF;
END $$;

-- 4. Concurrency index for revision ordering.
CREATE INDEX IF NOT EXISTS idx_case_revisions_parent ON case_revisions(parent_revision_id);

COMMIT;


