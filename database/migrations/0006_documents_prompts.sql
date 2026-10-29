-- Migration: 0006_documents_prompts.sql
-- Description: 人工審核簽核、條陳/報告公文產出及 AI 提示詞範本版本管制表
-- System: 刑事偵查輔助系統 (Criminal Investigation Analysis System v2.0)

BEGIN;

-- 22. 人工審核閘門紀錄表 (review_approvals)
CREATE TABLE IF NOT EXISTS review_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    revision_id UUID NOT NULL,
    target_entity_type VARCHAR(64) NOT NULL,
    target_entity_id UUID NOT NULL,
    reviewer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    status approval_status_enum NOT NULL DEFAULT 'PENDING',
    comments TEXT NOT NULL,
    approval_hash VARCHAR(64) NOT NULL,
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT fk_review_approvals_revision 
        FOREIGN KEY (case_id, revision_id) 
        REFERENCES case_revisions(case_id, id) 
        ON DELETE RESTRICT,
    CONSTRAINT chk_target_entity_type_valid 
        CHECK (target_entity_type IN ('REVISION_SUMMARY', 'LEGAL_DIRECTION', 'DOCUMENT_OUTPUT', 'FACTS_PACKAGE'))
);

-- 23. 條陳、函稿與調查報告產出表 (document_outputs)
CREATE TABLE IF NOT EXISTS document_outputs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    revision_id UUID NOT NULL,
    document_type VARCHAR(32) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content_markdown TEXT NOT NULL,
    is_final BOOLEAN NOT NULL DEFAULT FALSE,
    approval_id UUID REFERENCES review_approvals(id) ON DELETE SET NULL,
    generated_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT fk_document_outputs_revision 
        FOREIGN KEY (case_id, revision_id) 
        REFERENCES case_revisions(case_id, id) 
        ON DELETE RESTRICT,
    CONSTRAINT chk_document_type_valid 
        CHECK (document_type IN ('MEMORANDUM', 'INVESTIGATION_REPORT', 'TRANSCRIPT_SUMMARY', 'LEGAL_OPINION')),
    CONSTRAINT chk_final_doc_requires_approval 
        CHECK (is_final = FALSE OR (is_final = TRUE AND approval_id IS NOT NULL))
);

-- 24. AI 輔助提示詞範本與版本管制表 (llm_prompt_templates)
CREATE TABLE IF NOT EXISTS llm_prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_code VARCHAR(64) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    system_prompt TEXT NOT NULL,
    user_prompt_pattern TEXT NOT NULL,
    output_schema_json JSONB NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT chk_prompt_template_version_pos CHECK (version >= 1),
    CONSTRAINT uq_prompt_template_version UNIQUE (template_code, version)
);

COMMIT;
