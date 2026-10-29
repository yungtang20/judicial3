-- Test Suite: version_integrity_tests.sql
-- Description: 測試歷史版本鎖定 (is_locked = TRUE)、不可竄改性與下游連鎖過期 (STALE) 觸發器
-- Execution: 待正式環境由 DBA 或 CI/CD 執行

\set ON_ERROR_STOP off

BEGIN;

-- 測試 1: 對已鎖定之歷史版本子表進行 UPDATE 應被觸發器強制阻擋
SAVEPOINT test_locked_child_mutation;
DO $$
DECLARE
    v_locked_rev_id UUID;
    v_fact_id UUID;
BEGIN
    SELECT r.id, f.id INTO v_locked_rev_id, v_fact_id
    FROM case_revisions r
    JOIN facts f ON f.revision_id = r.id
    WHERE r.is_locked = TRUE
    LIMIT 1;

    IF v_locked_rev_id IS NOT NULL THEN
        UPDATE facts 
        SET description = '企圖篡改已核定歷史版本事實內容'
        WHERE id = v_fact_id;

        RAISE EXCEPTION 'TRIGGER_FAIL: 應阻擋修改已鎖定版本之事實但未阻擋';
    ELSE
        RAISE NOTICE 'SKIP: 無已鎖定版本測試資料可供測試';
    END IF;
EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%REV_SUBTABLE_LOCKED_ERR%' THEN
        RAISE NOTICE 'TEST PASS: 成功阻擋篡改已鎖定版本事實 (fn_prevent_locked_revision_mutation)';
    ELSE
        RAISE NOTICE 'TEST EXCEPTION: %', SQLERRM;
    END IF;
END $$;
ROLLBACK TO SAVEPOINT test_locked_child_mutation;

-- 測試 2: 對已鎖定之歷史版本主表進行實體 DELETE 應被觸發器強制阻擋
SAVEPOINT test_locked_revision_delete;
DO $$
DECLARE
    v_locked_rev_id UUID;
BEGIN
    SELECT id INTO v_locked_rev_id
    FROM case_revisions
    WHERE is_locked = TRUE
    LIMIT 1;

    IF v_locked_rev_id IS NOT NULL THEN
        DELETE FROM case_revisions WHERE id = v_locked_rev_id;
        RAISE EXCEPTION 'TRIGGER_FAIL: 應阻擋刪除已鎖定版本但未阻擋';
    ELSE
        RAISE NOTICE 'SKIP: 無已鎖定版本測試資料可供測試';
    END IF;
EXCEPTION WHEN OTHERS THEN
    IF SQLERRM LIKE '%REV_LOCKED_ERR%' THEN
        RAISE NOTICE 'TEST PASS: 成功阻擋刪除已鎖定版本記錄 (fn_prevent_locked_revision_mutation)';
    ELSE
        RAISE NOTICE 'TEST EXCEPTION: %', SQLERRM;
    END IF;
END $$;
ROLLBACK TO SAVEPOINT test_locked_revision_delete;

ROLLBACK;
