import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const tempDb = fs.mkdtempSync(path.join(os.tmpdir(), 'judicial3-critical-fixes-'));
process.env.JUDICIAL3_DATABASE_PATH = tempDb;
process.env.JUDICIAL3_LOAD_TEST_SEED = 'true';
process.env.NODE_ENV = 'test';

const runtime = await import('../src/server/databaseRuntime');
const service = await import('../src/server/databaseService');
const auth = await import('../src/server/auth');

const ownerA = '22222222-2222-2222-2222-222222222201';
const ownerB = '22222222-2222-2222-2222-222222222202';

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function payload(ownerId: string, caseNumber: string) {
  return {
    ownerId,
    caseNumber,
    title: '關鍵修復測試案件',
    rawText: '虛構測試資料。',
    facts: [{ seq: 1, description: '虛構事實', status: 'UNKNOWN' as const }],
    evidence: [],
    candidates: [],
    questions: [{ seq: 1, questionText: '請說明經過。', answerText: '' }],
    summary: '虛構摘要',
  };
}

try {
  const db = await runtime.getSqlClient();
  const roles = await db.query<{ role_code: string }>('SELECT role_code FROM user_roles ORDER BY role_code');
  assert(roles.rows.map((row) => row.role_code).join(',') === 'ANALYST,LEAD_INVESTIGATOR,REVIEWER', 'production roles must be seeded without test users');

  const username = `critical_${Date.now()}`;
  const userId = await auth.provisionUser({
    username,
    email: `${username}@example.invalid`,
    fullName: '測試使用者',
    roleCode: 'ANALYST',
    password: 'CriticalFixes!Password2026',
  });
  const created = await db.query<any>('SELECT u.id, u.password_hash, r.role_code FROM users u JOIN user_roles r ON r.id=u.role_id WHERE u.id=$1::UUID', [userId]);
  assert(created.rows[0]?.role_code === 'ANALYST', 'provisioning must resolve the requested system role');
  assert(created.rows[0].password_hash !== 'CriticalFixes!Password2026', 'password must never be stored in plaintext');

  const first = await service.getDatabaseHealth(ownerA);
  assert(first.caseCount === 1 && first.revisionCount === 1, 'health must count only owner A data');
  await service.saveCaseAnalysis(payload(ownerB, `critical-health-${Date.now()}`));
  const second = await service.getDatabaseHealth(ownerB);
  assert(second.caseCount === 1 && second.revisionCount === 1, 'health must count only owner B data');
  let rejectedWithoutOwner = false;
  try { await service.getDatabaseHealth(); } catch (error: any) { rejectedWithoutOwner = error?.code === 'OWNER_CONTEXT_REQUIRED'; }
  assert(rejectedWithoutOwner, 'health must reject missing owner context');

  console.log('CRITICAL_FIXES_PASS: role seed, controlled provisioning, owner-scoped health');
} finally {
  await runtime.closeDatabaseRuntime().catch(() => undefined);
  fs.rmSync(tempDb, { recursive: true, force: true });
}
