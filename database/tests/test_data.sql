-- Test Suite: test_data.sql
-- Description: 虛構模擬測試資料庫種子 (嚴禁真實案件個資或真實密鑰)
-- System: 刑事偵查輔助系統 (Criminal Investigation Analysis System v2.0)

BEGIN;

-- 1. 系統角色
INSERT INTO user_roles (id, role_code, role_name, permissions, description)
VALUES 
    ('11111111-1111-1111-1111-111111111101', 'LEAD_INVESTIGATOR', '主辦偵查官', '["case:create", "case:edit", "fact:edit", "interview:conduct", "document:draft"]'::jsonb, '主辦刑案偵查與事實整理人員'),
    ('11111111-1111-1111-1111-111111111102', 'REVIEWER', '審核長官', '["case:review", "document:approve", "revision:lock"]'::jsonb, '專案督導長官與簽核主管'),
    ('11111111-1111-1111-1111-111111111103', 'ANALYST', '犯罪分析員', '["case:read", "legal:research"]'::jsonb, '法規研究與智慧研析輔助人員')
ON CONFLICT (role_code) DO NOTHING;

-- 2. 測試使用者 (純虛構測試帳號；密碼僅供本機 seed，不得用於任何環境)
-- 本機測試密碼：Judicial3!TestPass2026（bcrypt cost 12）
INSERT INTO users (id, username, email, password_hash, full_name, badge_number, organization, role_id)
VALUES 
    ('22222222-2222-2222-2222-222222222201', 'lead_investigator_01', 'investigator01@simulated-police.gov.tw', '$2b$12$sYeEiM/8BErWHhrV8Q2rP.Xp.Qx/z/sSVaC.T/sUFgKV2hi4FJqsO', '陳○○偵查員', 'TP-99001', '刑事警察專案偵查第七大隊', '11111111-1111-1111-1111-111111111101'),
    ('22222222-2222-2222-2222-222222222202', 'reviewer_captain_01', 'reviewer01@simulated-police.gov.tw', '$2b$12$sYeEiM/8BErWHhrV8Q2rP.Xp.Qx/z/sSVaC.T/sUFgKV2hi4FJqsO', '李○○隊長', 'TP-99002', '刑事警察專案偵查第七大隊', '11111111-1111-1111-1111-111111111102'),
    ('22222222-2222-2222-2222-222222222203', 'analyst_unauthorized_02', 'analyst02@simulated-police.gov.tw', '$2b$12$sYeEiM/8BErWHhrV8Q2rP.Xp.Qx/z/sSVaC.T/sUFgKV2hi4FJqsO', '張○○分析員', 'TP-99003', '其他單位', '11111111-1111-1111-1111-111111111103')
ON CONFLICT (username) DO NOTHING;

-- 3. 法規條文基準
INSERT INTO statute_references (id, law_name, article_number, paragraph, subparagraph, content, effective_date, is_current)
VALUES 
    ('33333333-3333-3333-3333-333333333301', '中華民國刑法', '339-4', 1, '第2款、第3款', '犯第三百三十九條詐欺罪而有下列情形之一者，處一年以上七年以下有期徒刑，得併科一百萬元以下罰金：二、三人以上共同犯之。三、以廣播電視、電子通訊、網際網路或其他媒體等傳播工具，對公眾散布而犯之。', '2014-06-18', TRUE),
    ('33333333-3333-3333-3333-333333333302', '洗錢防制法', '14', 1, NULL, '有第二條各款所列洗錢行為者，處三年以上十年以下有期徒刑，併科新臺幣一億元以下罰金。其洗錢之財物或財產上利益未達新臺幣一億元者，處六月以上五年以下有期徒刑，併科新臺幣五千萬元以下罰金。', '2017-06-28', TRUE),
    ('33333333-3333-3333-3333-333333333303', '刑事訴訟法', '228', 1, NULL, '檢察官因告訴、告發、自首或其他情事知有犯罪嫌疑者，應即開始偵查。', '1967-01-28', TRUE)
ON CONFLICT (law_name, article_number, paragraph, subparagraph, effective_date) DO NOTHING;

-- 4. 實務裁判見解
INSERT INTO precedent_references (id, court_level, case_identifier, verdict_date, holding_summary, topic_tags, verified_in_law_bank)
VALUES 
    ('44444444-4444-4444-4444-444444444401', '最高法院', '最高法院 108 年度台上大字第 3101 號刑事裁定', '2019-10-23', '提供金融機構帳戶帳號及密碼予不相識之人，雖不能確定其用途，然通常可預見他人利用以掩飾隱匿犯罪所得，行為人仍基於縱若發生亦不違背其本意之不確定故意，應成立洗錢防制法之洗錢罪。', ARRAY['加重詐欺', '洗錢罪', '不確定故意', '人頭帳戶'], TRUE),
    ('44444444-4444-4444-4444-444444444402', '臺灣高等法院', '臺灣高等法院 112 年度金上訴字第 2454 號判決', '2023-11-15', '利用社群網路以投資虛擬貨幣為由施用詐術，分工縝密且受款後旋即分流提領，兼具三人以上共犯及網際網路傳播工具，該當刑法第339條之4加重詐欺要件。', ARRAY['加重詐欺', '三人以上共犯', '網路電信詐欺'], TRUE)
ON CONFLICT (case_identifier) DO NOTHING;

-- 5. 虛構案件主檔 (cases)
INSERT INTO cases (id, case_number, title, lead_investigator_id, classification_level)
VALUES 
    ('55555555-5555-5555-5555-555555555501', '115模擬偵字第0001號', '林○○受詐虛擬投資平臺案 (模擬測試案件)', '22222222-2222-2222-2222-222222222201', 'CONFIDENTIAL')
ON CONFLICT (case_number) DO NOTHING;

-- 6. 案件版本快照 (case_revisions)
INSERT INTO case_revisions (id, case_id, revision_number, revision_hash, change_summary, is_locked, created_by)
VALUES 
    ('66666666-6666-6666-6666-666666666601', '55555555-5555-5555-5555-555555555501', 1, 'a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90', '初始案情拆解與筆錄問句擬定 (初始版)', FALSE, '22222222-2222-2222-2222-222222222201')
ON CONFLICT (case_id, revision_number) DO NOTHING;

UPDATE cases 
SET current_revision_id = '66666666-6666-6666-6666-666666666601'
WHERE id = '55555555-5555-5555-5555-555555555501';

-- 7. 結構化事實 (facts)
INSERT INTO facts (id, case_id, revision_id, fact_seq, description, fact_type, status, confidence_score)
VALUES 
    ('77777777-7777-7777-7777-777777777701', '55555555-5555-5555-5555-555555555501', '66666666-6666-6666-6666-666666666601', 1, '報案人林○○於網路社群平台認識自稱從事投資之不詳男子。', 'STATEMENT', 'ASSERTED', 0.950),
    ('77777777-7777-7777-7777-777777777702', '55555555-5555-5555-5555-555555555501', '66666666-6666-6666-6666-666666666601', 2, '林○○依指示註冊虛假投資平台帳號，陸續匯款新臺幣30萬元至指定人頭帳戶。', 'OBJECTIVE', 'ADMITTED', 1.000),
    ('77777777-7777-7777-7777-777777777703', '55555555-5555-5555-5555-555555555501', '66666666-6666-6666-6666-666666666601', 3, '人頭帳戶名義人是否具備主觀詐欺或洗錢之故意。', 'STATE_OF_MIND', 'UNKNOWN', 0.500)
ON CONFLICT (revision_id, fact_seq) DO NOTHING;

-- 8. 行為人客觀行為拆解 (behaviors)
INSERT INTO behaviors (id, case_id, revision_id, actor_name, action_description, means_method, time_context)
VALUES 
    ('88888888-8888-8888-8888-888888888801', '55555555-5555-5555-5555-555555555501', '66666666-6666-6666-6666-666666666601', '不詳網路男子', '傳送虛假虛擬貨幣投資網站連結並誘導匯款', '社群網路訊息傳播與虛假獲利界面', '雙方聯繫約一個月期間'),
    ('88888888-8888-8888-8888-888888888802', '55555555-5555-5555-5555-555555555501', '66666666-6666-6666-6666-666666666601', '人頭帳戶名義人', '提供個人金融帳戶與提款卡供他人受款匯入', '金融機構開戶與交付網銀帳密', '被害人匯款前一週')
ON CONFLICT DO NOTHING;

-- 9. 候選法律方向 (legal_candidates)
INSERT INTO legal_candidates (id, case_id, revision_id, statute_id, charge_name, status, rationale)
VALUES 
    ('99999999-9999-9999-9999-999999999901', '55555555-5555-5555-5555-555555555501', '66666666-6666-6666-6666-666666666601', '33333333-3333-3333-3333-333333333301', '刑法第339條之4第1項加重詐欺罪', 'PRIMARY', '詐欺集團利用網際網路社群散布詐術訊息，且分工型態符合三人以上共同實行'),
    ('99999999-9999-9999-9999-999999999902', '55555555-5555-5555-5555-555555555501', '66666666-6666-6666-6666-666666666601', '33333333-3333-3333-3333-333333333302', '洗錢防制法第14條第1項洗錢罪', 'ALTERNATIVE', '掩飾或隱匿特定犯罪所得來源，帳戶名義人具備不確定故意之可能性')
ON CONFLICT (revision_id, statute_id, charge_name) DO NOTHING;

-- 10. 核心爭點 (core_issues)
INSERT INTO core_issues (id, case_id, revision_id, candidate_id, issue_category, title, inquiry_target)
VALUES 
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '55555555-5555-5555-5555-555555555501', '66666666-6666-6666-6666-666666666601', '99999999-9999-9999-9999-999999999902', 'FACTUAL_DISPUTE', '受款帳戶名義人交付帳戶之對價與主觀認知', '查明該名義人是否知悉款項非其合法所得，或有無領取對價報酬')
ON CONFLICT DO NOTHING;

-- 11. 筆錄問句 (interview_questions)
INSERT INTO interview_questions (id, case_id, revision_id, question_seq, question_text, target_issue_id, is_mandatory)
VALUES 
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbb01', '55555555-5555-5555-5555-555555555501', '66666666-6666-6666-6666-666666666601', 1, '你係於何時、何地，透過何種管道交付上開金融機構存摺、提款卡及密碼予他人？', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', TRUE),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbb02', '55555555-5555-5555-5555-555555555501', '66666666-6666-6666-6666-666666666601', 2, '交付該等帳戶資料時，對方有無承諾或實際給付任何金錢報酬或其他利益？', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', TRUE)
ON CONFLICT DO NOTHING;

-- 12. 流程階段 (workflow_stages)
INSERT INTO workflow_stages (id, case_id, revision_id, stage_name, status)
VALUES 
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', '55555555-5555-5555-5555-555555555501', '66666666-6666-6666-6666-666666666601', 'INTERVIEW_PREP', 'DRAFT')
ON CONFLICT (revision_id, stage_name) DO NOTHING;

-- 13. AI 提示詞範本 (llm_prompt_templates)
INSERT INTO llm_prompt_templates (id, template_code, version, system_prompt, user_prompt_pattern, output_schema_json)
VALUES 
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'LEGAL_DECOMPOSITION_V1', 1, '你是一名嚴謹的刑事偵查法制顧問。依據客觀案件事實，客觀拆解行為與構成要件。禁止自行判定罪名，應提出合理之替代法律方向。', '案件事實如下：{{case_description}}，請進行結構化拆解。', '{"type": "object", "properties": {"candidates": {"type": "array"}}}'::jsonb)
ON CONFLICT (template_code, version) DO NOTHING;

COMMIT;
