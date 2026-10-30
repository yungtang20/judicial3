import assert from 'node:assert/strict';
import { Pool } from 'pg';

const admin = new Pool({ connectionString: process.env.DATABASE_URL });
const provisioner = new Pool({ connectionString: process.env.JUDICIAL3_TEST_PROVISIONING_DATABASE_URL });
const app = new Pool({ connectionString: process.env.JUDICIAL3_TEST_APP_DATABASE_URL });

try {
  const version = await admin.query<{ version: string }>('SELECT version FROM schema_migrations ORDER BY version');
  assert.ok(version.rows.length >= 14, 'all migrations must be recorded');
  const roles = await admin.query<{ rolname: string; rolsuper: boolean; rolbypassrls: boolean }>(
    "SELECT rolname, rolsuper, rolbypassrls FROM pg_roles WHERE rolname IN ('judicial3_app','judicial3_provisioner') ORDER BY rolname",
  );
  assert.equal(roles.rows.length, 2, 'app and provisioner roles must be pre-created');
  assert.ok(roles.rows.every((row) => !row.rolsuper && !row.rolbypassrls), 'roles must not bypass RLS');

  const current = await provisioner.query<{ current_user: string }>('SELECT current_user::text AS current_user');
  assert.equal(current.rows[0].current_user, 'judicial3_provisioner');
  const provisionerRole = await provisioner.query<{ id: string; role_code: string }>(
    'SELECT id, role_code FROM user_roles ORDER BY role_code',
  );
  assert.equal(provisionerRole.rows.length, 3);
  const username = `pg_acceptance_${Date.now()}`;
  const roleId = provisionerRole.rows[0].id;
  const created = await provisioner.query<{ id: string }>(
    `INSERT INTO users(username,email,password_hash,full_name,role_id)
     VALUES ($1,$2,$3,$4,$5::uuid) RETURNING id`,
    [username, `${username}@example.invalid`, '$2b$12$placeholderhashplaceholderhashplaceholderhash', 'PG acceptance', roleId],
  );
  assert.ok(created.rows[0]?.id);
  await assert.rejects(() => provisioner.query('UPDATE users SET full_name=$1 WHERE id=$2::uuid', ['blocked', created.rows[0].id]));
  await assert.rejects(() => provisioner.query('DELETE FROM users WHERE id=$1::uuid', [created.rows[0].id]));
  await assert.rejects(() => provisioner.query('SELECT id FROM cases LIMIT 1'));
  await assert.rejects(() => provisioner.query('SELECT id FROM user_sessions LIMIT 1'));
  await assert.rejects(() => app.query(`INSERT INTO users(username,email,password_hash,full_name,role_id)
    VALUES ($1,$2,$3,$4,$5::uuid)`, [username + '_app', `${username}_app@example.invalid`, 'blocked', 'blocked', roleId]));
  await admin.query('DELETE FROM users WHERE id=$1::uuid', [created.rows[0].id]);
  console.log('POSTGRES_ACCEPTANCE_PASS: migrations, role attributes, provisioning grants, app/provisioner denial checks');
  console.log('PASS=1 FAIL=0 NOT_RUN=0 BLOCKED=0 EXIT_CODE=0 FINAL_STATUS=PASS');
} finally {
  await Promise.all([admin.end(), provisioner.end(), app.end()]);
}
