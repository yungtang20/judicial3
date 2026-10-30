import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const tempDb = fs.mkdtempSync(path.join(os.tmpdir(), 'judicial3-rls-'));
process.env.JUDICIAL3_DATABASE_PATH = tempDb;
process.env.JUDICIAL3_LOAD_TEST_SEED = 'true';
process.env.NODE_ENV = 'test';

const runtime = await import('../src/server/databaseRuntime');
const service = await import('../src/server/databaseService');

const ownerA = '22222222-2222-2222-2222-222222222201';
const ownerB = '22222222-2222-2222-2222-222222222202';
const roleName = 'judicial3_app_test';

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function payload(ownerId: string, caseNumber: string) {
  return {
    ownerId,
    caseNumber,
    title: `RLS case ${caseNumber}`,
    rawText: '虛構 RLS 測試案情。',
    facts: [{ seq: 1, description: '虛構事實', status: 'UNKNOWN' as const }],
    evidence: [],
    candidates: [],
    questions: [{ seq: 1, questionText: '問題', answerText: '' }],
    summary: '虛構摘要',
  };
}

try {
  const savedA = await service.saveCaseAnalysis(payload(ownerA, `rls-a-${Date.now()}`));
  const savedB = await service.saveCaseAnalysis(payload(ownerB, `rls-b-${Date.now()}`));
  const db = await runtime.getSqlClient();

  const force = await db.query<any>(`SELECT relrowsecurity, relforcerowsecurity FROM pg_class WHERE relname='cases'`);
  assert(force.rows[0].relrowsecurity === true && force.rows[0].relforcerowsecurity === true, 'cases must have ENABLE and FORCE row level security');

  await db.query(`DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='${roleName}') THEN
      CREATE ROLE ${roleName} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
  END $$`);
  await db.query(`GRANT USAGE ON SCHEMA public TO ${roleName}`);
  await db.query(`GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ${roleName}`);
  await db.query(`GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ${roleName}`);
  await db.query(`GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ${roleName}`);

  const role = await db.query<any>(`SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname='${roleName}'`);
  assert(role.rows[0].rolsuper === false && role.rows[0].rolbypassrls === false, 'application role must not be superuser or BYPASSRLS');

  const expectedOwned = await db.query<any>('SELECT COUNT(*)::text AS count FROM cases WHERE lead_investigator_id=$1::UUID', [ownerA]);
  const expectedOwnedCount = Number(expectedOwned.rows[0].count);

  await db.query('BEGIN');
  await db.query(`SET LOCAL ROLE ${roleName}`);
  await db.query(`SELECT set_config('app.current_user_id', $1, true)`, [ownerA]);

  const ownCases = await db.query<any>('SELECT id FROM cases');
  assert(ownCases.rows.length === expectedOwnedCount, `RLS must expose exactly the ${expectedOwnedCount} owner cases, got ${ownCases.rows.length}`);
  assert(ownCases.rows.some((row: any) => row.id === savedA.caseId), 'RLS must expose the authenticated owner case');
  assert(!ownCases.rows.some((row: any) => row.id === savedB.caseId), 'RLS must hide the other owner case');

  const otherFacts = await db.query<any>('SELECT id FROM facts WHERE case_id=$1::UUID', [savedB.caseId]);
  assert(otherFacts.rows.length === 0, 'direct SQL must not read another owner facts');

  const updateOther = await db.query<any>('UPDATE cases SET title=$1 WHERE id=$2::UUID', ['tampered', savedB.caseId]);
  assert(Number(updateOther.rowCount || 0) === 0, 'direct SQL must not update another owner case');

  let insertBlocked = false;
  await db.query('SAVEPOINT injected_fact');
  try {
    await db.query(`INSERT INTO facts (case_id, revision_id, fact_seq, description, status)
      VALUES ($1::UUID, $2::UUID, 99, 'injected', 'ASSERTED')`, [savedB.caseId, savedB.revisionId]);
  } catch {
    insertBlocked = true;
    await db.query('ROLLBACK TO SAVEPOINT injected_fact');
  }
  assert(insertBlocked, 'RLS must block inserting facts into another owner case');

  // Unverified statute placeholders are the only allowed shared-table insert.
  await db.query(`INSERT INTO statute_references(law_name, article_number, paragraph, content, effective_date, is_current)
    VALUES ('測試法', '999', 1, '[UNVERIFIED_SOURCE] 測試', DATE '1900-01-01', FALSE)`);
  let verifiedBlocked = false;
  await db.query('SAVEPOINT verified_statute');
  try {
    await db.query(`INSERT INTO statute_references(law_name, article_number, paragraph, content, effective_date, is_current)
      VALUES ('測試法', '998', 1, '偽造已查證條文', DATE '2026-01-01', TRUE)`);
  } catch {
    verifiedBlocked = true;
    await db.query('ROLLBACK TO SAVEPOINT verified_statute');
  }
  assert(verifiedBlocked, 'RLS must block writing verified statute content');

  await db.query('RESET ROLE');
  await db.query('COMMIT');

  // Transaction-local identity must not leak to the next unit of work.
  await db.query('BEGIN');
  await db.query(`SELECT set_config('app.current_user_id', $1, true)`, [ownerA]);
  await db.query('COMMIT');
  const residual = await db.query<any>("SELECT current_setting('app.current_user_id', true) AS uid");
  assert(!residual.rows[0].uid, 'transaction-local user context must be cleared after commit');

  // With no identity set, policies expose nothing even to the app role.
  await db.query('BEGIN');
  await db.query(`SET LOCAL ROLE ${roleName}`);
  const anonymous = await db.query<any>('SELECT id FROM cases');
  assert(anonymous.rows.length === 0, 'RLS must expose no cases without an identity');
  await db.query('RESET ROLE');
  await db.query('COMMIT');

  console.log('RLS_POLICY_PASS: FORCE RLS owner isolation, cross-owner write denial, no identity leakage, transaction-local context reset');
} finally {
  await runtime.closeDatabaseRuntime().catch(() => undefined);
  fs.rmSync(tempDb, { recursive: true, force: true });
}


