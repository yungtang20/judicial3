import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const tempDb = fs.mkdtempSync(path.join(os.tmpdir(), 'judicial3-role-seed-'));
process.env.JUDICIAL3_DATABASE_PATH = tempDb;
process.env.JUDICIAL3_LOAD_TEST_SEED = 'false';
process.env.NODE_ENV = 'test';

const runtime = await import('../src/server/databaseRuntime');

try {
  const db = await runtime.getSqlClient();
  const roles = await db.query<{ role_code: string }>('SELECT role_code FROM user_roles ORDER BY role_code');
  assert.deepEqual(roles.rows.map((row) => row.role_code), ['ANALYST', 'LEAD_INVESTIGATOR', 'REVIEWER']);
  const users = await db.query<{ count: string }>('SELECT COUNT(*)::text AS count FROM users');
  assert.equal(users.rows[0].count, '0');

  const roleMigration = fs.readFileSync(path.join(process.cwd(), 'database', 'migrations', '0013_system_roles.sql'), 'utf8');
  const { stripOuterTransaction } = runtime;
  await db.exec(stripOuterTransaction(roleMigration));
  const unchanged = await db.query<{ role_name: string; count: string }>(
    "SELECT role_name, COUNT(*) OVER ()::text AS count FROM user_roles WHERE role_code='REVIEWER'",
  );
  assert.equal(unchanged.rows[0]?.role_name, '審核長官');
  assert.equal(unchanged.rows[0]?.count, '1');
  console.log('ROLE_SEED_ISOLATION_PASS: clean database, no users, idempotent role seed');
} finally {
  await runtime.closeDatabaseRuntime().catch(() => undefined);
  fs.rmSync(tempDb, { recursive: true, force: true });
}
