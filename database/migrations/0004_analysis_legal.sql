-- Migration: 0004_analysis_legal.sql
-- Description: 法規基準、實務判決見解、候選法律方向、構成要件拆解、事實映射及核心爭點
-- System: 刑事偵查輔助系統 (Criminal Investigation Analysis System v2.0)

BEGIN;

-- 11. 法定規範基準庫 (statute_references)
CREATE TABLE IF NOT EXISTS statute_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    law_name VARCHAR(128) NOT NULL,
    article_number VARCHAR(32) NOT NULL,
    paragraph INTEGER NOT NULL DEFAULT 1,
    subparagraph VARCHAR(32),
    content TEXT NOT NULL,
    effective_date DATE NOT NULL,
    expiry_date DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT uq_statute_article_version 
        UNIQUE (law_name, article_number, paragraph, subparagraph, effective_date)
);

-- 12. 裁判例與實務見解庫 (precedent_references)
CREATE TABLE IF NOT EXISTS precedent_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    court_level VARCHAR(64) NOT NULL,
    case_identifier VARCHAR(128) NOT NULL UNIQUE,
    verdict_date DATE NOT NULL,
    holding_summary TEXT NOT NULL,
    topic_tags TEXT[] NOT NULL DEFAULT '{}',
    verified_in_law_bank BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- 13. 候選法律方向/罪名表 (legal_candidates)
CREATE TABLE IF NOT EXISTS legal_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    revision_id UUID NOT NULL,
    statute_id UUID NOT NULL REFERENCES statute_references(id) ON DELETE RESTRICT,
    charge_name VARCHAR(128) NOT NULL,
    status candidate_status_enum NOT NULL,
    rationale TEXT NOT NULL,
    competition_type VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT fk_legal_candidates_revision 
        FOREIGN KEY (case_id, revision_id) 
        REFERENCES case_revisions(case_id, id) 
        ON DELETE RESTRICT,
    CONSTRAINT uq_candidate_per_revision 
        UNIQUE (revision_id, statute_id, charge_name)
);

-- 14. 罪名構成要件拆解表 (constituent_elements)
CREATE TABLE IF NOT EXISTS constituent_elements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    revision_id UUID NOT NULL,
    candidate_id UUID NOT NULL REFERENCES legal_candidates(id) ON DELETE CASCADE,
    element_type VARCHAR(32) NOT NULL,
    element_name VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    status element_status_enum NOT NULL DEFAULT 'UNRESOLVED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT fk_constituent_elements_revision 
        FOREIGN KEY (case_id, revision_id) 
        REFERENCES case_revisions(case_id, id) 
        ON DELETE RESTRICT
);

-- 15. 構成要件與事實證據映射表 (element_fact_mappings)
CREATE TABLE IF NOT EXISTS element_fact_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    element_id UUID NOT NULL REFERENCES constituent_elements(id) ON DELETE CASCADE,
    fact_id UUID NOT NULL REFERENCES facts(id) ON DELETE RESTRICT,
    support_type VARCHAR(32) NOT NULL DEFAULT 'SUPPORTS',
    weight NUMERIC(3,2) NOT NULL DEFAULT 1.00,
    analysis_note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT chk_element_fact_weight 
        CHECK (weight >= 0.00 AND weight <= 1.00),
    CONSTRAINT chk_support_type_valid 
        CHECK (support_type IN ('SUPPORTS', 'REFUTES', 'NEUTRAL')),
    CONSTRAINT uq_element_fact_pair 
        UNIQUE (element_id, fact_id)
);

-- 16. 核心爭點與待證事項表 (core_issues)
CREATE TABLE IF NOT EXISTS core_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    revision_id UUID NOT NULL,
    candidate_id UUID REFERENCES legal_candidates(id) ON DELETE SET NULL,
    issue_category VARCHAR(32) NOT NULL,
    title VARCHAR(255) NOT NULL,
    inquiry_target TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolution_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT fk_core_issues_revision 
        FOREIGN KEY (case_id, revision_id) 
        REFERENCES case_revisions(case_id, id) 
        ON DELETE RESTRICT,
    CONSTRAINT chk_issue_category_valid 
        CHECK (issue_category IN ('FACTUAL_DISPUTE', 'LEGAL_INTERPRETATION', 'EVIDENTIARY_SUFFICIENCY'))
);

COMMIT;
