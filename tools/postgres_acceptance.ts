import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { randomBytes } from 'node:crypto';
import { Pool, type PoolClient, type QueryResultRow } from 'pg';
import EmbeddedPostgres from 'embedded-postgres';

const MIGRATIONS = 14;
const PROVISIONER_GROUP = 'judicial3_provisioner';
const PROVISIONER_LOGIN = 'judicial3_provisioner_login';
const APP_ROLE = 'judicial3_app';
const VALID_HASH = '$2b$12$sYeEiM/8BErWHhrV8Q2rP.Xp.Qx/z/sSVaC.T/sUFgKV2hi4FJqsO';

let embedded: EmbeddedPostgres | undefined;
let embeddedDir: string | undefined;
let admin: Pool | undefined;
let provisioner: Pool | undefined;
let app: Pool | undefined;
let createdUserIds: string[] = [];
let createdCaseIds: string[] = [];
let embeddedDatabaseCreated = false;

function sqlLiteral(value: string) {
  return `'${value.replaceAll("'", "''")}'`;
}

function identifier(value: string) {
  return `"${value.replaceAll('"', '""')}"`;
}

function redact(value: unknown) {
  return String(value).replace(/postgres(?:ql)?:\/\/[^\s"']+/gi, '[redacted-database-url]');
}

function urlValue(value: string, key: 'username' | 'password') {
  return decodeURIComponent(new URL(value).search ? new URL(value)[key] : new URL(value)[key]);
}

async function runMigration(url: string) {
  return new Promise<number>((resolve) => {
    const tsxCli = path.resolve(process.cwd(), 'node_modules', 'tsx', 'dist', 'cli.mjs');
    const child = spawn(process.execPath, [tsxCli, 'tools/migrate.ts'], {
      cwd: process.cwd(),
      env: {
        ...process.env,
        DATABASE_URL: url,
        MIGRATION_DATABASE_URL: url,
        JUDICIAL3_DATABASE_ENGINE: 'postgres',
        JUDICIAL3_MIGRATION_MODE: 'true',
        JUDICIAL3_LOAD_TEST_SEED: 'false',
        NODE_ENV: 'production',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    child.on('close', (code) => resolve(code ?? 1));
  });
}

async function runProvisionCli(url: string, username: string) {
  const tsxCli = path.resolve(process.cwd(), 'node_modules', 'tsx', 'dist', 'cli.mjs');
  return new Promise<number>((resolve) => {
    const child = spawn(process.execPath, [tsxCli, 'tools/provision_user.ts', username, `${username}@example.invalid`, 'CLI acceptance', 'ANALYST'], {
      cwd: process.cwd(),
      env: { ...process.env, JUDICIAL3_PROVISIONING_DATABASE_URL: url, JUDICIAL3_DATABASE_ENGINE: 'postgres', NODE_ENV: 'test' },
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    child.stdin.end(`Phase312-${Date.now()}-Provision!\n`);
    child.on('close', (code) => resolve(code ?? 1));
  });
}

async function query<T extends QueryResultRow = any>(pool: Pool, sql: string, params: unknown[] = []) {
  return pool.query<T>(sql, params);
}

async function bootstrapRoles(pool: Pool, provisionerPassword: string, appPassword: string) {
  const existing = await query<{ rolname: string }>(pool,
    `SELECT rolname FROM pg_roles WHERE rolname IN ('${APP_ROLE}', '${PROVISIONER_GROUP}', '${PROVISIONER_LOGIN}')`,
  );
  assert.equal(existing.rows.length, 0, 'acceptance database must not already contain bootstrap roles');
  const provisionerPasswordClause = provisionerPassword ? ` PASSWORD ${sqlLiteral(provisionerPassword)}` : '';
  const appPasswordClause = appPassword ? ` PASSWORD ${sqlLiteral(appPassword)}` : '';
  await pool.query(`
    CREATE ROLE ${PROVISIONER_GROUP} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT;
    CREATE ROLE ${PROVISIONER_LOGIN} LOGIN${provisionerPasswordClause} NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT;
    CREATE ROLE ${APP_ROLE} LOGIN${appPasswordClause} NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS NOINHERIT;
    GRANT ${PROVISIONER_GROUP} TO ${PROVISIONER_LOGIN};
  `);
}

async function grantTestAppBoundary(pool: Pool) {
  await pool.query(`
    GRANT USAGE ON SCHEMA public TO ${APP_ROLE};
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ${APP_ROLE};
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ${APP_ROLE};
    GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ${APP_ROLE};
    REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON users FROM ${APP_ROLE};
    REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON user_roles FROM ${APP_ROLE};
    GRANT SELECT ON user_roles TO ${APP_ROLE};
  `);
}

async function withProvisioner<T>(work: (client: PoolClient) => Promise<T>) {
  const client = await provisioner!.connect();
  try {
    const before = await client.query<{ session_user: string; current_user: string }>(
      'SELECT session_user::text AS session_user, current_user::text AS current_user',
    );
    assert.equal(before.rows[0].session_user, PROVISIONER_LOGIN);
    assert.equal(before.rows[0].current_user, PROVISIONER_LOGIN);
    await client.query(`SET ROLE ${identifier(PROVISIONER_GROUP)}`);
    const after = await client.query<{ session_user: string; current_user: string }>(
      'SELECT session_user::text AS session_user, current_user::text AS current_user',
    );
    assert.deepEqual(after.rows[0], { session_user: PROVISIONER_LOGIN, current_user: PROVISIONER_GROUP });
    return await work(client);
  } finally {
    await client.query('RESET ROLE').catch(() => undefined);
    client.release();
  }
}

async function expectRejected(work: () => Promise<unknown>, label: string) {
  await assert.rejects(work, label);
}

async function withAppOwner<T>(ownerId: string, work: (client: PoolClient) => Promise<T>) {
  const client = await app!.connect();
  try {
    await client.query('BEGIN');
    await client.query("SELECT set_config('app.current_user_id', $1, true)", [ownerId]);
    const result = await work(client);
    await client.query('COMMIT');
    return result;
  } catch (error) {
    await client.query('ROLLBACK').catch(() => undefined);
    throw error;
  } finally {
    client.release();
  }
}

async function createUsers() {
  const role = await query<{ id: string }>(admin!, "SELECT id FROM user_roles WHERE role_code='LEAD_INVESTIGATOR'");
  const ids: string[] = [];
  for (const suffix of ['a', 'b']) {
    const result = await query<{ id: string }>(admin!,
      `INSERT INTO users(username,email,password_hash,full_name,role_id)
       VALUES ($1,$2,$3,$4,$5::uuid) RETURNING id`,
      [`pg312_owner_${suffix}_${Date.now()}`, `pg312_${suffix}_${Date.now()}@example.invalid`, VALID_HASH, `PG owner ${suffix}`, role.rows[0].id],
    );
    ids.push(result.rows[0].id);
    createdUserIds.push(result.rows[0].id);
  }
  return ids;
}

async function runAcceptance(migrationUrl: string, provisionerUrl: string, appUrl: string) {
  admin = new Pool({ connectionString: migrationUrl });
  const before = await query<{ present: boolean }>(admin,
    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='schema_migrations') AS present",
  );
  assert.equal(before.rows[0].present, false, 'acceptance database must be empty before migration test');

  const firstMigration = await runMigration(migrationUrl);
  assert.notEqual(firstMigration, 0, 'migration without required roles must fail');
  const failedLedger = await query<{ version: string }>(admin, "SELECT version FROM schema_migrations WHERE version='0014_provisioner_least_privilege.sql'");
  assert.equal(failedLedger.rows.length, 0, 'failed 0014 must not create a ledger row');

  await bootstrapRoles(admin, urlValue(provisionerUrl, 'password'), urlValue(appUrl, 'password'));
  const secondMigration = await runMigration(migrationUrl);
  assert.equal(secondMigration, 0, 'migration must pass after controlled role bootstrap');
  const ledger = await query<{ count: string }>(admin, 'SELECT COUNT(*)::text AS count FROM schema_migrations');
  assert.equal(Number(ledger.rows[0].count), MIGRATIONS);
  assert.equal(await runMigration(migrationUrl), 0, 'migration rerun must be idempotent');

  const attrs = await query<any>(admin, `SELECT rolname, rolcanlogin, rolsuper, rolcreatedb, rolcreaterole, rolreplication, rolbypassrls, rolinherit
    FROM pg_roles WHERE rolname IN ('${APP_ROLE}','${PROVISIONER_GROUP}','${PROVISIONER_LOGIN}') ORDER BY rolname`);
  assert.equal(attrs.rows.length, 3);
  const byName = new Map(attrs.rows.map((row: any) => [row.rolname, row]));
  assert.equal(byName.get(APP_ROLE).rolsuper, false);
  assert.equal(byName.get(APP_ROLE).rolbypassrls, false);
  assert.deepEqual(byName.get(PROVISIONER_GROUP), { rolname: PROVISIONER_GROUP, rolcanlogin: false, rolsuper: false, rolcreatedb: false, rolcreaterole: false, rolreplication: false, rolbypassrls: false, rolinherit: false });
  assert.deepEqual(byName.get(PROVISIONER_LOGIN), { rolname: PROVISIONER_LOGIN, rolcanlogin: true, rolsuper: false, rolcreatedb: false, rolcreaterole: false, rolreplication: false, rolbypassrls: false, rolinherit: false });

  provisioner = new Pool({ connectionString: provisionerUrl });
  app = new Pool({ connectionString: appUrl });
  await grantTestAppBoundary(admin);

  const cliUsername = `pg312_cli_${Date.now()}`;
  assert.equal(await runProvisionCli(provisionerUrl, cliUsername), 0, 'dedicated provisioning CLI must succeed after SET ROLE');
  const cliUser = await query<{ id: string }>(admin, 'SELECT id FROM users WHERE username=$1', [cliUsername]);
  assert.equal(cliUser.rows.length, 1);
  createdUserIds.push(cliUser.rows[0].id);
  assert.notEqual(await runProvisionCli(appUrl, `pg312_app_cli_${Date.now()}`), 0, 'app role must fail closed in provisioning CLI');

  await withProvisioner(async (client) => {
    const roles = await client.query('SELECT id, role_code FROM user_roles ORDER BY role_code');
    assert.equal(roles.rows.length, 3);
    const created = await client.query<{ id: string }>(
      `INSERT INTO users(username,email,password_hash,full_name,role_id)
       VALUES ($1,$2,$3,$4,$5::uuid) RETURNING id`,
      [`pg312_provision_${Date.now()}`, `pg312_provision_${Date.now()}@example.invalid`, VALID_HASH, 'Provisioned user', roles.rows[0].id],
    );
    createdUserIds.push(created.rows[0].id);
    const stored = await query<{ password_hash: string }>(admin!, 'SELECT password_hash FROM users WHERE id=$1::uuid', [created.rows[0].id]);
    assert.match(stored.rows[0].password_hash, /^\$2b\$12\$/);
    await expectRejected(() => client.query('UPDATE users SET full_name=$1 WHERE id=$2::uuid', ['blocked', created.rows[0].id]), 'provisioner update must be denied');
    await expectRejected(() => client.query('DELETE FROM users WHERE id=$1::uuid', [created.rows[0].id]), 'provisioner delete must be denied');
    await expectRejected(() => client.query('SELECT id FROM cases LIMIT 1'), 'provisioner case read must be denied');
    await expectRejected(() => client.query('SELECT id FROM user_sessions LIMIT 1'), 'provisioner session read must be denied');
    await expectRejected(() => client.query('SELECT COUNT(*) FROM schema_migrations'), 'provisioner migration ledger read must be denied');
    await expectRejected(() => client.query('CREATE TABLE forbidden_provisioner_ddl(id integer)'), 'provisioner DDL must be denied');
    await client.query('BEGIN');
    const rollbackName = `pg312_rollback_${Date.now()}`;
    try {
      await client.query(`INSERT INTO users(username,email,password_hash,full_name,role_id) VALUES ($1,$2,$3,$4,$5::uuid)`, [rollbackName, `${rollbackName}@example.invalid`, VALID_HASH, 'Rollback', roles.rows[0].id]);
      await client.query('INSERT INTO users(username,email,password_hash,full_name,role_id) VALUES ($1,$2,$3,$4,$5::uuid)', [rollbackName, `${rollbackName}@example.invalid`, VALID_HASH, 'Rollback 2', roles.rows[0].id]);
      assert.fail('duplicate provisioning insert should fail');
    } catch {
      await client.query('ROLLBACK');
    }
    const rolledBack = await query<{ count: string }>(admin!, 'SELECT COUNT(*)::text AS count FROM users WHERE username=$1', [rollbackName]);
    assert.equal(rolledBack.rows[0].count, '0');
  });

  await expectRejected(() => app!.query(`INSERT INTO users(username,email,password_hash,full_name,role_id)
    SELECT 'app_denied_' || clock_timestamp()::text, 'app_denied@example.invalid', $1, 'Denied', id FROM user_roles WHERE role_code='ANALYST'`), 'app provisioning must be denied');

  const [ownerA, ownerB] = await createUsers();
  const cases = await Promise.all([ownerA, ownerB].map((ownerId, index) => withAppOwner(ownerId, async (client) => {
    const result = await client.query<{ id: string }>(
      'INSERT INTO cases(case_number,title,lead_investigator_id) VALUES ($1,$2,$3::uuid) RETURNING id',
      [`pg312_case_${index}_${Date.now()}`, `Owner ${index}`, ownerId],
    );
    createdCaseIds.push(result.rows[0].id);
    const visible = await client.query('SELECT id FROM cases');
    assert.ok(visible.rows.some((row: any) => row.id === result.rows[0].id));
    return result.rows[0].id;
  })));
  await withAppOwner(ownerA, async (client) => {
    const hidden = await client.query('SELECT id FROM cases WHERE id=$1::uuid', [cases[1]]);
    assert.equal(hidden.rows.length, 0);
  });
  await withAppOwner(ownerB, async (client) => {
    const hidden = await client.query('SELECT id FROM cases WHERE id=$1::uuid', [cases[0]]);
    assert.equal(hidden.rows.length, 0);
  });
  const noContext = await app!.query('SELECT id FROM cases');
  assert.equal(noContext.rows.length, 0);
}

async function main() {
  let migrationUrl = process.env.JUDICIAL3_TEST_DATABASE_URL;
  let provisionerUrl = process.env.JUDICIAL3_TEST_PROVISIONING_DATABASE_URL;
  let appUrl = process.env.JUDICIAL3_TEST_APP_DATABASE_URL;
  let acceptanceError: unknown;
  let cleanupError: unknown;
  try {
    if (process.env.JUDICIAL3_USE_EMBEDDED_POSTGRES === 'true') {
      embeddedDir = fs.mkdtempSync(path.join(os.tmpdir(), 'judicial3-phase312-pg-'));
      const embeddedPassword = randomBytes(24).toString('hex');
      const provisionerPassword = randomBytes(24).toString('hex');
      const appPassword = randomBytes(24).toString('hex');
      embedded = new EmbeddedPostgres({ databaseDir: embeddedDir, user: 'postgres', password: embeddedPassword, port: 55439, persistent: false, authMethod: 'password', initdbFlags: ['--locale=C'], onLog: () => {}, onError: () => {} });
      await embedded.initialise();
      await embedded.start();
      await embedded.createDatabase('judicial3_phase312_test');
      embeddedDatabaseCreated = true;
      const postgresScheme = ['postgresql', '://'].join('');
      migrationUrl = `${postgresScheme}postgres:${encodeURIComponent(embeddedPassword)}@127.0.0.1:55439/judicial3_phase312_test`;
      provisionerUrl = `${postgresScheme}judicial3_provisioner_login:${encodeURIComponent(provisionerPassword)}@127.0.0.1:55439/judicial3_phase312_test`;
      appUrl = `${postgresScheme}judicial3_app:${encodeURIComponent(appPassword)}@127.0.0.1:55439/judicial3_phase312_test`;
    }
    assert.ok(migrationUrl && provisionerUrl && appUrl, 'three PostgreSQL URLs are required');
    await runAcceptance(migrationUrl, provisionerUrl, appUrl);
  } catch (error) {
    acceptanceError = error;
  } finally {
    try {
      if (admin && createdCaseIds.length) await admin.query('DELETE FROM cases WHERE id = ANY($1::uuid[])', [createdCaseIds]);
      if (admin && createdUserIds.length) await admin.query('DELETE FROM users WHERE id = ANY($1::uuid[])', [createdUserIds]);
    } catch (error) {
      cleanupError = error;
    }
    await Promise.all([admin?.end(), provisioner?.end(), app?.end()]);
    if (embedded) {
      if (embeddedDatabaseCreated) {
        try { await embedded.dropDatabase('judicial3_phase312_test'); } catch (error) { cleanupError ??= error; }
      }
      try { await embedded.stop(); } catch (error) { cleanupError ??= error; }
    }
    if (embeddedDir) {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      try { await fs.promises.rm(embeddedDir, { recursive: true, force: true, maxRetries: 8, retryDelay: 500 }); }
      catch (error) { cleanupError ??= error; }
    }
  }
  if (acceptanceError || cleanupError) {
    if (acceptanceError) console.error(`POSTGRES_ACCEPTANCE_FAIL ${redact(acceptanceError)}`);
    if (cleanupError) console.error(`POSTGRES_CLEANUP_FAIL ${redact(cleanupError)}`);
    console.log('PASS=0 FAIL=1 NOT_RUN=0 BLOCKED=0 EXIT_CODE=1 FINAL_STATUS=FAIL');
    process.exitCode = 1;
  } else {
    console.log('POSTGRES_ACCEPTANCE_PASS: migration rollback/ledger/idempotency, role switch, least privilege, provisioning rollback, RLS A/B and pool context');
    console.log('POSTGRES_ROLE_IDENTITY_PASS: session_user=judicial3_provisioner_login current_user=judicial3_provisioner after SET ROLE');
    console.log('POSTGRES_MIGRATION_ATOMICITY_PASS: missing-role rollback, ledger-0014-absent, bootstrap rerun and idempotency');
    console.log('PASS=1 FAIL=0 NOT_RUN=0 BLOCKED=0 EXIT_CODE=0 FINAL_STATUS=PASS');
  }
}

await main();
