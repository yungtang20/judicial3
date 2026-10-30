-- Test Suite: constraint_tests.sql
-- Description: 資料庫層級約束 (CHECK / UNIQUE / FK) 完整性測試
-- Execution: 預期包含故意的失敗情境以驗證約束阻擋能力

\set ON_ERROR_STOP off

BEGIN;

-- 測試 1: 可信度評分超出界限 (< 0.000 或 > 1.000) 應被阻擋
SAVEPOINT test_confidence_bound;
DO $$
DECLARE
    v_case_id UUID;
    v_rev_id UUID;
BEGIN
    SELECT id, current_revision_id INTO v_case_id, v_rev_id FROM cases LIMIT 1;
    IF v_case_id IS NOT NULL THEN
        -- 故意插入 1.500 (非法)
        INSERT INTO facts (case_id, revision_id, fact_seq, description, status, confidence_score)
        VALUES (v_case_id, v_rev_id, 9999, '非法可信度測試', 'ASSERTED', 1.500);
        RAISE EXCEPTION 'CHECK_FAIL: 應阻擋大於 1.000 之可信度評分但未阻擋';
    END IF;
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'TEST PASS: 成功阻擋非法可信度評分 (chk_facts_confidence_range)';
END $$;
ROLLBACK TO SAVEPOINT test_confidence_bound;

-- 測試 2: 事實因果關聯自我循環 (source_fact_id = target_fact_id) 應被阻擋
SAVEPOINT test_fact_self_loop;
DO $$
DECLARE
    v_case_id UUID;
    v_rev_id UUID;
    v_fact_id UUID;
BEGIN
    SELECT id, case_id, revision_id INTO v_fact_id, v_case_id, v_rev_id FROM facts LIMIT 1;
    IF v_fact_id IS NOT NULL THEN
        INSERT INTO fact_relations (case_id, revision_id, source_fact_id, target_fact_id, relation_type, rationale)
        VALUES (v_case_id, v_rev_id, v_fact_id, v_fact_id, 'CAUSES', '自我循環非法測試');
        RAISE EXCEPTION 'CHECK_FAIL: 應阻擋事實自我循環關聯但未阻擋';
    END IF;
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'TEST PASS: 成功阻擋事實自我循環關聯 (chk_fact_rel_no_self_loop)';
END $$;
ROLLBACK TO SAVEPOINT test_fact_self_loop;

-- 測試 3: 正式公文條陳 (is_final = TRUE) 缺少核定審核 (approval_id IS NULL) 應被阻擋
SAVEPOINT test_final_doc_approval_required;
DO $$
DECLARE
    v_case_id UUID;
    v_rev_id UUID;
    v_user_id UUID;
BEGIN
    SELECT id, lead_investigator_id, current_revision_id INTO v_case_id, v_user_id, v_rev_id FROM cases LIMIT 1;
    IF v_case_id IS NOT NULL THEN
        INSERT INTO document_outputs (case_id, revision_id, document_type, title, content_markdown, is_final, approval_id, generated_by)
        VALUES (v_case_id, v_rev_id, 'MEMORANDUM', '未審核逕自核定條陳', '測試內容', TRUE, NULL, v_user_id);
        RAISE EXCEPTION 'CHECK_FAIL: 應阻擋未附審核簽核之正式條陳但未阻擋';
    END IF;
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'TEST PASS: 成功阻擋未審核之正式公文 (chk_final_doc_requires_approval)';
END $$;
ROLLBACK TO SAVEPOINT test_final_doc_approval_required;

-- 測試 4: 版本序號小於 1 應被阻擋
SAVEPOINT test_negative_rev_num;
DO $$
DECLARE
    v_case_id UUID;
    v_user_id UUID;
BEGIN
    SELECT id, lead_investigator_id INTO v_case_id, v_user_id FROM cases LIMIT 1;
    IF v_case_id IS NOT NULL THEN
        INSERT INTO case_revisions (case_id, revision_number, revision_hash, change_summary, created_by)
        VALUES (v_case_id, 0, 'dummyhash', '無效版本號測試', v_user_id);
        RAISE EXCEPTION 'CHECK_FAIL: 應阻擋小於 1 之版本序號但未阻擋';
    END IF;
EXCEPTION WHEN check_violation THEN
    RAISE NOTICE 'TEST PASS: 成功阻擋小於 1 之版本序號 (chk_rev_number_pos)';
END $$;
ROLLBACK TO SAVEPOINT test_negative_rev_num;

ROLLBACK;
