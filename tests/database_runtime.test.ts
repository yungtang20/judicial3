import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const tempDb = fs.mkdtempSync(path.join(os.tmpdir(), 'judicial3-runtime-'));
process.env.JUDICIAL3_DATABASE_PATH = tempDb;
process.env.JUDICIAL3_LOAD_TEST_SEED = 'true';
process.env.NODE_ENV = 'test';

const runtime = await import('../src/server/databaseRuntime');
const service = await import('../src/server/databaseService');

const ownerId = '22222222-2222-2222-2222-222222222201';
const migrationCount = fs.readdirSync(path.join(process.cwd(), 'database', 'migrations')).filter((name) => /^\d{4}_.+\.sql$/.test(name)).length;

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function basePayload(caseNumber: string) {
  return {
    ownerId,
    caseNumber,
    title: '資料層測試案件',
    rawText: '虛構測試案情，用於驗證交易、持久化與 migration ledger。',
    facts: [{ seq: 1, description: '虛構事實', status: 'UNKNOWN' as const }],
    evidence: [],
    candidates: [{ chargeName: '中華民國刑法 §339 I 詐欺取財', status: 'UNRESOLVED' as const, rationale: '待查', statuteRef: '中華民國刑法 §339 I' }],
    questions: [{ seq: 1, questionText: '請說明經過。', answerText: '' }],
    summary: '虛構摘要',
  };
}

try {
  const db = await runtime.getSqlClient();
  const ledger = await db.query<any>('SELECT version, checksum FROM schema_migrations ORDER BY version');
  assert(ledger.rows.length === migrationCount, `expected ${migrationCount} applied migrations, got ${ledger.rows.length}`);
  assert(ledger.rows.every((row: any) => /^[0-9a-f]{64}$/.test(row.checksum.trim())), 'every migration must have a checksum');
  const integrity = await db.query<any>('SELECT * FROM verify_schema_integrity()');
  assert(Array.isArray(integrity.rows) && integrity.rows.length > 0, 'schema integrity function must return results');

  const caseNumber = `runtime-${Date.now()}`;
  const saved = await service.saveCaseAnalysis(basePayload(caseNumber));
  assert(saved.revisionNumber === 1, 'first save must create revision 1');
  const beforeClose = await service.getCaseDetails(saved.caseId, ownerId);
  assert(beforeClose?.questions[0].question_text === '請說明經過。', 'question must be stored');

  // Restart: close the runtime and reopen the same on-disk database.
  await runtime.closeDatabaseRuntime();
  runtime.resetDatabaseRuntimeForTests();
  const reopened = await runtime.getSqlClient();
  const afterRestart = await service.getCaseDetails(saved.caseId, ownerId);
  assert(afterRestart?.case.title === '資料層測試案件', 'case must survive a runtime restart');
  assert(afterRestart?.currentRevision.revision_number === 1, 'revision must survive a runtime restart');
  const ledgerAfter = await reopened.query<any>('SELECT COUNT(*)::text AS count FROM schema_migrations');
  assert(Number(ledgerAfter.rows[0].count) === migrationCount, 'restart must not duplicate migration rows');

  // Transaction rollback: an invalid candidate aborts the whole save.
  const countsBefore = await reopened.query<any>(`SELECT
    (SELECT COUNT(*)::text FROM cases) AS cases,
    (SELECT COUNT(*)::text FROM case_revisions) AS revisions`);
  let rolledBack = false;
  try {
    await service.saveCaseAnalysis({
      ...basePayload(`rollback-${Date.now()}`),
      candidates: [{ chargeName: '無效法條', status: 'UNRESOLVED', rationale: '缺少 statuteRef' } as any],
    });
  } catch { rolledBack = true; }
  assert(rolledBack, 'invalid statute reference must abort the save');
  const countsAfter = await reopened.query<any>(`SELECT
    (SELECT COUNT(*)::text FROM cases) AS cases,
    (SELECT COUNT(*)::text FROM case_revisions) AS revisions`);
  assert(countsAfter.rows[0].cases === countsBefore.rows[0].cases, 'failed save must not create a partial case');
  assert(countsAfter.rows[0].revisions === countsBefore.rows[0].revisions, 'failed save must not create a partial revision');

  // Re-running migrations against an up-to-date database is a no-op.
  await runtime.closeDatabaseRuntime();
  runtime.resetDatabaseRuntimeForTests();
  await runtime.getRuntime();
  const ledgerRerun = await (await runtime.getSqlClient()).query<any>('SELECT COUNT(*)::text AS count FROM schema_migrations');
  assert(Number(ledgerRerun.rows[0].count) === migrationCount, 're-running migrations must not duplicate ledger rows');

  // A modified migration file (checksum drift) must stop startup.
  await (await runtime.getSqlClient()).query("UPDATE schema_migrations SET checksum=repeat('0',64) WHERE version='0001_extensions_enums.sql'");
  await runtime.closeDatabaseRuntime();
  runtime.resetDatabaseRuntimeForTests();
  let checksumRejected = '';
  try { await runtime.getRuntime(); } catch (error) { checksumRejected = error instanceof Error ? error.message : String(error); }
  assert(checksumRejected.includes('checksum mismatch'), `checksum drift must reject startup, got: ${checksumRejected}`);

  console.log(`DATABASE_RUNTIME_PASS: ${migrationCount} migrations, ledger checksums, restart persistence, rollback, checksum drift`);
} finally {
  await runtime.closeDatabaseRuntime().catch(() => undefined);
  fs.rmSync(tempDb, { recursive: true, force: true });
}


