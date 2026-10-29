-- ============================================================================
-- 刑事偵查輔助系統 (Criminal Investigation Assistant)
-- 資料庫綱要定義檔 (PostgreSQL Schema DDL) - 規格版本 2.0 (2026-10-27)
-- 包含 20 張實體資料表、CHECK 約束、外鍵關聯、複合索引與 RLS 行級安全政策
-- ============================================================================

-- 啟用必要擴充套件
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- 1. profiles: 使用者設定檔（綁定指定公務帳號）
-- ----------------------------------------------------------------------------
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id TEXT UNIQUE NOT NULL,
    badge_number VARCHAR(64) NOT NULL,
    full_name VARCHAR(64) NOT NULL,
    unit_name VARCHAR(128) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'INVESTIGATOR' CHECK (role IN ('INVESTIGATOR', 'SUPERVISOR', 'SYSTEM_ADMIN')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 2. cases: 案件主檔
-- ----------------------------------------------------------------------------
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_number VARCHAR(64) UNIQUE NOT NULL,
    title VARCHAR(256) NOT NULL,
    owner_id UUID NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
    current_stage VARCHAR(32) NOT NULL DEFAULT 'G0_INTAKE' CHECK (current_stage IN ('G0_INTAKE', 'G1_FACTS', 'G2_LEGAL', 'G3_QUESTIONS', 'G4_ANSWERS', 'G5_DOCUMENTS')),
    flow_status VARCHAR(32) NOT NULL DEFAULT 'DRAFT' CHECK (flow_status IN ('DRAFT', 'IN_REVIEW', 'APPROVED', 'CHANGES_REQUESTED', 'PROCESSING', 'FAILED', 'STALE', 'CANCELLED', 'ARCHIVED')),
    is_archived BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cases_owner_updated ON cases(owner_id, updated_at DESC);

-- ----------------------------------------------------------------------------
-- 3. case_revisions: 原始案情與案件修訂版本（不可變快照）
-- ----------------------------------------------------------------------------
CREATE TABLE case_revisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    revision_number INT NOT NULL,
    raw_intake_text TEXT NOT NULL,
    content_hash_sha256 VARCHAR(64) NOT NULL,
    author_id UUID NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_case_revision UNIQUE (case_id, revision_number)
);

CREATE INDEX idx_case_revisions_lookup ON case_revisions(case_id, revision_number);

-- ----------------------------------------------------------------------------
-- 4. facts: 結構化事實
-- ----------------------------------------------------------------------------
CREATE TABLE facts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    revision_id UUID NOT NULL REFERENCES case_revisions(id) ON DELETE CASCADE,
    subject VARCHAR(128) NOT NULL,
    predicate TEXT NOT NULL,
    object VARCHAR(256) NOT NULL,
    event_time VARCHAR(128) NOT NULL,
    event_location VARCHAR(256) NOT NULL,
    source_type VARCHAR(32) NOT NULL CHECK (source_type IN ('VICTIM', 'SUSPECT', 'WITNESS', 'POLICE_RECORD', 'PHYSICAL_EVIDENCE', 'INFERRED')),
    source_ref VARCHAR(256) NOT NULL,
    source_excerpt TEXT NOT NULL,
    assertion_status VARCHAR(32) NOT NULL CHECK (assertion_status IN ('ASSERTED', 'ADMITTED', 'DENIED', 'INFERRED', 'UNKNOWN')),
    confidence NUMERIC(3, 2) NOT NULL DEFAULT 1.00 CHECK (confidence >= 0.00 AND confidence <= 1.00),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_facts_case_revision ON facts(case_id, revision_id);

-- ----------------------------------------------------------------------------
-- 5. evidence_items: 證據與來源
-- ----------------------------------------------------------------------------
CREATE TABLE evidence_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    evidence_type VARCHAR(64) NOT NULL,
    description TEXT NOT NULL,
    custody_location VARCHAR(256) NOT NULL,
    collection_status VARCHAR(32) NOT NULL CHECK (collection_status IN ('OBTAINED', 'REQUESTED', 'PENDING_SEARCH', 'UNAVAILABLE')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_evidence_items_case ON evidence_items(case_id);

-- ----------------------------------------------------------------------------
-- 6. fact_evidence_links: 事實與證據的多對多關聯
-- ----------------------------------------------------------------------------
CREATE TABLE fact_evidence_links (
    fact_id UUID NOT NULL REFERENCES facts(id) ON DELETE CASCADE,
    evidence_id UUID NOT NULL REFERENCES evidence_items(id) ON DELETE CASCADE,
    link_type VARCHAR(32) NOT NULL DEFAULT 'SUPPORTS' CHECK (link_type IN ('SUPPORTS', 'CONTRADICTS', 'CORROBORATES')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (fact_id, evidence_id)
);

-- ----------------------------------------------------------------------------
-- 7. behaviors: 行為拆解
-- ----------------------------------------------------------------------------
CREATE TABLE behaviors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    revision_id UUID NOT NULL REFERENCES case_revisions(id) ON DELETE CASCADE,
    actor_ref VARCHAR(128) NOT NULL,
    action_description TEXT NOT NULL,
    object_ref VARCHAR(256) NOT NULL,
    time_ref VARCHAR(128) NOT NULL,
    uncertainty_status VARCHAR(32) NOT NULL DEFAULT 'CONFIRMED' CHECK (uncertainty_status IN ('CONFIRMED', 'DISPUTED', 'UNKNOWN')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 8. legal_sources: 法條、判決來源與查證狀態
-- ----------------------------------------------------------------------------
CREATE TABLE legal_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type VARCHAR(32) NOT NULL CHECK (source_type IN ('STATUTE', 'PRECEDENT', 'TREATISE', 'ADMIN_RULE')),
    statute_name VARCHAR(128) NOT NULL,
    article_number VARCHAR(64) NOT NULL,
    paragraph_number VARCHAR(32),
    case_identifier VARCHAR(128),
    official_source_url TEXT,
    content_text TEXT NOT NULL,
    statute_version VARCHAR(64) NOT NULL,
    verification_status VARCHAR(32) NOT NULL DEFAULT 'UNVERIFIED' CHECK (verification_status IN ('VERIFIED', 'UNVERIFIED', 'UNAVAILABLE', 'VERSION_UNCERTAIN')),
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 9. legal_candidates: 候選法律方向
-- ----------------------------------------------------------------------------
CREATE TABLE legal_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    revision_id UUID NOT NULL REFERENCES case_revisions(id) ON DELETE CASCADE,
    legal_name VARCHAR(256) NOT NULL,
    statute_source_id UUID REFERENCES legal_sources(id) ON DELETE SET NULL,
    candidate_status VARCHAR(32) NOT NULL CHECK (candidate_status IN ('PRIMARY', 'ALTERNATIVE', 'LOW_CONFIDENCE', 'UNRESOLVED', 'REJECTED')),
    exclusion_reason TEXT,
    confidence NUMERIC(3, 2) NOT NULL DEFAULT 0.50,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_legal_candidates_case_rev ON legal_candidates(case_id, revision_id);

-- ----------------------------------------------------------------------------
-- 10. legal_elements: 構成要件逐項分析
-- ----------------------------------------------------------------------------
CREATE TABLE legal_elements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES legal_candidates(id) ON DELETE CASCADE,
    element_name VARCHAR(128) NOT NULL,
    element_description TEXT NOT NULL,
    element_status VARCHAR(32) NOT NULL CHECK (element_status IN ('SUPPORTED', 'CONTRADICTED', 'UNRESOLVED', 'NOT_APPLICABLE')),
    reasoning TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 11. candidate_fact_links: 候選罪名與事實關聯表
-- ----------------------------------------------------------------------------
CREATE TABLE candidate_fact_links (
    candidate_id UUID NOT NULL REFERENCES legal_candidates(id) ON DELETE CASCADE,
    fact_id UUID NOT NULL REFERENCES facts(id) ON DELETE CASCADE,
    relation_type VARCHAR(32) NOT NULL CHECK (relation_type IN ('SUPPORTING', 'CONTRARY', 'UNKNOWN_PENDING')),
    PRIMARY KEY (candidate_id, fact_id, relation_type)
);

-- ----------------------------------------------------------------------------
-- 12. core_issues: 核心爭點
-- ----------------------------------------------------------------------------
CREATE TABLE core_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES legal_candidates(id) ON DELETE CASCADE,
    issue_description TEXT NOT NULL,
    priority VARCHAR(16) NOT NULL DEFAULT 'HIGH' CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 13. interview_questions: 筆錄問句
-- ----------------------------------------------------------------------------
CREATE TABLE interview_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    candidate_id UUID REFERENCES legal_candidates(id) ON DELETE SET NULL,
    element_id UUID REFERENCES legal_elements(id) ON DELETE SET NULL,
    question_type VARCHAR(64) NOT NULL CHECK (question_type IN (
        '1_CORE_ELEMENT', '2_ACT_PROCESS', '3_SUBJECTIVE_INTENT', 
        '4_TIME_LOCATION_PERSON', '5_FLOW_OF_PROPERTY', '6_EVIDENCE_SOURCE', 
        '7_CONTRARY_ALTERNATIVE', '8_CONTRADICTION_SUPPLEMENT', '9_UNRESOLVED_INQUIRY'
    )),
    question_text TEXT NOT NULL,
    rationale TEXT NOT NULL,
    priority VARCHAR(32) NOT NULL DEFAULT 'P1_IMPORTANT' CHECK (priority IN ('P0_CRITICAL', 'P1_IMPORTANT', 'P2_SUPPLEMENTAL')),
    review_status VARCHAR(32) NOT NULL DEFAULT 'DRAFT' CHECK (review_status IN ('DRAFT', 'IN_REVIEW', 'APPROVED', 'REVISED', 'STALE', 'REJECTED')),
    revision_number INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_interview_questions_lookup ON interview_questions(case_id, candidate_id);

-- ----------------------------------------------------------------------------
-- 14. interview_answers: 問句回答紀錄
-- ----------------------------------------------------------------------------
CREATE TABLE interview_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES interview_questions(id) ON DELETE CASCADE,
    answer_text TEXT NOT NULL,
    respondent_role VARCHAR(32) NOT NULL CHECK (respondent_role IN ('VICTIM', 'SUSPECT', 'WITNESS')),
    answer_revision INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_interview_answers_lookup ON interview_answers(question_id, answer_revision);

-- ----------------------------------------------------------------------------
-- 15. analysis_runs: 分析執行紀錄
-- ----------------------------------------------------------------------------
CREATE TABLE analysis_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    input_revision_id UUID NOT NULL REFERENCES case_revisions(id) ON DELETE RESTRICT,
    task_type VARCHAR(64) NOT NULL,
    engine_type VARCHAR(32) NOT NULL CHECK (engine_type IN ('LOCAL_RULES', 'GEMINI_EXTERNAL')),
    engine_model VARCHAR(64),
    status VARCHAR(32) NOT NULL CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED')),
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_analysis_runs_case_time ON analysis_runs(case_id, started_at DESC);

-- ----------------------------------------------------------------------------
-- 16. review_records: 人工審核紀錄
-- ----------------------------------------------------------------------------
CREATE TABLE review_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    gate_name VARCHAR(32) NOT NULL CHECK (gate_name IN ('G0_INTAKE', 'G1_FACTS', 'G2_LEGAL', 'G3_QUESTIONS', 'G4_ANSWERS', 'G5_DOCUMENTS')),
    target_revision_id UUID NOT NULL REFERENCES case_revisions(id) ON DELETE RESTRICT,
    decision VARCHAR(32) NOT NULL CHECK (decision IN ('APPROVE', 'REQUEST_CHANGES', 'REJECT')),
    reviewer_id UUID NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
    reason TEXT,
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    dependency_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_review_records_case_gate ON review_records(case_id, gate_name, reviewed_at DESC);

-- ----------------------------------------------------------------------------
-- 17. document_outputs: 條陳與文件輸出版本
-- ----------------------------------------------------------------------------
CREATE TABLE document_outputs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    template_version VARCHAR(64) NOT NULL,
    source_revision_id UUID NOT NULL REFERENCES case_revisions(id) ON DELETE RESTRICT,
    document_type VARCHAR(64) NOT NULL DEFAULT 'POLICE_STATEMENT',
    title_reason VARCHAR(256) NOT NULL,
    summary_findings TEXT NOT NULL,
    seized_items JSONB NOT NULL DEFAULT '[]'::jsonb,
    legal_provisions JSONB NOT NULL DEFAULT '[]'::jsonb,
    recommendations TEXT NOT NULL,
    validation_status VARCHAR(32) NOT NULL DEFAULT 'NOT_RUN' CHECK (validation_status IN ('PASS', 'FAIL', 'NOT_RUN')),
    validation_errors JSONB NOT NULL DEFAULT '[]'::jsonb,
    is_approved BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_document_outputs_case_time ON document_outputs(case_id, created_at DESC);

-- ----------------------------------------------------------------------------
-- 18. audit_events: 操作稽核日誌
-- ----------------------------------------------------------------------------
CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id) ON DELETE SET NULL,
    actor_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    action_type VARCHAR(64) NOT NULL,
    target_entity VARCHAR(64) NOT NULL,
    target_id VARCHAR(64),
    ip_address INET,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_events_case_time ON audit_events(case_id, occurred_at DESC);

-- ----------------------------------------------------------------------------
-- 19. prompt_versions: 提示詞版本管理
-- ----------------------------------------------------------------------------
CREATE TABLE prompt_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type VARCHAR(64) NOT NULL,
    version VARCHAR(32) NOT NULL,
    system_instruction TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_prompt_task_version UNIQUE (task_type, version)
);

-- ----------------------------------------------------------------------------
-- 20. schema_migrations: 資料庫遷移履歷
-- ----------------------------------------------------------------------------
CREATE TABLE schema_migrations (
    version VARCHAR(64) PRIMARY KEY,
    description TEXT NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 行級安全控制 (Row-Level Security Policies)
-- ----------------------------------------------------------------------------
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE facts ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_outputs ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;

-- 政策示例：僅案件擁有者可存取案件及其關聯資料
CREATE POLICY cases_owner_policy ON cases
    FOR ALL
    USING (owner_id = (SELECT id FROM profiles WHERE auth_user_id = current_setting('request.jwt.claim.sub', true)::text));
