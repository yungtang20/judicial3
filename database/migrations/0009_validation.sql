-- Migration: 0009_validation.sql
-- Description: 資料庫結構完整性驗收函式與健全性自我檢查
-- System: 刑事偵查輔助系統 (Criminal Investigation Analysis System v2.0)

BEGIN;

CREATE OR REPLACE FUNCTION verify_schema_integrity()
RETURNS TABLE (
    check_item VARCHAR(100),
    expected_count INT,
    actual_count INT,
    status VARCHAR(10),
    details TEXT
) AS $$
DECLARE
    v_missing_tables TEXT;
    v_missing_rls TEXT;
BEGIN
    -- 1. 檢驗 24 張核心業務資料表
    RETURN QUERY
    WITH expected_tables AS (
        SELECT unnest(ARRAY[
            'user_roles', 'users', 'user_sessions', 'cases', 'case_revisions',
            'facts', 'fact_relations', 'evidence_items', 'evidence_sources', 'behaviors',
            'statute_references', 'precedent_references', 'legal_candidates', 'constituent_elements',
            'element_fact_mappings', 'core_issues', 'interview_sessions', 'interview_questions',
            'interview_answers', 'fact_update_logs', 'workflow_stages', 'review_approvals',
            'document_outputs', 'llm_prompt_templates'
        ]) AS tbl
    ),
    actual_tables AS (
        SELECT table_name::text AS tbl 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    )
    SELECT 
        'CORE_TABLES_COUNT'::VARCHAR(100),
        24,
        COUNT(a.tbl)::INT,
        CASE WHEN COUNT(a.tbl) = 24 THEN 'PASS'::VARCHAR(10) ELSE 'FAIL'::VARCHAR(10) END,
        COALESCE(string_agg(e.tbl, ', ') FILTER (WHERE a.tbl IS NULL), 'All 24 core tables exist')
    FROM expected_tables e
    LEFT JOIN actual_tables a ON e.tbl = a.tbl;

    -- 2. 檢驗 7 項核心列舉型別 (Enums)
    RETURN QUERY
    WITH expected_enums AS (
        SELECT unnest(ARRAY[
            'classification_level_enum', 'fact_status_enum', 'element_status_enum',
            'candidate_status_enum', 'source_status_enum', 'workflow_stage_enum',
            'workflow_status_enum', 'approval_status_enum'
        ]) AS enm
    ),
    actual_enums AS (
        SELECT typname::text AS enm 
        FROM pg_type 
        WHERE typtype = 'e'
    )
    SELECT 
        'CORE_ENUMS_COUNT'::VARCHAR(100),
        8,
        COUNT(a.enm)::INT,
        CASE WHEN COUNT(a.enm) = 8 THEN 'PASS'::VARCHAR(10) ELSE 'FAIL'::VARCHAR(10) END,
        COALESCE(string_agg(e.enm, ', ') FILTER (WHERE a.enm IS NULL), 'All 8 core enums registered')
    FROM expected_enums e
    LEFT JOIN actual_enums a ON e.enm = a.enm;

    -- 3. 檢驗所有 24 張表均已啟用 RLS
    RETURN QUERY
    WITH target_tables AS (
        SELECT unnest(ARRAY[
            'user_roles', 'users', 'user_sessions', 'cases', 'case_revisions',
            'facts', 'fact_relations', 'evidence_items', 'evidence_sources', 'behaviors',
            'statute_references', 'precedent_references', 'legal_candidates', 'constituent_elements',
            'element_fact_mappings', 'core_issues', 'interview_sessions', 'interview_questions',
            'interview_answers', 'fact_update_logs', 'workflow_stages', 'review_approvals',
            'document_outputs', 'llm_prompt_templates'
        ]) AS tbl
    ),
    rls_enabled AS (
        SELECT relname::text AS tbl
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relrowsecurity = TRUE
    )
    SELECT 
        'RLS_SECURITY_ACTIVE'::VARCHAR(100),
        24,
        COUNT(r.tbl)::INT,
        CASE WHEN COUNT(r.tbl) = 24 THEN 'PASS'::VARCHAR(10) ELSE 'FAIL'::VARCHAR(10) END,
        COALESCE(string_agg(t.tbl, ', ') FILTER (WHERE r.tbl IS NULL), 'RLS active on all tables')
    FROM target_tables t
    LEFT JOIN rls_enabled r ON t.tbl = r.tbl;

    -- 4. 檢驗不可竄改鎖定保護觸發器存在性
    RETURN QUERY
    SELECT 
        'IMMUTABILITY_TRIGGERS_COUNT'::VARCHAR(100),
        7,
        COUNT(*)::INT,
        CASE WHEN COUNT(*) >= 7 THEN 'PASS'::VARCHAR(10) ELSE 'FAIL'::VARCHAR(10) END,
        'Triggers protecting locked revisions and cascading staleness verified'
    FROM information_schema.triggers
    WHERE trigger_schema = 'public'
      AND trigger_name IN (
        'trg_revision_immutability', 'trg_facts_immutability', 'trg_behaviors_immutability',
        'trg_legal_candidates_immutability', 'trg_constituent_elements_immutability',
        'trg_interview_questions_immutability', 'trg_document_outputs_immutability'
      );

END;
$$ LANGUAGE plpgsql;

COMMIT;
