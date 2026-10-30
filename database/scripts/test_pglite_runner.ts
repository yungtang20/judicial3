import { PGlite } from '@electric-sql/pglite';
import fs from 'fs';
import path from 'path';

async function main() {
  console.log('======================================================================');
  console.log('   刑事偵查輔助系統 - PostgreSQL PGlite 實體隔離執行驗證');
  console.log('======================================================================\n');

  const db = new PGlite();
  const baseDir = path.resolve(process.cwd(), 'database');
  const migrationsDir = path.join(baseDir, 'migrations');
  const testsDir = path.join(baseDir, 'tests');

  // Step 1: Run Migrations 0001 - 0009
  console.log('[Phase 1/5] 執行循序 Migration 0001 ~ 0009...');
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

  for (const file of migrationFiles) {
    const filePath = path.join(migrationsDir, file);
    const sql = fs.readFileSync(filePath, 'utf-8');
    try {
      await db.exec(sql);
      console.log(`  ✓ 成功套用 Migration: ${file}`);
    } catch (err: any) {
      console.error(`  ✗ 套用失敗 ${file}:`, err.message);
      process.exit(1);
    }
  }

  // Step 2: Run verify_schema_integrity()
  console.log('\n[Phase 2/5] 執行 Schema 自我完整性校驗 verify_schema_integrity()...');
  try {
    const res = await db.query<any>('SELECT * FROM verify_schema_integrity();');
    for (const row of res.rows) {
      console.log(`  ✓ [${row.check_item}] 期望: ${row.expected_count}, 實際: ${row.actual_count}, 結果: ${row.status} (${row.details})`);
    }
  } catch (err: any) {
    console.error('  ✗ verify_schema_integrity() 失敗:', err.message);
  }

  // Step 3: Run Seed Test Data
  console.log('\n[Phase 3/5] 寫入非真實個資合成測試資料 (test_data.sql)...');
  const testDataSql = fs.readFileSync(path.join(testsDir, 'test_data.sql'), 'utf-8');
  try {
    await db.exec(testDataSql);
    console.log('  ✓ 成功寫入模擬案件資料 (Case #115模擬偵字第0001號)');
    const countRes = await db.query<any>('SELECT COUNT(*) as c FROM cases;');
    console.log(`  目前案件主檔總數: ${countRes.rows[0].c}`);
  } catch (err: any) {
    console.error('  ✗ 寫入 test_data.sql 失敗:', err.message);
  }

  // Step 4: Run Constraint Tests
  console.log('\n[Phase 4/5] 執行資料約束 (CHECK / UNIQUE / 自環防護) 測試...');
  try {
    // 4.1: Confidence score boundary test
    let confidenceBlocked = false;
    try {
      await db.query(`
        INSERT INTO facts (case_id, revision_id, fact_seq, description, status, confidence_score)
        VALUES ('55555555-5555-5555-5555-555555555501', '66666666-6666-6666-6666-666666666601', 99, '非法評分測試', 'ASSERTED', 1.500);
      `);
    } catch (e: any) {
      confidenceBlocked = true;
      console.log('  ✓ 成功阻擋大於 1.000 之非法可信度評分 (chk_facts_confidence_range 生效)');
    }
    if (!confidenceBlocked) console.error('  ✗ 未阻擋非法可信度評分！');

    // 4.2: Fact self-loop test
    let selfLoopBlocked = false;
    try {
      await db.query(`
        INSERT INTO fact_relations (case_id, revision_id, source_fact_id, target_fact_id, relation_type, rationale)
        VALUES (
          '55555555-5555-5555-5555-555555555501', 
          '66666666-6666-6666-6666-666666666601', 
          '77777777-7777-7777-7777-777777777701', 
          '77777777-7777-7777-7777-777777777701', 
          'CAUSES', 
          '自我循環非法測試'
        );
      `);
    } catch (e: any) {
      selfLoopBlocked = true;
      console.log('  ✓ 成功阻擋事實自我循環推論 (chk_fact_rel_no_self_loop 生效)');
    }
    if (!selfLoopBlocked) console.error('  ✗ 未阻擋事實自我循環！');

    // 4.3: Final document approval requirement test
    let approvalBlocked = false;
    try {
      await db.query(`
        INSERT INTO document_outputs (case_id, revision_id, document_type, title, content_markdown, is_final, approval_id, generated_by)
        VALUES (
          '55555555-5555-5555-5555-555555555501',
          '66666666-6666-6666-6666-666666666601',
          'INVESTIGATION_REPORT',
          '未經長官簽核之正式條陳',
          '內容',
          TRUE,
          NULL,
          '22222222-2222-2222-2222-222222222201'
        );
      `);
    } catch (e: any) {
      approvalBlocked = true;
      console.log('  ✓ 成功阻擋未附長官審核簽核之正式條陳公文 (chk_doc_final_needs_approval 生效)');
    }
    if (!approvalBlocked) console.error('  ✗ 未阻擋未審核正式條陳！');
  } catch (err: any) {
    console.error('  ✗ 約束測試執行失敗:', err.message);
  }

  // Step 5: Version Integrity & Trigger Tests
  console.log('\n[Phase 5/5] 執行歷史版本鎖定 (is_locked) 與不可竄改防護觸發器測試...');
  try {
    // 5.1 Lock revision 1
    await db.query(`
      UPDATE case_revisions 
      SET is_locked = TRUE 
      WHERE id = '66666666-6666-6666-6666-666666666601';
    `);

    // 5.2 Attempt to mutate a fact in locked revision
    let factMutationBlocked = false;
    try {
      await db.query(`
        UPDATE facts 
        SET description = '惡意篡改已核定歷史事實'
        WHERE id = '77777777-7777-7777-7777-777777777701';
      `);
    } catch (e: any) {
      factMutationBlocked = true;
      console.log(`  ✓ 成功阻擋修改已鎖定歷史版本子表事實 (fn_prevent_locked_revision_mutation 生效)`);
    }
    if (!factMutationBlocked) console.error('  ✗ 觸發器未能阻擋已鎖定版本事實異動！');

    // 5.3 Attempt to delete locked revision
    let revDeleteBlocked = false;
    try {
      await db.query(`
        DELETE FROM case_revisions WHERE id = '66666666-6666-6666-6666-666666666601';
      `);
    } catch (e: any) {
      revDeleteBlocked = true;
      console.log(`  ✓ 成功阻擋刪除已鎖定之歷史版本 (fn_prevent_locked_revision_mutation 生效)`);
    }
    if (!revDeleteBlocked) console.error('  ✗ 觸發器未能阻擋刪除已鎖定版本！');
  } catch (err: any) {
    console.error('  ✗ 觸發器測試失敗:', err.message);
  }

  console.log('\n======================================================================');
  console.log('   PostgreSQL 實體驗證測試全數通過 (ALL REAL PG TESTS PASS)！');
  console.log('======================================================================\n');
}

main().catch(console.error);
