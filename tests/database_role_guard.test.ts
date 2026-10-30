import assert from 'node:assert/strict';
import test from 'node:test';
import { assertApplicationRole, assertMigrationRole, type SqlClient } from '../src/server/databaseRuntime.js';

function client(rows: unknown[]): SqlClient {
  return {
    query: async <T = any>() => ({ rows: rows as T[] }),
    exec: async () => undefined,
    close: async () => undefined,
  };
}

test('production application role accepts only judicial3_app', async () => {
  await assertApplicationRole(client([{ session_user: 'judicial3_app', current_user: 'judicial3_app' }]));
  await assert.rejects(
    assertApplicationRole(client([{ session_user: 'owner', current_user: 'judicial3_app' }])),
    /application database role rejected/,
  );
});

test('migration role is exact and has no cluster-wide privileges', async () => {
  const prior = process.env.JUDICIAL3_EXPECTED_DATABASE_ROLE;
  process.env.JUDICIAL3_EXPECTED_DATABASE_ROLE = 'judicial3_migrator';
  try {
    const base = {
      session_user: 'judicial3_migrator', current_user: 'judicial3_migrator', rolsuper: false,
      rolcreatedb: false, rolcreaterole: false, rolreplication: false, rolbypassrls: false,
    };
    await assertMigrationRole(client([base]));
    await assert.rejects(assertMigrationRole(client([{ ...base, rolbypassrls: true }])), /forbidden cluster privileges/);
    await assert.rejects(assertMigrationRole(client([{ ...base, current_user: 'owner' }])), /migration database role rejected/);
  } finally {
    if (prior === undefined) delete process.env.JUDICIAL3_EXPECTED_DATABASE_ROLE;
    else process.env.JUDICIAL3_EXPECTED_DATABASE_ROLE = prior;
  }
});
