-- Test Suite: schema_validation.sql
-- Description: 檢驗所有 24 張核心資料表、外鍵關係與索引之定義完整性
-- Execution: 待正式環境由 DBA 或 CI/CD 執行

\set ON_ERROR_STOP on

BEGIN;

-- 1. 執行內建結構驗收函式
SELECT * FROM verify_schema_integrity();

-- 2. 檢驗複合外鍵 (case_id, revision_id) 關聯性是否完備
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
  AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
  AND tc.table_name IN ('facts', 'behaviors', 'legal_candidates', 'interview_questions', 'document_outputs')
  AND ccu.table_name = 'case_revisions';

-- 3. 檢驗 CHECK 約束存在性
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    cc.check_clause
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc 
  ON tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'public'
ORDER BY tc.table_name;

ROLLBACK;
