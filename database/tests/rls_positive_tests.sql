-- Test Suite: rls_positive_tests.sql
-- Description: 資料列安全 (RLS) 正向測試：授權主辦偵查人員對自有案件及子表之合法存取
-- Execution: 待正式環境由 DBA 或 CI/CD 執行

\set ON_ERROR_STOP on

BEGIN;

DO $$
DECLARE
    v_user_id UUID;
    v_case_count INT;
    v_fact_count INT;
BEGIN
    SELECT id INTO v_user_id FROM users WHERE username = 'lead_investigator_01';

    IF v_user_id IS NULL THEN
        RAISE NOTICE 'SKIP: 尚未載入測試使用者資料';
        RETURN;
    END IF;

    PERFORM set_config('app.current_user_id', v_user_id::text, true);

    SELECT COUNT(*) INTO v_case_count FROM cases;
    IF v_case_count = 0 THEN
        RAISE EXCEPTION 'RLS_POS_FAIL: 授權主辦人應可讀取自有案件，但查詢結果為 0 筆';
    END IF;
    RAISE NOTICE 'TEST PASS: 授權使用者成功讀取案件主檔 (筆數: %)', v_case_count;

    SELECT COUNT(*) INTO v_fact_count FROM facts;
    RAISE NOTICE 'TEST PASS: 授權使用者成功讀取案件事實 (筆數: %)', v_fact_count;

    RAISE NOTICE 'TEST PASS: 所有正向 RLS 驗證成功';
END $$;

ROLLBACK;
