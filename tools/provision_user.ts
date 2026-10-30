import fs from 'node:fs';

const provisioningUrl = process.env.JUDICIAL3_PROVISIONING_DATABASE_URL || process.env.MIGRATION_DATABASE_URL;
if (provisioningUrl) {
  process.env.DATABASE_URL = provisioningUrl;
  process.env.JUDICIAL3_DATABASE_ENGINE = 'postgres';
}

import { provisionUser } from '../src/server/auth.js';

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
  const id = await provisionUser({ username, email, fullName, roleCode, password });
  console.log(`USER_PROVISIONED id=${id} role=${roleCode.toUpperCase()}`);
} catch (error: any) {
  console.error(`USER_PROVISION_FAILED ${error?.message || 'unknown error'}`);
  process.exit(1);
}


