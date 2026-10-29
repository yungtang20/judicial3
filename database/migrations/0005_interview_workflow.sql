-- Migration: 0005_interview_workflow.sql
-- Description: 筆錄詢問會話、問句擬定、回答記錄、事實異動日誌與流程狀態機表
-- System: 刑事偵查輔助系統 (Criminal Investigation Analysis System v2.0)

BEGIN;

-- 17. 筆錄詢問會話主表 (interview_sessions)
CREATE TABLE IF NOT EXISTS interview_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    revision_id UUID NOT NULL,
    interviewee_name VARCHAR(100) NOT NULL,
    interviewee_role VARCHAR(32) NOT NULL,
    interviewer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    ended_at TIMESTAMPTZ,
    rights_notified BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(32) NOT NULL DEFAULT 'PLANNED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT fk_interview_sessions_revision 
        FOREIGN KEY (case_id, revision_id) 
        REFERENCES case_revisions(case_id, id) 
        ON DELETE RESTRICT,
    CONSTRAINT chk_interviewee_role_valid 
        CHECK (interviewee_role IN ('SUSPECT', 'VICTIM', 'WITNESS', 'EXPERT', 'PERSON_OF_INTEREST')),
    CONSTRAINT chk_interview_status_valid 
        CHECK (status IN ('PLANNED', 'IN_PROGRESS', 'CONCLUDED', 'CANCELLED'))
);

-- 18. 筆錄擬定問句表 (interview_questions)
CREATE TABLE IF NOT EXISTS interview_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    revision_id UUID NOT NULL,
    session_id UUID REFERENCES interview_sessions(id) ON DELETE SET NULL,
    question_seq INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    target_element_id UUID REFERENCES constituent_elements(id) ON DELETE SET NULL,
    target_issue_id UUID REFERENCES core_issues(id) ON DELETE SET NULL,
    is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT fk_interview_questions_revision 
        FOREIGN KEY (case_id, revision_id) 
        REFERENCES case_revisions(case_id, id) 
        ON DELETE RESTRICT,
    CONSTRAINT uq_question_seq_per_session 
        UNIQUE (revision_id, session_id, question_seq)
);

-- 19. 筆錄受詢回答紀錄表 (interview_answers)
CREATE TABLE IF NOT EXISTS interview_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES interview_questions(id) ON DELETE CASCADE,
    answer_text TEXT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    eval_fact_status fact_status_enum NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

-- 20. 事實修正與反饋歷程表 (fact_update_logs)
CREATE TABLE IF NOT EXISTS fact_update_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    fact_id UUID NOT NULL REFERENCES facts(id) ON DELETE CASCADE,
    trigger_source VARCHAR(32) NOT NULL,
    trigger_reference_id UUID,
    previous_status fact_status_enum NOT NULL,
    new_status fact_status_enum NOT NULL,
    previous_description TEXT NOT NULL,
    new_description TEXT NOT NULL,
    changed_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT chk_trigger_source_valid 
        CHECK (trigger_source IN ('INTERVIEW_ANSWER', 'NEW_EVIDENCE', 'MANUAL_EDIT', 'CROSS_EXAMINATION'))
);

-- 21. 案件處理流程狀態機表 (workflow_stages)
CREATE TABLE IF NOT EXISTS workflow_stages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL,
    revision_id UUID NOT NULL,
    stage_name workflow_stage_enum NOT NULL,
    status workflow_status_enum NOT NULL DEFAULT 'DRAFT',
    entered_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    completed_at TIMESTAMPTZ,
    CONSTRAINT fk_workflow_stages_revision 
        FOREIGN KEY (case_id, revision_id) 
        REFERENCES case_revisions(case_id, id) 
        ON DELETE RESTRICT,
    CONSTRAINT uq_stage_per_revision 
        UNIQUE (revision_id, stage_name)
);

COMMIT;
