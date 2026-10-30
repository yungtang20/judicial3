import fs from 'node:fs';

function redactedError(error: unknown, secret: string) {
  const message = error instanceof Error ? error.message : 'unknown error';
  return message.split(secret).join('[redacted-database-url]').replace(/postgres(?:ql)?:\/\/[^\s"']+/gi, '[redacted-database-url]');
}

async function main() {
  const provisioningUrl = process.env.JUDICIAL3_PROVISIONING_DATABASE_URL;
  if (!provisioningUrl) {
    console.error('USER_PROVISION_FAILED JUDICIAL3_PROVISIONING_DATABASE_URL is required');
    return 2;
  }
  const [username, email, fullName, roleCode = 'LEAD_INVESTIGATOR'] = process.argv.slice(2);
  if (!username || !email || !fullName) {
    console.error('Usage: npm run user:provision -- <username> <email> <full-name> [role-code]');
    return 2;
  }
  if (process.stdin.isTTY) {
    console.error('Password must be supplied through controlled stdin; it is never accepted as a command argument.');
    return 2;
  }

  process.env.DATABASE_URL = provisioningUrl;
  process.env.JUDICIAL3_DATABASE_ENGINE = 'postgres';
  process.env.JUDICIAL3_PROVISIONING_MODE = 'true';
  let closeDatabaseRuntime: (() => Promise<void>) | undefined;
  try {
    const runtime = await import('../src/server/databaseRuntime.js');
    closeDatabaseRuntime = runtime.closeDatabaseRuntime;
    const { assertProvisioningRole } = await import('../src/server/provisioning.js');
    const { provisionUser } = await import('../src/server/auth.js');
    const password = fs.readFileSync(0, 'utf8').trimEnd();
    await assertProvisioningRole(await runtime.getSqlClient());
    const id = await provisionUser({ username, email, fullName, roleCode, password });
    console.log(`USER_PROVISIONED id=${id} role=${roleCode.toUpperCase()}`);
    return 0;
  } catch (error) {
    console.error(`USER_PROVISION_FAILED ${redactedError(error, provisioningUrl)}`);
    return 1;
  } finally {
    await closeDatabaseRuntime?.().catch(() => undefined);
  }
}

process.exitCode = await main();


