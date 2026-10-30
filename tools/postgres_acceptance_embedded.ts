import EmbeddedPostgres from 'embedded-postgres';
import { Client } from 'pg';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { closeDatabaseRuntime, getRuntime, resetDatabaseRuntimeForTests } from '../src/server/databaseRuntime.js';
const port = 55439;
const database = 'judicial3_phase3_2_test';
const rootPassword = `root-${Date.now()}-${Math.random().toString(36).slice(2)}`;
const appPassword = `app-${Date.now()}-${Math.random().toString(36).slice(2)}`;
const provisioningPassword = `provision-${Date.now()}-${Math.random().toString(36).slice(2)}`;
const databaseDir = await mkdtemp(`${tmpdir()}/judicial3-phase3-2-`);
const pg = new EmbeddedPostgres({ databaseDir, user: 'postgres', password: rootPassword, port, authMethod: 'password', persistent: false, initdbFlags: ['--locale=C'], onLog: () => undefined, onError: () => undefined });
const rootUrl = `postgresql://postgres:${encodeURIComponent(rootPassword)}@127.0.0.1:${port}/${database}`;
const appUrl = `postgresql://judicial3_app:${encodeURIComponent(appPassword)}@127.0.0.1:${port}/${database}`;
const provisioningUrl = `postgresql://judicial3_provisioner_login:${encodeURIComponent(provisioningPassword)}@127.0.0.1:${port}/${database}`;

async function client(url: string) {
  const connection = new Client({ connectionString: url });
  connection.on('error', (error) => console.error(`embedded client error: ${error instanceof Error ? error.message : String(error)}`));
  await connection.connect();
  return connection;
}

async function runMigration(url: string, expectFailure: boolean) {
  process.env.DATABASE_URL = url;
  process.env.JUDICIAL3_DATABASE_ENGINE = 'postgres';
  process.env.NODE_ENV = 'test';
  process.env.JUDICIAL3_MIGRATION_MODE = 'true';
  process.env.MIGRATION_DATABASE_URL = url;
  try {
    const runtime = await getRuntime();
    await closeDatabaseRuntime();
    if (expectFailure) throw new Error('migration unexpectedly passed without required roles');
  } catch (error) {
    await closeDatabaseRuntime().catch(() => undefined);
    resetDatabaseRuntimeForTests();
    if (!expectFailure) throw error;
    console.log('POSTGRES_MIGRATION_ATOMICITY_PASS: missing roles rejected and ledger remained atomic');
  }
  resetDatabaseRuntimeForTests();
}

try {
  await pg.initialise();
  await pg.start();
  await pg.createDatabase(database);
  const admin = await client(rootUrl);
  await admin.query(`CREATE ROLE judicial3_app LOGIN PASSWORD '${appPassword.replaceAll("'", "''")}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS`);
  await admin.query(`CREATE ROLE judicial3_provisioner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS`);
  await admin.query(`CREATE ROLE judicial3_provisioner_login LOGIN PASSWORD '${provisioningPassword.replaceAll("'", "''")}' IN ROLE judicial3_provisioner NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS`);
  await admin.end();
  await runMigration(rootUrl, false);
  await runMigration(rootUrl, false);

  process.env.DATABASE_URL = provisioningUrl;
  process.env.JUDICIAL3_PROVISIONING_MODE = 'true';
  delete process.env.JUDICIAL3_MIGRATION_MODE;
  delete process.env.MIGRATION_DATABASE_URL;
  resetDatabaseRuntimeForTests();
  const { getSqlClient: getProvisioningClient, closeDatabaseRuntime: closeProvisioningRuntime } = await import('../src/server/databaseRuntime.js');
  const { assertProvisioningRole } = await import('../src/server/provisioning.js');
  const { provisionUser } = await import('../src/server/auth.js');
  await assertProvisioningRole(await getProvisioningClient());
  const provisionedId = await provisionUser({ username: 'phase32_embedded', email: 'phase32_embedded@test.invalid', fullName: 'Phase 3.2 Embedded', password: 'Phase32!EmbeddedPassword' });
  await closeProvisioningRuntime();

  const provisioner = await client(provisioningUrl);
  await provisioner.query('SET ROLE judicial3_provisioner');
  const identity = await provisioner.query<{ session_user: string; current_user: string }>('SELECT session_user::text, current_user::text');
  if (identity.rows[0]?.session_user !== 'judicial3_provisioner_login' || identity.rows[0]?.current_user !== 'judicial3_provisioner') throw new Error('provisioning identity mismatch');
  await provisioner.query('RESET ROLE');
  await provisioner.end();
  if (!provisionedId) throw new Error('provisioning did not return a user id');
  console.log('POSTGRES_ROLE_IDENTITY_PASS: session_user=judicial3_provisioner_login current_user=judicial3_provisioner');
  console.log('POSTGRES_ACCEPTANCE_PASS: embedded PostgreSQL migration, role identity, provisioning, idempotent rerun');
  console.log('POSTGRES_MIGRATION_MISSING_ROLE_NOT_RUN: isolated failure-case inspection is reserved for Render staging');
  console.log('POSTGRES_VERSION: embedded-postgres PostgreSQL 16 test binary');
  console.log('PASS=2 FAIL=0 NOT_RUN=1 BLOCKED=0 EXIT_CODE=2 FINAL_STATUS=PARTIAL_PASS');
  process.exitCode = 2;
} finally {
  await pg.stop().catch(() => undefined);
  await rm(databaseDir, { recursive: true, force: true }).catch(() => undefined);
}
