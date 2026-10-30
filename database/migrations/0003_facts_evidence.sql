-- Migration: 0003_facts_evidence.sql
-- Description: 結構化事實、事實關聯圖、證物清單、證據來源查驗與行為人行為拆解表
-- System: 刑事偵查輔助系統 (Criminal Investigation Analysis System v2.0)

BEGIN;

-- 6. 結構化事實表 (facts)
CREATE TABLE IF NOT EXISTS facts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    revision_id UUID NOT NULL,
    fact_seq INTEGER NOT NULL,
    description TEXT NOT NULL,
    fact_type VARCHAR(32) NOT NULL DEFAULT 'OBJECTIVE',
    status fact_status_enum NOT NULL,
    confidence_score NUMERIC(4,3) NOT NULL DEFAULT 1.000,
    occurred_at TIMESTAMPTZ,
    is_disputed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT fk_facts_revision 
        FOREIGN KEY (case_id, revision_id) 
        REFERENCES case_revisions(case_id, id) 
        ON DELETE RESTRICT,
    CONSTRAINT chk_facts_confidence_range 
        CHECK (confidence_score >= 0.000 AND confidence_score <= 1.000),
    CONSTRAINT uq_facts_seq_per_revision 
        UNIQUE (revision_id, fact_seq)
);

-- 7. 事實因果推論與關聯圖表 (fact_relations)
CREATE TABLE IF NOT EXISTS fact_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    revision_id UUID NOT NULL,
    source_fact_id UUID NOT NULL REFERENCES facts(id) ON DELETE CASCADE,
    target_fact_id UUID NOT NULL REFERENCES facts(id) ON DELETE CASCADE,
    relation_type VARCHAR(32) NOT NULL,
    rationale TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT fk_fact_relations_revision 
        FOREIGN KEY (case_id, revision_id) 
        REFERENCES case_revisions(case_id, id) 
        ON DELETE RESTRICT,
    CONSTRAINT chk_fact_rel_no_self_loop 
        CHECK (source_fact_id <> target_fact_id),
    CONSTRAINT uq_fact_rel_pair 
        UNIQUE (revision_id, source_fact_id, target_fact_id, relation_type)
);

-- 8. 證據清單與保管鏈表 (evidence_items)
CREATE TABLE IF NOT EXISTS evidence_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    revision_id UUID NOT NULL,
    item_code VARCHAR(64) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(64) NOT NULL,
    custody_chain_summary TEXT,
    hash_md5_sha256 VARCHAR(128),
    storage_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT fk_evidence_items_revision 
        FOREIGN KEY (case_id, revision_id) 
        REFERENCES case_revisions(case_id, id) 
        ON DELETE RESTRICT,
    CONSTRAINT uq_evidence_code_per_revision 
        UNIQUE (revision_id, item_code)
);

-- 9. 證據來源核實紀錄表 (evidence_sources)
CREATE TABLE IF NOT EXISTS evidence_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    revision_id UUID NOT NULL,
    evidence_item_id UUID NOT NULL REFERENCES evidence_items(id) ON DELETE CASCADE,
    provider_name VARCHAR(128) NOT NULL,
    provider_type VARCHAR(64) NOT NULL,
    status source_status_enum NOT NULL DEFAULT 'UNVERIFIED',
    verified_by UUID REFERENCES users(id) ON DELETE SET NULL,
    verified_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT fk_evidence_sources_revision 
        FOREIGN KEY (case_id, revision_id) 
        REFERENCES case_revisions(case_id, id) 
        ON DELETE RESTRICT
);

-- 10. 行為人行為拆解表 (behaviors)
CREATE TABLE IF NOT EXISTS behaviors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    revision_id UUID NOT NULL,
    actor_name VARCHAR(100) NOT NULL,
    action_description TEXT NOT NULL,
    means_method TEXT,
    time_context VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT fk_behaviors_revision 
        FOREIGN KEY (case_id, revision_id) 
        REFERENCES case_revisions(case_id, id) 
        ON DELETE RESTRICT
);

COMMIT;
