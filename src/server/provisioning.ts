import type { SqlClient } from './databaseRuntime.js';

export const PROVISIONING_DATABASE_ENV = 'JUDICIAL3_PROVISIONING_DATABASE_URL';
export const PROVISIONING_ROLE = 'judicial3_provisioner';
export const PROVISIONING_LOGIN_ROLE = 'judicial3_provisioner_login';

export async function assertProvisioningRole(db: SqlClient): Promise<void> {
  const result = await db.query<{ session_user: string; current_user: string }>(
    'SELECT session_user::text AS session_user, current_user::text AS current_user',
  );
  const identity = result.rows[0];
  if (identity?.session_user !== PROVISIONING_LOGIN_ROLE || identity.current_user !== PROVISIONING_ROLE) {
    throw new Error('provisioning connection role rejected');
  }
}
