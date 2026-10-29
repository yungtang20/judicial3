-- Migration: 0008_rls_policies.sql
-- Description: 資料列層級安全政策 (Row-Level Security, RLS) 與會話身分判定函式
-- System: 刑事偵查輔助系統 (Criminal Investigation Analysis System v2.0)

BEGIN;

-- 1. 當前操作者身分取得函式 (相容標準 PostgreSQL Session 與 Supabase Auth)
CREATE OR REPLACE FUNCTION current_app_user_id() 
RETURNS UUID AS $$
BEGIN
    -- 優先自 PostgreSQL Session 設定取得 (SET LOCAL app.current_user_id = '...')
    IF NULLIF(current_setting('app.current_user_id', true), '') IS NOT NULL THEN
        RETURN current_setting('app.current_user_id', true)::UUID;
    END IF;

    -- 備援相容 Supabase JWT Claim (request.jwt.claim.sub)
    BEGIN
        IF NULLIF(current_setting('request.jwt.claim.sub', true), '') IS NOT NULL THEN
            RETURN current_setting('request.jwt.claim.sub', true)::UUID;
        END IF;
    EXCEPTION WHEN OTHERS THEN
        NULL;
    END;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- 2. 判斷當前使用者是否為管理員/督察長官
CREATE OR REPLACE FUNCTION is_app_admin_or_reviewer()
RETURNS BOOLEAN AS $$
DECLARE
    v_role_code VARCHAR(32);
BEGIN
    SELECT r.role_code INTO v_role_code
    FROM users u
    JOIN user_roles r ON u.role_id = r.id
    WHERE u.id = current_app_user_id() AND u.is_active = TRUE;

    RETURN v_role_code IN ('ADMIN', 'REVIEWER', 'SUPERVISOR');
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- 3. 啟用所有 24 張資料表之 RLS (Enable & Force RLS)
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles FORCE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions FORCE ROW LEVEL SECURITY;
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE cases FORCE ROW LEVEL SECURITY;
ALTER TABLE case_revisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE case_revisions FORCE ROW LEVEL SECURITY;
ALTER TABLE facts ENABLE ROW LEVEL SECURITY;
ALTER TABLE facts FORCE ROW LEVEL SECURITY;
ALTER TABLE fact_relations ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_relations FORCE ROW LEVEL SECURITY;
ALTER TABLE evidence_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_items FORCE ROW LEVEL SECURITY;
ALTER TABLE evidence_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_sources FORCE ROW LEVEL SECURITY;
ALTER TABLE behaviors ENABLE ROW LEVEL SECURITY;
ALTER TABLE behaviors FORCE ROW LEVEL SECURITY;
ALTER TABLE statute_references ENABLE ROW LEVEL SECURITY;
ALTER TABLE statute_references FORCE ROW LEVEL SECURITY;
ALTER TABLE precedent_references ENABLE ROW LEVEL SECURITY;
ALTER TABLE precedent_references FORCE ROW LEVEL SECURITY;
ALTER TABLE legal_candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE legal_candidates FORCE ROW LEVEL SECURITY;
ALTER TABLE constituent_elements ENABLE ROW LEVEL SECURITY;
ALTER TABLE constituent_elements FORCE ROW LEVEL SECURITY;
ALTER TABLE element_fact_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE element_fact_mappings FORCE ROW LEVEL SECURITY;
ALTER TABLE core_issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE core_issues FORCE ROW LEVEL SECURITY;
ALTER TABLE interview_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_sessions FORCE ROW LEVEL SECURITY;
ALTER TABLE interview_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_questions FORCE ROW LEVEL SECURITY;
ALTER TABLE interview_answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_answers FORCE ROW LEVEL SECURITY;
ALTER TABLE fact_update_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_update_logs FORCE ROW LEVEL SECURITY;
ALTER TABLE workflow_stages ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_stages FORCE ROW LEVEL SECURITY;
ALTER TABLE review_approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE review_approvals FORCE ROW LEVEL SECURITY;
ALTER TABLE document_outputs ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_outputs FORCE ROW LEVEL SECURITY;
ALTER TABLE llm_prompt_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE llm_prompt_templates FORCE ROW LEVEL SECURITY;

-- 4. 基礎與公共字典表政策 (Statutes, Precedents, Prompt Templates, Roles)
DROP POLICY IF EXISTS p_user_roles_read ON user_roles;
CREATE POLICY p_user_roles_read ON user_roles FOR SELECT TO PUBLIC
    USING (current_app_user_id() IS NOT NULL);

DROP POLICY IF EXISTS p_statute_read ON statute_references;
CREATE POLICY p_statute_read ON statute_references FOR SELECT TO PUBLIC
    USING (current_app_user_id() IS NOT NULL);

DROP POLICY IF EXISTS p_precedent_read ON precedent_references;
CREATE POLICY p_precedent_read ON precedent_references FOR SELECT TO PUBLIC
    USING (current_app_user_id() IS NOT NULL);

DROP POLICY IF EXISTS p_prompts_read ON llm_prompt_templates;
CREATE POLICY p_prompts_read ON llm_prompt_templates FOR SELECT TO PUBLIC
    USING (current_app_user_id() IS NOT NULL);

-- 5. 使用者與 Session 政策
DROP POLICY IF EXISTS p_users_select ON users;
CREATE POLICY p_users_select ON users FOR SELECT TO PUBLIC
    USING (current_app_user_id() IS NOT NULL AND (id = current_app_user_id() OR is_app_admin_or_reviewer()));

DROP POLICY IF EXISTS p_user_sessions_owner ON user_sessions;
CREATE POLICY p_user_sessions_owner ON user_sessions FOR ALL TO PUBLIC
    USING (user_id = current_app_user_id())
    WITH CHECK (user_id = current_app_user_id());

-- 6. 案件主檔政策 (cases)
DROP POLICY IF EXISTS p_cases_investigator ON cases;
CREATE POLICY p_cases_investigator ON cases FOR ALL TO PUBLIC
    USING (lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())
    WITH CHECK (lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer());

-- 7. 案件歷史版本快照 (case_revisions)
DROP POLICY IF EXISTS p_case_revisions_access ON case_revisions;
CREATE POLICY p_case_revisions_access ON case_revisions FOR ALL TO PUBLIC
    USING (
        EXISTS (
            SELECT 1 FROM cases c 
            WHERE c.id = case_revisions.case_id 
              AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM cases c 
            WHERE c.id = case_revisions.case_id 
              AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())
        )
    );

-- 8. 案件子表存取通用巨集式政策 (Facts, Behaviors, Evidence, Analysis, Interviews, Docs)

-- 8.1 facts
DROP POLICY IF EXISTS p_facts_isolation ON facts;
CREATE POLICY p_facts_isolation ON facts FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = facts.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = facts.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

-- 8.2 fact_relations
DROP POLICY IF EXISTS p_fact_relations_isolation ON fact_relations;
CREATE POLICY p_fact_relations_isolation ON fact_relations FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = fact_relations.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = fact_relations.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

-- 8.3 evidence_items & sources
DROP POLICY IF EXISTS p_evidence_items_isolation ON evidence_items;
CREATE POLICY p_evidence_items_isolation ON evidence_items FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = evidence_items.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = evidence_items.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

DROP POLICY IF EXISTS p_evidence_sources_isolation ON evidence_sources;
CREATE POLICY p_evidence_sources_isolation ON evidence_sources FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = evidence_sources.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = evidence_sources.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

-- 8.4 behaviors
DROP POLICY IF EXISTS p_behaviors_isolation ON behaviors;
CREATE POLICY p_behaviors_isolation ON behaviors FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = behaviors.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = behaviors.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

-- 8.5 legal_candidates, elements, mappings, core_issues
DROP POLICY IF EXISTS p_legal_candidates_isolation ON legal_candidates;
CREATE POLICY p_legal_candidates_isolation ON legal_candidates FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = legal_candidates.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = legal_candidates.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

DROP POLICY IF EXISTS p_constituent_elements_isolation ON constituent_elements;
CREATE POLICY p_constituent_elements_isolation ON constituent_elements FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = constituent_elements.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = constituent_elements.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

DROP POLICY IF EXISTS p_element_fact_mappings_isolation ON element_fact_mappings;
CREATE POLICY p_element_fact_mappings_isolation ON element_fact_mappings FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM constituent_elements e JOIN cases c ON c.id = e.case_id WHERE e.id = element_fact_mappings.element_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM constituent_elements e JOIN cases c ON c.id = e.case_id WHERE e.id = element_fact_mappings.element_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

DROP POLICY IF EXISTS p_core_issues_isolation ON core_issues;
CREATE POLICY p_core_issues_isolation ON core_issues FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = core_issues.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = core_issues.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

-- 8.6 interviews
DROP POLICY IF EXISTS p_interview_sessions_isolation ON interview_sessions;
CREATE POLICY p_interview_sessions_isolation ON interview_sessions FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = interview_sessions.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = interview_sessions.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

DROP POLICY IF EXISTS p_interview_questions_isolation ON interview_questions;
CREATE POLICY p_interview_questions_isolation ON interview_questions FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = interview_questions.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = interview_questions.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

DROP POLICY IF EXISTS p_interview_answers_isolation ON interview_answers;
CREATE POLICY p_interview_answers_isolation ON interview_answers FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM interview_questions q JOIN cases c ON c.id = q.case_id WHERE q.id = interview_answers.question_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM interview_questions q JOIN cases c ON c.id = q.case_id WHERE q.id = interview_answers.question_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

DROP POLICY IF EXISTS p_fact_update_logs_isolation ON fact_update_logs;
CREATE POLICY p_fact_update_logs_isolation ON fact_update_logs FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = fact_update_logs.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = fact_update_logs.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

-- 8.7 workflow, reviews & document outputs
DROP POLICY IF EXISTS p_workflow_stages_isolation ON workflow_stages;
CREATE POLICY p_workflow_stages_isolation ON workflow_stages FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = workflow_stages.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = workflow_stages.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

DROP POLICY IF EXISTS p_review_approvals_isolation ON review_approvals;
CREATE POLICY p_review_approvals_isolation ON review_approvals FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = review_approvals.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = review_approvals.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

DROP POLICY IF EXISTS p_document_outputs_isolation ON document_outputs;
CREATE POLICY p_document_outputs_isolation ON document_outputs FOR ALL TO PUBLIC
    USING (EXISTS (SELECT 1 FROM cases c WHERE c.id = document_outputs.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())))
    WITH CHECK (EXISTS (SELECT 1 FROM cases c WHERE c.id = document_outputs.case_id AND (c.lead_investigator_id = current_app_user_id() OR is_app_admin_or_reviewer())));

COMMIT;
