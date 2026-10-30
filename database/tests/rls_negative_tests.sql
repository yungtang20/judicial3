-- Test Suite: rls_negative_tests.sql
-- Description: 資料列安全 (RLS) 負向測試：阻斷未認證、跨案件越權與未授權寫入
-- Execution: 待正式環境由 DBA 或 CI/CD 執行

\set ON_ERROR_STOP off

BEGIN;

-- 測試 1: 未設定任何 Session 身分 (未登入狀態) 查詢案件應回傳 0 筆
SAVEPOINT test_unauthenticated_access;
DO $$
DECLARE
    v_count INT;
BEGIN
    -- 清空 session user
    PERFORM set_config('app.current_user_id', '', true);

    SELECT COUNT(*) INTO v_count FROM cases;
    IF v_count > 0 THEN
        RAISE EXCEPTION 'RLS_SEC_BREACH: 未認證連線不應讀取到任何案件，但讀取到 % 筆', v_count;
    END IF;
    RAISE NOTICE 'TEST PASS: 未認證連線被全面阻隔 (筆數: 0)';
END $$;
ROLLBACK TO SAVEPOINT test_unauthenticated_access;

-- 測試 2: 非承辦人 (使用者 B) 查詢使用者 A 之案件應回傳 0 筆
SAVEPOINT test_cross_tenant_read;
DO $$
DECLARE
    v_user_b_id UUID;
    v_user_a_case_id UUID;
    v_visible_count INT;
BEGIN
    SELECT id INTO v_user_b_id FROM users WHERE username = 'analyst_unauthorized_02';
    SELECT id INTO v_user_a_case_id FROM cases WHERE case_number = '115模擬偵字第0001號';

    IF v_user_b_id IS NOT NULL AND v_user_a_case_id IS NOT NULL THEN
        -- 切換至使用者 B
        PERFORM set_config('app.current_user_id', v_user_b_id::text, true);

        SELECT COUNT(*) INTO v_visible_count FROM cases WHERE id = v_user_a_case_id;
        IF v_visible_count > 0 THEN
            RAISE EXCEPTION 'RLS_SEC_BREACH: 使用者 B 越權讀取到使用者 A 之案件！';
        END IF;
        RAISE NOTICE 'TEST PASS: 成功阻擋跨案件越權查詢 (回傳 0 筆)';
    ELSE
        RAISE NOTICE 'SKIP: 缺少使用者 B 或案件 A 之測試資料';
    END IF;
END $$;
ROLLBACK TO SAVEPOINT test_cross_tenant_read;

-- 測試 3: 非承辦人 (使用者 B) 企圖向使用者 A 之案件注入事實應被 RLS WITH CHECK 阻擋
SAVEPOINT test_cross_tenant_insert;
DO $$
DECLARE
    v_user_b_id UUID;
    v_user_a_case_id UUID;
    v_user_a_rev_id UUID;
BEGIN
    SELECT id INTO v_user_b_id FROM users WHERE username = 'analyst_unauthorized_02';
    SELECT id, current_revision_id INTO v_user_a_case_id, v_user_a_rev_id FROM cases WHERE case_number = '115模擬偵字第0001號';

    IF v_user_b_id IS NOT NULL AND v_user_a_case_id IS NOT NULL THEN
        PERFORM set_config('app.current_user_id', v_user_b_id::text, true);

        -- 企圖向使用者 A 的案件注入非法事證
        INSERT INTO facts (case_id, revision_id, fact_seq, description, status)
        VALUES (v_user_a_case_id, v_user_a_rev_id, 999, '越權惡意注入事實', 'ASSERTED');

        RAISE EXCEPTION 'RLS_SEC_BREACH: RLS 應阻擋跨案件寫入事實但未阻擋！';
    END IF;
EXCEPTION WHEN insufficient_privilege THEN
    RAISE NOTICE 'TEST PASS: 成功阻擋跨案件寫入事實 (RLS WITH CHECK)';
WHEN OTHERS THEN
    IF SQLERRM LIKE '%row-level security%' THEN
        RAISE NOTICE 'TEST PASS: 成功阻擋跨案件寫入事實 (RLS violation)';
    ELSE
        RAISE NOTICE 'TEST EXCEPTION: %', SQLERRM;
    END IF;
END $$;
ROLLBACK TO SAVEPOINT test_cross_tenant_insert;

ROLLBACK;
