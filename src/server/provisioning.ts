import type { SqlClient } from './databaseRuntime.js';

export const PROVISIONING_DATABASE_ENV = 'JUDICIAL3_PROVISIONING_DATABASE_URL';
export const PROVISIONING_ROLE = 'judicial3_provisioner';

export async function assertProvisioningRole(db: SqlClient): Promise<void> {
  const result = await db.query<{ current_user: string }>('SELECT current_user::text AS current_user');
  const currentUser = result.rows[0]?.current_user;
  if (currentUser !== PROVISIONING_ROLE) {
    throw new Error('provisioning connection role rejected');
  }
}
