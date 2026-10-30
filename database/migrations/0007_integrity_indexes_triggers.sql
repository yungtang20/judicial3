-- Migration: 0007_integrity_indexes_triggers.sql
-- Description: 效能索引、不可竄改版本鎖定觸發器、雜湊校驗與下游過期無效化觸發器
-- System: 刑事偵查輔助系統 (Criminal Investigation Analysis System v2.0)

BEGIN;

-- 1. 核心查詢效能與外鍵索引
CREATE INDEX IF NOT EXISTS idx_cases_lead_investigator ON cases(lead_investigator_id);
CREATE INDEX IF NOT EXISTS idx_cases_archived ON cases(is_archived);
CREATE INDEX IF NOT EXISTS idx_case_revisions_case_num ON case_revisions(case_id, revision_number);
CREATE INDEX IF NOT EXISTS idx_case_revisions_locked ON case_revisions(is_locked);

CREATE INDEX IF NOT EXISTS idx_facts_case_rev ON facts(case_id, revision_id);
CREATE INDEX IF NOT EXISTS idx_facts_status ON facts(status);
CREATE INDEX IF NOT EXISTS idx_fact_relations_target ON fact_relations(target_fact_id);

CREATE INDEX IF NOT EXISTS idx_evidence_items_case_rev ON evidence_items(case_id, revision_id);
CREATE INDEX IF NOT EXISTS idx_evidence_sources_item ON evidence_sources(evidence_item_id);
CREATE INDEX IF NOT EXISTS idx_behaviors_case_rev ON behaviors(case_id, revision_id);

CREATE INDEX IF NOT EXISTS idx_statutes_lookup ON statute_references(law_name, article_number);
CREATE INDEX IF NOT EXISTS idx_precedents_tags ON precedent_references USING GIN(topic_tags);

CREATE INDEX IF NOT EXISTS idx_legal_candidates_case_rev ON legal_candidates(case_id, revision_id);
CREATE INDEX IF NOT EXISTS idx_constituent_elements_cand ON constituent_elements(candidate_id);
CREATE INDEX IF NOT EXISTS idx_elem_fact_map_fact ON element_fact_mappings(fact_id);
CREATE INDEX IF NOT EXISTS idx_core_issues_case_rev ON core_issues(case_id, revision_id);

CREATE INDEX IF NOT EXISTS idx_interview_sessions_case_rev ON interview_sessions(case_id, revision_id);
CREATE INDEX IF NOT EXISTS idx_interview_questions_session ON interview_questions(session_id);
CREATE INDEX IF NOT EXISTS idx_interview_answers_question ON interview_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_fact_updates_fact ON fact_update_logs(fact_id);

CREATE INDEX IF NOT EXISTS idx_workflow_stages_lookup ON workflow_stages(case_id, revision_id, stage_name);
CREATE INDEX IF NOT EXISTS idx_review_approvals_case_rev ON review_approvals(case_id, revision_id);
CREATE INDEX IF NOT EXISTS idx_document_outputs_case_rev ON document_outputs(case_id, revision_id);

-- 2. 觸發函式：防止對已鎖定版本進行修改或刪除 (Revision Immutability Guard)
CREATE OR REPLACE FUNCTION fn_prevent_locked_revision_mutation()
RETURNS TRIGGER AS $$
DECLARE
    v_locked BOOLEAN;
    v_rev_id UUID;
BEGIN
    IF TG_TABLE_NAME = 'case_revisions' THEN
        IF TG_OP = 'DELETE' THEN
            IF OLD.is_locked THEN
                RAISE EXCEPTION 'REV_LOCKED_ERR: 已鎖定之歷史版本 (ID: %) 禁止實體刪除。', OLD.id;
            END IF;
            RETURN OLD;
        ELSIF TG_OP = 'UPDATE' THEN
            IF OLD.is_locked AND (NEW.revision_hash <> OLD.revision_hash OR NEW.revision_number <> OLD.revision_number OR NEW.change_summary <> OLD.change_summary) THEN
                RAISE EXCEPTION 'REV_LOCKED_ERR: 已鎖定之歷史版本 (ID: %) 為不可竄改快照，禁止修改內容。', OLD.id;
            END IF;
            RETURN NEW;
        END IF;
    ELSE
        IF TG_OP = 'DELETE' THEN
            v_rev_id := OLD.revision_id;
        ELSE
            v_rev_id := NEW.revision_id;
        END IF;

        SELECT is_locked INTO v_locked FROM case_revisions WHERE id = v_rev_id;

        IF v_locked = TRUE THEN
            RAISE EXCEPTION 'REV_SUBTABLE_LOCKED_ERR: 資料表 % 之所屬版本 (%) 已核定鎖定，禁止異動子表紀錄。', TG_TABLE_NAME, v_rev_id;
        END IF;

        IF TG_OP = 'DELETE' THEN
            RETURN OLD;
        ELSE
            RETURN NEW;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_revision_immutability ON case_revisions;
CREATE TRIGGER trg_revision_immutability
    BEFORE UPDATE OR DELETE ON case_revisions
    FOR EACH ROW
    EXECUTE FUNCTION fn_prevent_locked_revision_mutation();

DROP TRIGGER IF EXISTS trg_facts_immutability ON facts;
CREATE TRIGGER trg_facts_immutability
    BEFORE INSERT OR UPDATE OR DELETE ON facts
    FOR EACH ROW EXECUTE FUNCTION fn_prevent_locked_revision_mutation();

DROP TRIGGER IF EXISTS trg_behaviors_immutability ON behaviors;
CREATE TRIGGER trg_behaviors_immutability
    BEFORE INSERT OR UPDATE OR DELETE ON behaviors
    FOR EACH ROW EXECUTE FUNCTION fn_prevent_locked_revision_mutation();

DROP TRIGGER IF EXISTS trg_legal_candidates_immutability ON legal_candidates;
CREATE TRIGGER trg_legal_candidates_immutability
    BEFORE INSERT OR UPDATE OR DELETE ON legal_candidates
    FOR EACH ROW EXECUTE FUNCTION fn_prevent_locked_revision_mutation();

DROP TRIGGER IF EXISTS trg_constituent_elements_immutability ON constituent_elements;
CREATE TRIGGER trg_constituent_elements_immutability
    BEFORE INSERT OR UPDATE OR DELETE ON constituent_elements
    FOR EACH ROW EXECUTE FUNCTION fn_prevent_locked_revision_mutation();

DROP TRIGGER IF EXISTS trg_interview_questions_immutability ON interview_questions;
CREATE TRIGGER trg_interview_questions_immutability
    BEFORE INSERT OR UPDATE OR DELETE ON interview_questions
    FOR EACH ROW EXECUTE FUNCTION fn_prevent_locked_revision_mutation();

DROP TRIGGER IF EXISTS trg_document_outputs_immutability ON document_outputs;
CREATE TRIGGER trg_document_outputs_immutability
    BEFORE INSERT OR UPDATE OR DELETE ON document_outputs
    FOR EACH ROW EXECUTE FUNCTION fn_prevent_locked_revision_mutation();

-- 3. 觸發函式：事實異動自動標記下游分析流程為過期 (Downstream Stale Cascade)
CREATE OR REPLACE FUNCTION fn_invalidate_downstream_on_fact_change()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE workflow_stages
    SET status = 'STALE',
        completed_at = NULL
    WHERE revision_id = COALESCE(NEW.revision_id, OLD.revision_id)
      AND stage_name IN ('ELEMENT_EVALUATION', 'INTERVIEW_PREP', 'DOCUMENT_GENERATION')
      AND status = 'APPROVED';

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_facts_stale_cascade ON facts;
CREATE TRIGGER trg_facts_stale_cascade
    AFTER INSERT OR UPDATE OR DELETE ON facts
    FOR EACH ROW EXECUTE FUNCTION fn_invalidate_downstream_on_fact_change();

-- 4. 觸發函式：更新 updated_at 時間戳記
CREATE OR REPLACE FUNCTION fn_touch_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = clock_timestamp();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_touch_updated_at ON users;
CREATE TRIGGER trg_users_touch_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION fn_touch_updated_at();

DROP TRIGGER IF EXISTS trg_cases_touch_updated_at ON cases;
CREATE TRIGGER trg_cases_touch_updated_at
    BEFORE UPDATE ON cases
    FOR EACH ROW EXECUTE FUNCTION fn_touch_updated_at();

COMMIT;
