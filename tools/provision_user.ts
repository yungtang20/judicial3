import fs from 'node:fs';

const provisioningUrl = process.env.JUDICIAL3_PROVISIONING_DATABASE_URL;
if (!provisioningUrl) {
  console.error('USER_PROVISION_FAILED JUDICIAL3_PROVISIONING_DATABASE_URL is required');
  process.exit(2);
}

process.env.DATABASE_URL = provisioningUrl;
process.env.JUDICIAL3_DATABASE_ENGINE = 'postgres';
process.env.JUDICIAL3_PROVISIONING_MODE = 'true';

const { closeDatabaseRuntime, getSqlClient } = await import('../src/server/databaseRuntime.js');
const { assertProvisioningRole } = await import('../src/server/provisioning.js');
const { provisionUser } = await import('../src/server/auth.js');

const [username, email, fullName, roleCode = 'LEAD_INVESTIGATOR'] = process.argv.slice(2);
if (!username || !email || !fullName) {
  console.error('Usage: npm run user:provision -- <username> <email> <full-name> [role-code]');
  process.exit(2);
}
if (process.stdin.isTTY) {
  console.error('Password must be supplied through controlled stdin; it is never accepted as a command argument.');
  process.exit(2);
}
const password = fs.readFileSync(0, 'utf8').trimEnd();
try {
  await assertProvisioningRole(await getSqlClient());
  const id = await provisionUser({ username, email, fullName, roleCode, password });
  console.log(`USER_PROVISIONED id=${id} role=${roleCode.toUpperCase()}`);
} catch (error: any) {
  console.error(`USER_PROVISION_FAILED ${error?.message || 'unknown error'}`);
  process.exit(1);
} finally {
  await closeDatabaseRuntime().catch(() => undefined);
}


