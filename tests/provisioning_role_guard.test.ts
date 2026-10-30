import assert from 'node:assert/strict';
import { assertProvisioningRole, PROVISIONING_ROLE } from '../src/server/provisioning.js';

const queries: string[] = [];
const goodDb = {
  async query<T>(sql: string) {
    queries.push(sql);
    return { rows: [{ session_user: 'judicial3_provisioner_login', current_user: PROVISIONING_ROLE }] as T[] };
  },
  async exec() { return undefined; },
  async close() { return undefined; },
};
await assertProvisioningRole(goodDb);
assert.match(queries[0], /current_user/);

await assert.rejects(
  () => assertProvisioningRole({ ...goodDb, query: async <T>() => ({ rows: [{ session_user: 'judicial3_app', current_user: 'judicial3_app' }] as T[] }) }),
  /provisioning connection role rejected/,
);
console.log('PROVISIONING_ROLE_GUARD_PASS: current_user is checked fail-closed');
