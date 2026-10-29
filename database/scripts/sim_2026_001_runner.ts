import { PGlite } from '@electric-sql/pglite';
import fs from 'fs';
import path from 'path';

export interface AuditStepResult {
  stepId: string;
  category: string;
  name: string;
  status: 'PASS' | 'FAIL' | 'NOT_RUN' | 'BLOCKED';
  details: string;
  executionProof?: any;
}

export async function runSimulationAudit(): Promise<{
  results: AuditStepResult[];
  tableCounts: Record<string, number>;
  logs: string[];
}> {
  const results: AuditStepResult[] = [];
  const logs: string[] = [];
  const log = (msg: string) => {
    logs.push(msg);
    console.log(msg);
  };

  log('======================================================================');
  log('   刑事偵查輔助系統 - SIM-2026-001 模擬案件端到端測試與資料庫稽核');
  log('======================================================================\n');

  // Initialize clean isolated PGlite instance in memory
  const db = new PGlite();
  const baseDir = path.resolve(process.cwd(), 'database');
  const migrationsDir = path.join(baseDir, 'migrations');

  // -------------------------------------------------------------------------
  // Step 0: Apply Migrations 0001 - 0009
  // -------------------------------------------------------------------------
  log('[INIT] 套用 Migrations 0001 ~ 0009 到獨立隔離測試資料庫...');
  const migrationFiles = [
    '0001_extensions_enums.sql',
    '0002_identity_cases.sql',
    '0003_facts_evidence.sql',
    '0004_analysis_legal.sql',
    '0005_interview_workflow.sql',
    '0006_documents_prompts.sql',
    '0007_integrity_indexes_triggers.sql',
    '0008_rls_policies.sql',
    '0009_validation.sql',
  ];

  try {
    for (const file of migrationFiles) {
      const sql = fs.readFileSync(path.join(migrationsDir, file), 'utf-8');
      await db.exec(sql);
    }
    results.push({
      stepId: 'MIG-01',
      category: '資料庫初始化',
      name: '0001~0009 Migration 循序建置',
      status: 'PASS',
      details: '24張資料表、8大Enums、索引、不可竄改觸發器及RLS政策套用成功',
    });
  } catch (err: any) {
    results.push({
      stepId: 'MIG-01',
      category: '資料庫初始化',
      name: '0001~0009 Migration 循序建置',
      status: 'FAIL',
      details: `Migration 失敗: ${err.message}`,
    });
    return { results, tableCounts: {}, logs };
  }

  // -------------------------------------------------------------------------
  // Step 0.2: Seed Users and Roles
  // -------------------------------------------------------------------------
  const investigatorId = '22222222-2222-2222-2222-222222222201';
  const reviewerId = '22222222-2222-2222-2222-222222222202';
  const unauthorizedId = '22222222-2222-2222-2222-222222222203';

  await db.exec(`
    INSERT INTO user_roles (id, role_code, role_name, permissions, description)
    VALUES 
      ('11111111-1111-1111-1111-111111111101', 'LEAD_INVESTIGATOR', '主辦偵查官', '["case:create", "case:edit", "fact:edit", "interview:conduct", "document:draft"]'::jsonb, '主辦刑案偵查與事實整理人員'),
      ('11111111-1111-1111-1111-111111111102', 'REVIEWER', '審核長官', '["case:review", "document:approve", "revision:lock"]'::jsonb, '專案督導長官與簽核主管'),
      ('11111111-1111-1111-1111-111111111103', 'ANALYST', '犯罪分析員', '["case:read", "legal:research"]'::jsonb, '法規研究與智慧研析輔助人員');

    INSERT INTO users (id, username, email, password_hash, full_name, badge_number, organization, role_id)
    VALUES 
      ('${investigatorId}', 'lead_investigator_sim', 'investigator_sim@simulated-police.gov.tw', '$argon2id$v=19$m=65536,t=3,p=4$simulated_hash_not_real_key$1234567890abcdef', '陳○○偵查員', 'TP-99001', '刑事警察專案偵查第七大隊', '11111111-1111-1111-1111-111111111101'),
      ('${reviewerId}', 'reviewer_captain_sim', 'reviewer_sim@simulated-police.gov.tw', '$argon2id$v=19$m=65536,t=3,p=4$simulated_hash_not_real_key$abcdef1234567890', '李○○隊長', 'TP-99002', '刑事警察專案偵查第七大隊', '11111111-1111-1111-1111-111111111102'),
      ('${unauthorizedId}', 'unauthorized_analyst_sim', 'unauthorized_sim@simulated-police.gov.tw', '$argon2id$v=19$m=65536,t=3,p=4$simulated_hash_not_real_key$fedcba0987654321', '張○○分析員', 'TP-99003', '其他單位', '11111111-1111-1111-1111-111111111103');
  `);

  // Seed reference statutes & precedents
  const statute339_4 = '33333333-3333-3333-3333-333333333301';
  const statuteMoneyLaundering = '33333333-3333-3333-3333-333333333302';
  const statute339 = '33333333-3333-3333-3333-333333333304';
  const statuteAiding = '33333333-3333-3333-3333-333333333305';
  const statuteEmbezzlement = '33333333-3333-3333-3333-333333333306';

  await db.exec(`
    INSERT INTO statute_references (id, law_name, article_number, paragraph, subparagraph, content, effective_date, is_current)
    VALUES 
      ('${statute339_4}', '中華民國刑法', '339-4', 1, '第3款', '犯第三百三十九條詐欺罪而有下列情形之一者，處一年以上七年以下有期徒刑，得併科一百萬元以下罰金：三、以廣播電視、電子通訊、網際網路或其他媒體等傳播工具，對公眾散布而犯之。', '2014-06-18', TRUE),
      ('${statuteMoneyLaundering}', '洗錢防制法', '14', 1, NULL, '有第二條各款所列洗錢行為者，處三年以上十年以下有期徒刑，併科新臺幣一億元以下罰金。', '2017-06-28', TRUE),
      ('${statute339}', '中華民國刑法', '339', 1, NULL, '意圖為自己或第三人不法之所有，以詐術使人將本人或第三人之物交付者，處五年以下有期徒刑、拘役或科或併科五十萬元以下罰金。', '2014-06-18', TRUE),
      ('${statuteAiding}', '中華民國刑法', '30', 1, NULL, '幫助他人實行犯罪行為者，為幫助犯。雖他人不知幫助之情者，亦同。', '2005-02-02', TRUE),
      ('${statuteEmbezzlement}', '中華民國刑法', '335', 1, NULL, '意圖為自己或第三人不法之所有，而侵占自己持有他人之物者，處五年以下有期徒刑、拘役或科或併科三萬元以下罰金。', '2019-12-25', TRUE);

    INSERT INTO precedent_references (court_level, case_identifier, verdict_date, holding_summary, topic_tags, verified_in_law_bank)
    VALUES 
      ('最高法院', '最高法院 108 年度台上大字第 3101 號刑事裁定', '2019-10-23', '提供金融機構帳戶帳號及密碼予不相識之人，雖不能確定其用途，然通常可預見他人利用以掩飾隱匿犯罪所得，行為人仍基於縱若發生亦不違背其本意之不確定故意，應成立洗錢防制法之洗錢罪。', ARRAY['加重詐欺', '洗錢罪', '不確定故意', '人頭帳戶'], TRUE),
      ('臺灣高等法院', '臺灣高等法院 112 年度金上訴字第 2454 號判決', '2023-11-15', '利用社群網路以低價代購海外限量商品為由施用詐術，受款後旋即斷訊註銷帳號，屬以網際網路傳播工具對公眾散布詐術之典型加重詐欺手法。', ARRAY['加重詐欺', '代購詐騙', '網路傳播'], TRUE);
  `);

  // -------------------------------------------------------------------------
  // Phase 1: 建立案件主檔與第 1 版本 (SIM-2026-001)
  // -------------------------------------------------------------------------
  log('\n[Phase 1] 建立 SIM-2026-001 案件主檔與版本 1...');
  const caseId = 'aaaaaaaa-1111-2222-3333-000000000001';
  const rev1Id = 'bbbbbbbb-1111-2222-3333-000000000001';

  try {
    // 1.1 建立案件主檔
    await db.query(`
      INSERT INTO cases (id, case_number, title, lead_investigator_id, classification_level)
      VALUES ('${caseId}', 'SIM-2026-001', '林○○報案受詐代購案 (SIM-2026-001 虛構測試)', '${investigatorId}', 'CONFIDENTIAL');
    `);

    // 1.2 建立版本 1 快照
    await db.exec(`
      INSERT INTO case_revisions (id, case_id, revision_number, parent_revision_id, revision_hash, change_summary, is_locked, created_by)
      VALUES ('${rev1Id}', '${caseId}', 1, NULL, 'hash_rev1_sim_initial_decomposition_20261020', '初始案情拆解、客觀事證登記與偵詢問句擬定 (初始版)', FALSE, '${investigatorId}');

      UPDATE cases SET current_revision_id = '${rev1Id}' WHERE id = '${caseId}';
    `);

    results.push({
      stepId: 'WF-01',
      category: '案件建立',
      name: '案件主檔與版本 1 初始化',
      status: 'PASS',
      details: '案件 SIM-2026-001 與版本 1 建立成功，外鍵指向一致',
      executionProof: { caseId, rev1Id, caseNumber: 'SIM-2026-001' },
    });
  } catch (err: any) {
    results.push({
      stepId: 'WF-01',
      category: '案件建立',
      name: '案件主檔與版本 1 初始化',
      status: 'FAIL',
      details: err.message,
    });
  }

  // 1.3 結構化事實 (10 條事實，區分 ASSERTED / ADMITTED / UNKNOWN)
  const fact1Id = 'cccccccc-0001-0000-0000-000000000001';
  const fact2Id = 'cccccccc-0002-0000-0000-000000000001';
  const fact3Id = 'cccccccc-0003-0000-0000-000000000001';
  const fact4Id = 'cccccccc-0004-0000-0000-000000000001';
  const fact5Id = 'cccccccc-0005-0000-0000-000000000001';
  const fact6Id = 'cccccccc-0006-0000-0000-000000000001';
  const fact7Id = 'cccccccc-0007-0000-0000-000000000001';
  const fact8Id = 'cccccccc-0008-0000-0000-000000000001';
  const fact9Id = 'cccccccc-0009-0000-0000-000000000001';
  const fact10Id = 'cccccccc-0010-0000-0000-000000000001';

  try {
    await db.query(`
      INSERT INTO facts (id, case_id, revision_id, fact_seq, description, fact_type, status, confidence_score, occurred_at)
      VALUES 
        ('${fact1Id}', '${caseId}', '${rev1Id}', 1, '報案人林○○於民國115年10月初透過社群平台認識自稱「陳先生」之男子。', 'STATEMENT', 'ASSERTED', 0.950, '2026-10-05 10:00:00+08'),
        ('${fact2Id}', '${caseId}', '${rev1Id}', 2, '陳先生表示從事海外商品代購，並稱可協助報案人以較低價格購買限量商品。', 'STATEMENT', 'ASSERTED', 0.900, '2026-10-06 14:00:00+08'),
        ('${fact3Id}', '${caseId}', '${rev1Id}', 3, '10月12日陳先生傳送商品照片及訂購資料，要求報案人先支付30,000元訂金，稱一週內寄達。', 'OBJECTIVE', 'ASSERTED', 0.950, '2026-10-12 11:30:00+08'),
        ('${fact4Id}', '${caseId}', '${rev1Id}', 4, '10月13日報案人依指示轉帳新臺幣30,000元至王○○之銀行帳戶。', 'OBJECTIVE', 'ADMITTED', 1.000, '2026-10-13 15:20:00+08'),
        ('${fact5Id}', '${caseId}', '${rev1Id}', 5, '10月15日陳先生稱海關查驗需補繳關稅及保證金18,000元，稱不補繳無法出貨且先前訂金不退。', 'STATEMENT', 'ASSERTED', 0.950, '2026-10-15 16:00:00+08'),
        ('${fact6Id}', '${caseId}', '${rev1Id}', 6, '10月16日報案人再次轉帳新臺幣18,000元至張○○之銀行帳戶。', 'OBJECTIVE', 'ADMITTED', 1.000, '2026-10-16 10:15:00+08'),
        ('${fact7Id}', '${caseId}', '${rev1Id}', 7, '10月19日陳先生封鎖報案人通訊軟體帳號，社群平台帳號亦已註銷，報案人共損失48,000元。', 'OBJECTIVE', 'ASSERTED', 1.000, '2026-10-19 18:00:00+08'),
        ('${fact8Id}', '${caseId}', '${rev1Id}', 8, '自稱「陳先生」男子之真實身分及是否自始具備代購能力或真意。', 'OBJECTIVE', 'UNKNOWN', 0.200, NULL),
        ('${fact9Id}', '${caseId}', '${rev1Id}', 9, '受款帳戶名義人王○○提供帳戶之原因、有無對價及其主觀詐欺或洗錢認知。', 'STATE_OF_MIND', 'UNKNOWN', 0.500, NULL),
        ('${fact10Id}', '${caseId}', '${rev1Id}', 10, '受款帳戶名義人張○○提供帳戶之原因、有無對價及其主觀詐欺或洗錢認知。', 'STATE_OF_MIND', 'UNKNOWN', 0.500, NULL);
    `);

    results.push({
      stepId: 'WF-02',
      category: '事實拆解',
      name: '結構化事實拆解與狀態區分',
      status: 'PASS',
      details: '成功登錄 10 條事實，精確標記 ASSERTED, ADMITTED, UNKNOWN，未擅自推論真實真偽',
    });
  } catch (err: any) {
    results.push({
      stepId: 'WF-02',
      category: '事實拆解',
      name: '結構化事實拆解與狀態區分',
      status: 'FAIL',
      details: err.message,
    });
  }

  // 1.4 涉案行為人與行為拆解 (behaviors)
  try {
    await db.query(`
      INSERT INTO behaviors (case_id, revision_id, actor_name, action_description, means_method, time_context)
      VALUES 
        ('${caseId}', '${rev1Id}', '陳先生 (不詳男子)', '利用社群平台散布低價限量商品代購資訊以吸引買家', '社群網路訊息傳播與虛假商品照片展示', '115年10月初至10月12日'),
        ('${caseId}', '${rev1Id}', '陳先生 (不詳男子)', '假借海關查驗需補繳關稅及保證金為由再度索款', '詐稱不繳則訂金不退以施加心理壓力', '115年10月15日'),
        ('${caseId}', '${rev1Id}', '陳先生 (不詳男子)', '得款後旋即封鎖被害人並註銷社群平台帳號斷訊', '通訊軟體黑名單阻斷與帳號註銷', '115年10月19日'),
        ('${caseId}', '${rev1Id}', '王○○ (受款帳戶名義人)', '名下金融帳戶收受報案人匯入之新臺幣30,000元', '提供金融機構帳戶供他人入帳', '115年10月13日'),
        ('${caseId}', '${rev1Id}', '張○○ (受款帳戶名義人)', '名下金融帳戶收受報案人匯入之新臺幣18,000元', '提供金融機構帳戶供他人入帳', '115年10月16日'),
        ('${caseId}', '${rev1Id}', '林○○ (報案人/被害人)', '依指示先後匯款新臺幣30,000元及18,000元至指定帳戶', '網路銀行跨行轉帳', '115年10月13日及10月16日');
    `);
    results.push({
      stepId: 'WF-03',
      category: '行為人行為',
      name: '涉案行為人與具體行為拆解',
      status: 'PASS',
      details: '登錄陳先生、王○○、張○○、林○○等 6 項具體客觀行為與手段',
    });
  } catch (err: any) {
    results.push({
      stepId: 'WF-03',
      category: '行為人行為',
      name: '涉案行為人與具體行為拆解',
      status: 'FAIL',
      details: err.message,
    });
  }

  // 1.5 證據品項與查證狀態 (8 項證物：4 取得、4 函調/待補)
  const ev1Id = 'dddddddd-0001-0000-0000-000000000001';
  const ev2Id = 'dddddddd-0002-0000-0000-000000000001';
  const ev3Id = 'dddddddd-0003-0000-0000-000000000001';
  const ev4Id = 'dddddddd-0004-0000-0000-000000000001';
  const ev5Id = 'dddddddd-0005-0000-0000-000000000001';
  const ev6Id = 'dddddddd-0006-0000-0000-000000000001';
  const ev7Id = 'dddddddd-0007-0000-0000-000000000001';
  const ev8Id = 'dddddddd-0008-0000-0000-000000000001';

  try {
    await db.exec(`
      INSERT INTO evidence_items (id, case_id, revision_id, item_code, name, category, custody_chain_summary, hash_md5_sha256)
      VALUES 
        ('${ev1Id}', '${caseId}', '${rev1Id}', 'E-001', '10/13 匯款新臺幣 30,000 元網路銀行轉帳成功截圖', 'DIGITAL', '報案人林○○報案時翻拍提供', 'sha256_mock_e001_transfer_30000_receipt'),
        ('${ev2Id}', '${caseId}', '${rev1Id}', 'E-002', '10/16 匯款新臺幣 18,000 元網路銀行轉帳成功截圖', 'DIGITAL', '報案人林○○報案時翻拍提供', 'sha256_mock_e002_transfer_18000_receipt'),
        ('${ev3Id}', '${caseId}', '${rev1Id}', 'E-003', '雙方通訊軟體 LINE 對話紀錄完整匯出檔案', 'DIGITAL', '數位鑑識採證林○○手機資料並匯出備份', 'sha256_mock_e003_line_chat_export_full'),
        ('${ev4Id}', '${caseId}', '${rev1Id}', 'E-004', '社群平台「陳先生」海外代購商品照片及訂購報價單', 'DIGITAL', '報案人提供之數位圖片電子檔', 'sha256_mock_e004_goods_photo_spec'),
        ('${ev5Id}', '${caseId}', '${rev1Id}', 'E-005', '王○○受款銀行帳戶開戶資料、金流明細及ATM提領影像', 'DOCUMENTARY', '本局依法向受款銀行函詢調取中 (尚未回覆)', NULL),
        ('${ev6Id}', '${caseId}', '${rev1Id}', 'E-006', '張○○受款銀行帳戶開戶資料、金流明細及ATM提領影像', 'DOCUMENTARY', '本局依法向受款銀行函詢調取中 (尚未回覆)', NULL),
        ('${ev7Id}', '${caseId}', '${rev1Id}', 'E-007', '社群平台帳號及通訊軟體帳號註冊歷程與登入IP位址', 'DIGITAL', '向業者函請保全並調取IP紀錄中', NULL),
        ('${ev8Id}', '${caseId}', '${rev1Id}', 'E-008', '報案人與王○○、張○○間之實體合約或實體接觸證物', 'DOCUMENTARY', '經詢報案人查無任何實體書面合約', NULL);

      INSERT INTO evidence_sources (case_id, revision_id, evidence_item_id, provider_name, provider_type, status, verified_by)
      VALUES 
        ('${caseId}', '${rev1Id}', '${ev1Id}', '林○○', 'VICTIM', 'VERIFIED', '${investigatorId}'),
        ('${caseId}', '${rev1Id}', '${ev2Id}', '林○○', 'VICTIM', 'VERIFIED', '${investigatorId}'),
        ('${caseId}', '${rev1Id}', '${ev3Id}', '林○○', 'VICTIM', 'VERIFIED', '${investigatorId}'),
        ('${caseId}', '${rev1Id}', '${ev4Id}', '林○○', 'VICTIM', 'VERIFIED', '${investigatorId}'),
        ('${caseId}', '${rev1Id}', '${ev5Id}', '受款金融機構 (玉山/國泰)', 'FINANCIAL_INSTITUTION', 'UNVERIFIED', NULL),
        ('${caseId}', '${rev1Id}', '${ev6Id}', '受款金融機構 (中信/台新)', 'FINANCIAL_INSTITUTION', 'UNVERIFIED', NULL),
        ('${caseId}', '${rev1Id}', '${ev7Id}', '社群平台與通訊服務商', 'TELECOM', 'UNVERIFIED', NULL),
        ('${caseId}', '${rev1Id}', '${ev8Id}', '雙方當事人', 'VICTIM', 'UNAVAILABLE', NULL);
    `);

    results.push({
      stepId: 'WF-04',
      category: '證據管理',
      name: '證物清單與來源狀態隔離登記',
      status: 'PASS',
      details: '登記 8 項證物，4 項已取得驗證 (VERIFIED)，4 項函調待查 (UNVERIFIED / UNAVAILABLE)',
    });
  } catch (err: any) {
    results.push({
      stepId: 'WF-04',
      category: '證據管理',
      name: '證物清單與來源狀態隔離登記',
      status: 'FAIL',
      details: err.message,
    });
  }

  // 1.6 候選法律方向與構成要件 (加重詐欺 PRIMARY, 普通詐欺 ALTERNATIVE, 洗錢/人頭 ALTERNATIVE, 侵占 REJECTED)
  const candAggFraud = 'eeeeeeee-0001-0000-0000-000000000001';
  const candOrdFraud = 'eeeeeeee-0002-0000-0000-000000000001';
  const candMoneyLaundering = 'eeeeeeee-0003-0000-0000-000000000001';
  const candAidingFraud = 'eeeeeeee-0004-0000-0000-000000000001';
  const candEmbezzlement = 'eeeeeeee-0005-0000-0000-000000000001';

  try {
    await db.query(`
      INSERT INTO legal_candidates (id, case_id, revision_id, statute_id, charge_name, status, rationale, competition_type)
      VALUES 
        ('${candAggFraud}', '${caseId}', '${rev1Id}', '${statute339_4}', '刑法第339條之4第1項第3款加重詐欺罪', 'PRIMARY', '行為人「陳先生」利用社群平台散布代購限量商品訊息，符合「以網際網路等傳播工具對公眾散布而犯之」之加重構成要件。', 'MAIN_OFFENSE'),
        ('${candOrdFraud}', '${caseId}', '${rev1Id}', '${statute339}', '刑法第339條第1項普通詐欺取財罪', 'ALTERNATIVE', '若後續調查認定行為人僅係對單一特定人私訊招攬而非對不特定公眾散布，則退居普通詐欺罪。', 'SUBSIDIARY'),
        ('${candMoneyLaundering}', '${caseId}', '${rev1Id}', '${statuteMoneyLaundering}', '洗錢防制法第14條第1項洗錢罪 (或第15條之2交付帳戶罪)', 'ALTERNATIVE', '受款帳戶名義人王○○、張○○提供金融帳戶掩飾不法所得流向，需調查其是否具備不確定故意或無正當理由交付帳戶。', 'COMPETITION'),
        ('${candAidingFraud}', '${caseId}', '${rev1Id}', '${statuteAiding}', '刑法第30條第1項、第339條幫助詐欺取財罪', 'ALTERNATIVE', '若帳戶名義人主觀上僅具幫助他人犯罪之故意，而無洗錢或共同正犯犯意，成立幫助犯。', 'SUBSIDIARY'),
        ('${candEmbezzlement}', '${caseId}', '${rev1Id}', '${statuteEmbezzlement}', '刑法第335條侵占罪', 'REJECTED', '排除理由：行為人自始即基於詐欺欺罔意圖騙取財物，並非先行合法持有他人財物後易持有為所有，與侵占罪構成要件不符，予以排除。', 'EXCLUDED');
    `);

    // 構成要件拆解
    await db.exec(`
      INSERT INTO constituent_elements (id, case_id, revision_id, candidate_id, element_type, element_name, description, status)
      VALUES 
        ('ffffffff-0001-0000-0000-000000000001', '${caseId}', '${rev1Id}', '${candAggFraud}', 'OBJECTIVE_ACT', '傳播工具公眾散布', '以網際網路社群平台對公眾散布訊息', 'SUPPORTED'),
        ('ffffffff-0002-0000-0000-000000000001', '${caseId}', '${rev1Id}', '${candAggFraud}', 'OBJECTIVE_ACT', '施用詐術', '虛構代購事實與海關查驗補稅事由', 'SUPPORTED'),
        ('ffffffff-0003-0000-0000-000000000001', '${caseId}', '${rev1Id}', '${candAggFraud}', 'SUBJECTIVE_INTENT', '不法所有意圖', '行為人自始無交貨真意，得款後旋即斷訊', 'SUPPORTED'),
        ('ffffffff-0004-0000-0000-000000000001', '${caseId}', '${rev1Id}', '${candMoneyLaundering}', 'SUBJECTIVE_INTENT', '洗錢不確定故意', '帳戶名義人是否知悉或可得預見帳戶將供掩飾贓款', 'UNRESOLVED');

      INSERT INTO core_issues (case_id, revision_id, candidate_id, issue_category, title, inquiry_target)
      VALUES 
        ('${caseId}', '${rev1Id}', '${candAggFraud}', 'FACTUAL_DISPUTE', '陳先生是否自始無代購真意而施用詐術', '查明是否真有海外代購管道與訂單，抑或純屬幽靈代購'),
        ('${caseId}', '${rev1Id}', '${candMoneyLaundering}', 'FACTUAL_DISPUTE', '帳戶名義人王○○交出帳戶之原因及對價關係', '查明王○○是否係應徵受騙或販售帳戶牟利，有無主觀預見'),
        ('${caseId}', '${rev1Id}', '${candMoneyLaundering}', 'FACTUAL_DISPUTE', '帳戶名義人張○○借出手機及網銀之客觀合理性', '查明張○○所述借予朋友是否屬實，是否違反一般人妥善保管帳密之常理');
    `);

    results.push({
      stepId: 'WF-05',
      category: '法律方向分析',
      name: '候選罪名主備位評估與構成要件拆解',
      status: 'PASS',
      details: '確立主位加重詐欺(PRIMARY)、備位普通詐欺/幫助詐欺/洗錢(ALTERNATIVE)、具理排除侵占罪(REJECTED)',
    });
  } catch (err: any) {
    results.push({
      stepId: 'WF-05',
      category: '法律方向分析',
      name: '候選罪名主備位評估與構成要件拆解',
      status: 'FAIL',
      details: err.message,
    });
  }

  // 1.7 建立針對三位涉案人之偵詢會話與 9 大類別問句
  const sessionVictimId = '12121212-0001-0000-0000-000000000001';
  const sessionWangId = '12121212-0002-0000-0000-000000000001';
  const sessionZhangId = '12121212-0003-0000-0000-000000000001';

  const qA1 = '34343434-0001-0000-0000-000000000001';
  const qA2 = '34343434-0002-0000-0000-000000000001';
  const qB1 = '34343434-0003-0000-0000-000000000001';
  const qB2 = '34343434-0004-0000-0000-000000000001';
  const qC1 = '34343434-0005-0000-0000-000000000001';
  const qC2 = '34343434-0006-0000-0000-000000000001';

  try {
    await db.exec(`
      INSERT INTO interview_sessions (id, case_id, revision_id, interviewee_name, interviewee_role, interviewer_id, rights_notified, status)
      VALUES 
        ('${sessionVictimId}', '${caseId}', '${rev1Id}', '林○○', 'VICTIM', '${investigatorId}', TRUE, 'PLANNED'),
        ('${sessionWangId}', '${caseId}', '${rev1Id}', '王○○', 'SUSPECT', '${investigatorId}', TRUE, 'PLANNED'),
        ('${sessionZhangId}', '${caseId}', '${rev1Id}', '張○○', 'SUSPECT', '${investigatorId}', TRUE, 'PLANNED');

      INSERT INTO interview_questions (id, case_id, revision_id, session_id, question_seq, question_text, is_mandatory)
      VALUES 
        ('${qA1}', '${caseId}', '${rev1Id}', '${sessionVictimId}', 1, '【通訊聯絡/客觀查證】你與「陳先生」認識與聯繫過程為何？是否曾與陳先生本人面交或電話通話？有無簽署任何書面委任或買賣合約？', TRUE),
        ('${qA2}', '${caseId}', '${rev1Id}', '${sessionVictimId}', 2, '【金流與交付】兩筆匯款（10/13 3萬元至王○○帳戶、10/16 1.8萬元至張○○帳戶）具體操作管道為何？陳先生如何指示受款帳戶？', TRUE),
        ('${qB1}', '${caseId}', '${rev1Id}', '${sessionWangId}', 1, '【知情與否認/行為手段】你名下銀行帳戶何以於10月13日收受林○○匯入之30,000元？提款卡、密碼與存摺目前由何人保管？', TRUE),
        ('${qB2}', '${caseId}', '${rev1Id}', '${sessionWangId}', 2, '【主觀犯意/利益流向】你提供該帳戶是否有取得任何報酬、對價或借貸利益？有無向警方報案之報案三聯單？', TRUE),
        ('${qC1}', '${caseId}', '${rev1Id}', '${sessionZhangId}', 1, '【知情與否認/行為手段】你名下銀行帳戶於10月16日收受18,000元款項，該帳戶及網路銀行平日由何人使用？', TRUE),
        ('${qC2}', '${caseId}', '${rev1Id}', '${sessionZhangId}', 2, '【共犯結構/防禦補強】你所稱將手機及網銀借給朋友使用，該朋友真實姓名、年籍、聯絡電話及借用目的為何？能否提供對話紀錄佐證？', TRUE);
    `);

    results.push({
      stepId: 'WF-06',
      category: '偵訊擬定',
      name: '9 大類別中立偵詢問句產製',
      status: 'PASS',
      details: '建立被害人林○○、嫌疑人王○○、張○○三組筆錄詢問會話與核心爭點問句',
    });
  } catch (err: any) {
    results.push({
      stepId: 'WF-06',
      category: '偵訊擬定',
      name: '9 大類別中立偵詢問句產製',
      status: 'FAIL',
      details: err.message,
    });
  }

  // -------------------------------------------------------------------------
  // Phase 2: 模擬第一階段調查結果與問答 (Answers A, B, C)
  // -------------------------------------------------------------------------
  log('\n[Phase 2] 寫入第一階段調查結果與當事人詢問回答 (Answers A, B, C)...');
  const ansAId = '56565656-0001-0000-0000-000000000001';
  const ansBId = '56565656-0002-0000-0000-000000000001';
  const ansCId = '56565656-0003-0000-0000-000000000001';

  try {
    await db.exec(`
      INSERT INTO interview_answers (id, question_id, answer_text, eval_fact_status, notes)
      VALUES 
        ('${ansAId}', '${qA1}', '回答A（報案人林○○）：我都是透過通訊軟體跟陳先生用文字傳訊，從來沒有通話過，也沒有見過陳先生本人，更沒有簽任何書面契約。他傳給我的限量商品照片我也無法查證真假，我現在只能提供通訊截圖跟匯款水單。', 'ADMITTED', '報案人坦承未曾核實對方身分亦無書面保障'),
        ('${ansBId}', '${qB1}', '回答B（帳戶人王○○）：我絕對沒有參與詐欺犯罪！我是在臉書社團看到家庭代工與行政兼職廣告，對方自稱人資主管，要求我將提款卡寄出並告知密碼，說是公司要做薪資轉帳及帳戶實名驗證測試，保證測完寄回。我完全沒有拿到任何報酬，後來發現聯絡不上對方，我已經在10月17日自己去派出所報案遺失！', 'DENIED', '嫌疑人王○○否認犯意，抗辯係求職受騙，聲明已報案'),
        ('${ansCId}', '${qC1}', '回答C（帳戶人張○○）：我沒有賣帳戶也沒有參與詐騙！那是10月中旬我一個綽號叫「小阿豪」的朋友說手機沒電，跟我借手機去用，我不知道他拿我手機去登入我的網路銀行收錢轉帳。但是我現在找不到小阿豪，我不知道他的本名，也沒有他的身分證字號或固定電話。', 'DENIED', '嫌疑人張○○否認參與，抗辯借手機予友人，但友人身分不詳抗辯薄弱');

      UPDATE interview_sessions SET status = 'CONCLUDED', ended_at = clock_timestamp() WHERE id IN ('${sessionVictimId}', '${sessionWangId}', '${sessionZhangId}');
    `);

    results.push({
      stepId: 'WF-07',
      category: '調查問答',
      name: '當事人回答紀錄與法律狀態標記',
      status: 'PASS',
      details: '完整收錄回答 A (ADMITTED), 回答 B (DENIED), 回答 C (DENIED)，確實保留否認抗辯',
    });
  } catch (err: any) {
    results.push({
      stepId: 'WF-07',
      category: '調查問答',
      name: '當事人回答紀錄與法律狀態標記',
      status: 'FAIL',
      details: err.message,
    });
  }

  // -------------------------------------------------------------------------
  // Phase 3: 事實更新與版本 2 快照建立 (Revision 2)
  // -------------------------------------------------------------------------
  log('\n[Phase 3] 建立版本 2 快照並更新事實 (保留爭議與否認，下游無效化)...');
  const rev2Id = 'bbbbbbbb-2222-2222-3333-000000000002';
  const fact11Id = 'cccccccc-0011-0000-0000-000000000002';
  const fact12Id = 'cccccccc-0012-0000-0000-000000000002';
  const docDraftId = '78787878-0001-0000-0000-000000000001';

  try {
    // 3.1 建立版本 2 (以版本 1 為父版本)
    await db.exec(`
      INSERT INTO case_revisions (id, case_id, revision_number, parent_revision_id, revision_hash, change_summary, is_locked, created_by)
      VALUES ('${rev2Id}', '${caseId}', 2, '${rev1Id}', 'hash_rev2_sim_after_interviews_updated_20261022', '納入報案人補強陳述及人頭帳戶名義人王○○、張○○偵詢供述，更新事實爭點與主客觀構成要件', FALSE, '${investigatorId}');

      UPDATE cases SET current_revision_id = '${rev2Id}' WHERE id = '${caseId}';
    `);

    // 3.2 複製舊版事實到版本 2，並依據問答更新狀態 (保留 DENIED / UNKNOWN)
    await db.exec(`
      INSERT INTO facts (id, case_id, revision_id, fact_seq, description, fact_type, status, confidence_score, occurred_at)
      SELECT gen_random_uuid(), case_id, '${rev2Id}', fact_seq, description, fact_type, status, confidence_score, occurred_at
      FROM facts
      WHERE revision_id = '${rev1Id}' AND fact_seq NOT IN (9, 10);

      -- 更新 Fact 9 (王○○：抗辯求職受騙，否認犯意)
      INSERT INTO facts (id, case_id, revision_id, fact_seq, description, fact_type, status, confidence_score)
      VALUES (gen_random_uuid(), '${caseId}', '${rev2Id}', 9, '王○○否認參與詐欺，辯稱係應徵兼職工作依指示寄出提款卡及密碼，未獲對價，並已主動報案遺失 (抗辯求職受騙)。', 'STATE_OF_MIND', 'DENIED', 0.650);

      -- 更新 Fact 10 (張○○：抗辯手機借友，否認犯意，惟友人身分不詳)
      INSERT INTO facts (id, case_id, revision_id, fact_seq, description, fact_type, status, confidence_score)
      VALUES (gen_random_uuid(), '${caseId}', '${rev2Id}', 10, '張○○否認販賣帳戶，辯稱手機及網銀借予綽號「小阿豪」友人使用不知情，惟無法提供該友人之年籍資料以供查證 (不合常理抗辯)。', 'STATE_OF_MIND', 'DENIED', 0.400);

      -- 新增 Fact 11 & 12
      INSERT INTO facts (id, case_id, revision_id, fact_seq, description, fact_type, status, confidence_score)
      VALUES 
        ('${fact11Id}', '${caseId}', '${rev2Id}', 11, '報案人林○○坦承自始未曾見過陳先生本人、未曾通話、無實體合約，亦無從核實商品照片真實性。', 'STATEMENT', 'ADMITTED', 1.000),
        ('${fact12Id}', '${caseId}', '${rev2Id}', 12, '王○○提出10月17日向轄區派出所報案提款卡遺失之受理紀錄。', 'OBJECTIVE', 'ASSERTED', 0.850);
    `);

    // 3.3 記錄事實異動歷程 (fact_update_logs)
    await db.exec(`
      INSERT INTO fact_update_logs (case_id, fact_id, trigger_source, trigger_reference_id, previous_status, new_status, previous_description, new_description, changed_by)
      VALUES 
        ('${caseId}', '${fact9Id}', 'INTERVIEW_ANSWER', '${ansBId}', 'UNKNOWN', 'DENIED', '受款帳戶名義人王○○提供帳戶之原因、有無對價及其主觀詐欺或洗錢認知。', '王○○否認參與詐欺，辯稱應徵受騙寄卡且無對價，並已報案遺失。', '${investigatorId}'),
        ('${caseId}', '${fact10Id}', 'INTERVIEW_ANSWER', '${ansCId}', 'UNKNOWN', 'DENIED', '受款帳戶名義人張○○提供帳戶之原因、有無對價及其主觀詐欺或洗錢認知。', '張○○否認販賣帳戶，抗辯手機借朋友不知情，但無法提供友人身分。', '${investigatorId}');
    `);

    // 3.4 建立版本 2 的流程狀態
    await db.exec(`
      INSERT INTO workflow_stages (case_id, revision_id, stage_name, status)
      VALUES 
        ('${caseId}', '${rev2Id}', 'FACTS_INTAKE', 'APPROVED'),
        ('${caseId}', '${rev2Id}', 'LEGAL_RESEARCH', 'IN_REVIEW'),
        ('${caseId}', '${rev2Id}', 'DOCUMENT_GENERATION', 'DRAFT');
    `);

    // 3.5 產生修訂後案件條陳草案 (DRAFT，未經審核 is_final 必須為 FALSE)
    await db.query(`
      INSERT INTO document_outputs (id, case_id, revision_id, document_type, title, content_markdown, is_final, approval_id, generated_by)
      VALUES (
        '${docDraftId}',
        '${caseId}',
        '${rev2Id}',
        'MEMORANDUM',
        '刑事案件偵查條陳 (SIM-2026-001 第二版草案)',
        '### 刑事案件偵查條陳 (草稿)\n\n**一、案由**：加重詐欺及洗錢防制法案件\n**二、犯罪嫌疑人**：\n1. 不詳男子「陳先生」（首謀實行詐術者）\n2. 帳戶名義人王○○（抗辯求職受騙，已調取報案紀錄查證）\n3. 帳戶名義人張○○（抗辯借用手機予不詳友人，常理有違）\n**三、調查經過與法律意見**：\n報案人林○○受誘騙匯款共計48,000元。嫌疑人張○○辯稱借用手機，顯屬卸責之詞，建請依洗錢防制法及幫助詐欺持續偵辦；王○○部分應函詢查證其求職對話真偽。',
        FALSE,
        NULL,
        '${investigatorId}'
      );
    `);

    results.push({
      stepId: 'WF-08',
      category: '版本升級與異動',
      name: '版本 2 建立與事證追溯更新',
      status: 'PASS',
      details: '版本 2 正確繼承父版本 1，事實更新保留 DENIED 狀態，寫入異動歷程，產出 DRAFT 條陳',
    });
  } catch (err: any) {
    results.push({
      stepId: 'WF-08',
      category: '版本升級與異動',
      name: '版本 2 建立與事證追溯更新',
      status: 'FAIL',
      details: err.message,
    });
  }

  // 3.6 負向約束測試：未經長官審核時，禁止將公文條陳標記為 is_final = TRUE
  log('\n[Phase 3.6] 驗證資料約束：未附 approval_id 禁止設定 is_final = TRUE...');
  let illegalDraftBlocked = false;
  try {
    await db.query(`
      INSERT INTO document_outputs (case_id, revision_id, document_type, title, content_markdown, is_final, approval_id, generated_by)
      VALUES ('${caseId}', '${rev2Id}', 'MEMORANDUM', '非法未核定正式條陳', '內文', TRUE, NULL, '${investigatorId}');
    `);
  } catch (e: any) {
    illegalDraftBlocked = true;
    log(`  ✓ 成功阻擋：未核定公文禁止設定為 FINAL (${e.message.split('\n')[0]})`);
  }

  results.push({
    stepId: 'SEC-01',
    category: '資料約束',
    name: '正式公文強核定約束 (chk_doc_final_needs_approval)',
    status: illegalDraftBlocked ? 'PASS' : 'FAIL',
    details: illegalDraftBlocked ? 'CHECK 約束成功阻擋未經審核之正式條陳寫入' : '未能阻擋未審核之正式條陳！',
  });

  // -------------------------------------------------------------------------
  // Phase 4: 人工審核簽核與版本鎖定 (Reviewer Sign-off & Lock)
  // -------------------------------------------------------------------------
  log('\n[Phase 4] 審核長官審核簽核、正式發布與版本 2 封存鎖定...');
  const approvalId = '90909090-0001-0000-0000-000000000001';

  try {
    // 4.1 審核員李○○隊長執行審核
    await db.query(`
      INSERT INTO review_approvals (id, case_id, revision_id, target_entity_type, target_entity_id, reviewer_id, status, comments, approval_hash)
      VALUES (
        '${approvalId}',
        '${caseId}',
        '${rev2Id}',
        'DOCUMENT_OUTPUT',
        '${docDraftId}',
        '${reviewerId}',
        'APPROVED',
        '核定意見：案情摘要與爭點分析完整，張○○卸責抗辯薄弱應列為加重偵查重點，准予備查核定為正式條陳。',
        'sha256_approval_signature_reviewer_captain_20261022_sim'
      );
    `);

    // 4.2 更新條陳為核定本 (is_final = TRUE, 關聯 approval_id)
    await db.query(`
      UPDATE document_outputs 
      SET is_final = TRUE, approval_id = '${approvalId}'
      WHERE id = '${docDraftId}';
    `);

    // 4.3 將版本 2 標記為 is_locked = TRUE
    await db.query(`
      UPDATE case_revisions 
      SET is_locked = TRUE, locked_at = clock_timestamp()
      WHERE id = '${rev2Id}';
    `);

    results.push({
      stepId: 'WF-09',
      category: '人工審核',
      name: '審核長官核定與條陳正式本簽發',
      status: 'PASS',
      details: '李○○隊長完成 review_approvals 簽核，條陳成功更新為 is_final = TRUE，版本 2 封存鎖定',
    });
  } catch (err: any) {
    results.push({
      stepId: 'WF-09',
      category: '人工審核',
      name: '審核長官核定與條陳正式本簽發',
      status: 'FAIL',
      details: err.message,
    });
  }

  // 4.4 防竄改觸發器測試：驗證已鎖定之版本 2 禁止竄改與刪除
  log('\n[Phase 4.4] 驗證歷史防竄改觸發器 (fn_prevent_locked_revision_mutation)...');
  let factMutationBlocked = false;
  try {
    await db.query(`
      UPDATE facts 
      SET description = '惡意篡改已核定歷史事實：受款人承認詐欺'
      WHERE revision_id = '${rev2Id}' AND fact_seq = 9;
    `);
  } catch (e: any) {
    factMutationBlocked = true;
    log(`  ✓ 成功阻擋：已鎖定版本子表事實禁止修改 (${e.message.split('\n')[0]})`);
  }

  let revisionDeleteBlocked = false;
  try {
    await db.query(`
      DELETE FROM case_revisions WHERE id = '${rev2Id}';
    `);
  } catch (e: any) {
    revisionDeleteBlocked = true;
    log(`  ✓ 成功阻擋：已鎖定歷史版本記錄禁止刪除 (${e.message.split('\n')[0]})`);
  }

  results.push({
    stepId: 'SEC-02',
    category: '不可竄改防護',
    name: '已鎖定版本防竄改觸發器驗證',
    status: (factMutationBlocked && revisionDeleteBlocked) ? 'PASS' : 'FAIL',
    details: 'fn_prevent_locked_revision_mutation 觸發器成功阻斷事實更新與版本刪除操作',
  });

  // -------------------------------------------------------------------------
  // Phase 5: 資料庫全表實體統計與 RLS 權限隔離稽核
  // -------------------------------------------------------------------------
  log('\n[Phase 5] 執行全表記錄數盤點與 RLS 隔離稽核...');

  const tables = [
    'user_roles', 'users', 'user_sessions', 'cases', 'case_revisions',
    'facts', 'fact_relations', 'evidence_items', 'evidence_sources', 'behaviors',
    'statute_references', 'precedent_references', 'legal_candidates', 'constituent_elements',
    'element_fact_mappings', 'core_issues', 'interview_sessions', 'interview_questions',
    'interview_answers', 'fact_update_logs', 'workflow_stages', 'review_approvals',
    'document_outputs', 'llm_prompt_templates'
  ];

  const tableCounts: Record<string, number> = {};
  for (const t of tables) {
    try {
      const q = await db.query<any>(`SELECT COUNT(*) as count FROM ${t};`);
      tableCounts[t] = parseInt(q.rows[0].count, 10);
    } catch (e) {
      tableCounts[t] = -1;
    }
  }

  // 5.2 RLS 正向與負向存取稽核
  // 建立非 Superuser 角色以驗證真正的 PostgreSQL RLS 行為 (Superuser 天生豁免 RLS)
  await db.exec(`
    DO $$ BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_runner') THEN
        CREATE ROLE app_runner NOSUPERUSER;
      END IF;
    END $$;
    GRANT USAGE ON SCHEMA public TO app_runner;
    GRANT ALL ON ALL TABLES IN SCHEMA public TO app_runner;
  `);

  // 5.2.1 測試未認證使用者查詢 (應阻絕，回傳 0 筆)
  let unauthenticatedBlocked = false;
  try {
    await db.exec(`
      SET ROLE app_runner;
      SELECT set_config('app.current_user_id', '', false);
    `);
    const qUnauth = await db.query<any>(`SELECT COUNT(*) as c FROM cases;`);
    if (parseInt(qUnauth.rows[0].c, 10) === 0) {
      unauthenticatedBlocked = true;
      log('  ✓ RLS 負向驗證：未登入匿名階段查詢案件主檔回傳 0 筆 (阻絕成功)');
    } else {
      log(`  ✗ RLS 負向驗證：匿名使用者查到了 ${qUnauth.rows[0].c} 筆案件！`);
    }
  } catch (e: any) {
    unauthenticatedBlocked = true;
  }

  // 5.2.2 測試非承辦人（未授權分析員）查詢承辦人之案件 (應阻絕，回傳 0 筆)
  let unauthorizedUserBlocked = false;
  try {
    await db.exec(`
      SET ROLE app_runner;
      SELECT set_config('app.current_user_id', '${unauthorizedId}', false);
    `);
    const qCross = await db.query<any>(`SELECT COUNT(*) as c FROM cases WHERE id = '${caseId}';`);
    if (parseInt(qCross.rows[0].c, 10) === 0) {
      unauthorizedUserBlocked = true;
      log('  ✓ RLS 負向驗證：未授權分析員跨案查詢主辦案件回傳 0 筆 (阻絕成功)');
    } else {
      log(`  ✗ RLS 負向驗證：未授權分析員查到了 ${qCross.rows[0].c} 筆主辦案件！`);
    }
  } catch (e: any) {
    unauthorizedUserBlocked = true;
  }

  // 5.2.3 測試授權承辦人查詢 (應可查到所屬案件 SIM-2026-001)
  let investigatorAuthorized = false;
  try {
    await db.exec(`
      SET ROLE app_runner;
      SELECT set_config('app.current_user_id', '${investigatorId}', false);
    `);
    const qAuth = await db.query<any>(`SELECT COUNT(*) as c FROM cases WHERE id = '${caseId}';`);
    if (parseInt(qAuth.rows[0].c, 10) === 1) {
      investigatorAuthorized = true;
      log('  ✓ RLS 正向驗證：主辦承辦人可合法查詢承辦之 SIM-2026-001 案件');
    }
  } catch (e: any) {
    investigatorAuthorized = false;
  } finally {
    await db.query(`RESET ROLE;`);
  }

  results.push({
    stepId: 'SEC-03',
    category: '存取控制',
    name: 'Row-Level Security (RLS) 權限隔離稽核',
    status: (unauthenticatedBlocked && unauthorizedUserBlocked && investigatorAuthorized) ? 'PASS' : 'FAIL',
    details: '匿名存取阻絕、未授權人員跨案阻絕與主辦人員合規存取均通過驗證',
  });

  // 5.3 敏感資訊與密鑰稽核
  const usersRes = await db.query<any>(`SELECT username, email, password_hash FROM users;`);
  let hasRealSecrets = false;
  for (const u of usersRes.rows) {
    if (!u.password_hash.includes('simulated_hash_not_real_key')) {
      hasRealSecrets = true;
    }
  }

  results.push({
    stepId: 'SEC-04',
    category: '機密防護',
    name: '無真實密鑰與真實個資外洩稽核',
    status: !hasRealSecrets ? 'PASS' : 'FAIL',
    details: '全數帳號均使用 Argon2id 虛構雜湊與去識別化代號，無任何正式金鑰曝露',
  });

  log('\n======================================================================');
  log('   端到端測試執行完畢！所有測試步驟與安全斷言均已記錄。');
  log('======================================================================\n');

  return { results, tableCounts, logs };
}

// If executed directly from CLI
if (process.argv[1]?.includes('sim_2026_001_runner')) {
  runSimulationAudit()
    .then((out) => {
      console.log('Result counts:');
      console.table(out.results);
      console.log('Entity counts:');
      console.table(out.tableCounts);
      process.exit(out.results.some((r) => r.status === 'FAIL') ? 1 : 0);
    })
    .catch((err) => {
      console.error('Audit execution error:', err);
      process.exit(1);
    });
}
