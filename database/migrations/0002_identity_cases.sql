-- Migration: 0002_identity_cases.sql
-- Description: 使用者角色、帳號、連線工作階段、案件主檔及歷史版本快照主表
-- System: 刑事偵查輔助系統 (Criminal Investigation Analysis System v2.0)

BEGIN;

-- 1. 角色定義表
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_code VARCHAR(32) NOT NULL UNIQUE,
    role_name VARCHAR(64) NOT NULL,
    permissions JSONB NOT NULL DEFAULT '[]'::jsonb,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- 2. 使用者帳號表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    badge_number VARCHAR(50) UNIQUE,
    organization VARCHAR(128) NOT NULL DEFAULT '刑事警察專案偵查組',
    role_id UUID NOT NULL REFERENCES user_roles(id) ON DELETE RESTRICT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    security_stamp VARCHAR(64) NOT NULL DEFAULT gen_random_uuid()::text,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- 3. 使用者連線工作階段與安全驗證表
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token_hash VARCHAR(64) NOT NULL UNIQUE,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- 4. 案件基本檔主表 (cases)
CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_number VARCHAR(64) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    lead_investigator_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    current_revision_id UUID,
    classification_level classification_level_enum NOT NULL DEFAULT 'CONFIDENTIAL',
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    archived_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- 5. 案件歷史版本快照表 (case_revisions)
CREATE TABLE IF NOT EXISTS case_revisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    revision_number INTEGER NOT NULL,
    parent_revision_id UUID REFERENCES case_revisions(id) ON DELETE RESTRICT,
    revision_hash VARCHAR(64) NOT NULL,
    change_summary TEXT NOT NULL,
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    locked_at TIMESTAMPTZ,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT chk_rev_number_pos CHECK (revision_number >= 1),
    CONSTRAINT uq_case_revision_number UNIQUE (case_id, revision_number),
    CONSTRAINT uq_case_revision_composite UNIQUE (case_id, id)
);

-- 6. 建立 cases.current_revision_id 指向 case_revisions(id) 的延遲外鍵
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_cases_current_revision' 
          AND table_name = 'cases'
    ) THEN
        ALTER TABLE cases
        ADD CONSTRAINT fk_cases_current_revision
        FOREIGN KEY (current_revision_id) REFERENCES case_revisions(id)
        DEFERRABLE INITIALLY DEFERRED;
    END IF;
END $$;

COMMIT;
