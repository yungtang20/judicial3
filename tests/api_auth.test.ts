import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createHmac } from 'node:crypto';

const tempDb = fs.mkdtempSync(path.join(os.tmpdir(), 'judicial3-auth-middleware-'));
process.env.JUDICIAL3_DATABASE_PATH = tempDb;
process.env.JUDICIAL3_LOAD_TEST_SEED = 'true';
process.env.NODE_ENV = 'test';
process.env.JUDICIAL3_SESSION_SECRET = 'middleware-test-secret';

const { requireApiUser, requireCsrf, sessionCookieName, login } = await import('../src/server/auth');
const { closeDatabaseRuntime } = await import('../src/server/databaseRuntime');

function tokenFor(userId: string) {
  const payload = Buffer.from(JSON.stringify({ sub: userId, exp: Math.floor(Date.now() / 1000) + 300 })).toString('base64url');
  return `${payload}.${createHmac('sha256', process.env.JUDICIAL3_SESSION_SECRET!).update(payload).digest('base64url')}`;
}

async function run(handler: any, req: any) {
  const outcome = { status: 200, body: undefined as unknown, nextCalled: false };
  const res = {
    status: (value: number) => { outcome.status = value; return res; },
    json: (value: unknown) => { outcome.body = value; return res; },
    end: () => res,
  } as any;
  await new Promise<void>((resolve) => {
    Promise.resolve(handler(req, res, () => { outcome.nextCalled = true; resolve(); })).catch(() => resolve());
    setTimeout(resolve, 2000);
  });
  return outcome;
}

const req = (headers: Record<string, string>, cookies: Record<string, string> = {}) => ({
  header: (name: string) => headers[name.toLowerCase()],
  cookies,
}) as any;

const unauth = await run(requireApiUser, req({ 'x-user-id': '22222222-2222-2222-2222-222222222201' }));
if (unauth.status !== 401 || unauth.nextCalled) throw new Error('missing credential or spoofed x-user-id was not rejected');
if (JSON.stringify(unauth.body) !== JSON.stringify({ error: 'authentication required' })) throw new Error('unauthenticated response leaked detail');

const malformed = await run(requireApiUser, req({ authorization: 'Bearer not-a-token' }));
if (malformed.status !== 401) throw new Error('malformed bearer token was not rejected');

const wrongSignature = await run(requireApiUser, req({ authorization: `Bearer ${tokenFor('22222222-2222-2222-2222-222222222201')}tampered` }));
if (wrongSignature.status !== 401) throw new Error('wrong token signature was not rejected');

const expiredPayload = Buffer.from(JSON.stringify({ sub: '22222222-2222-2222-2222-222222222201', exp: 1 })).toString('base64url');
const expired = await run(requireApiUser, req({ authorization: `Bearer ${expiredPayload}.${createHmac('sha256', process.env.JUDICIAL3_SESSION_SECRET!).update(expiredPayload).digest('base64url')}` }));
if (expired.status !== 401) throw new Error('expired bearer token was not rejected');

const legacy = await run(requireApiUser, req({ authorization: `Bearer ${tokenFor('22222222-2222-2222-2222-222222222201')}` }));
if (!legacy.nextCalled) throw new Error('development legacy token must still work for the local bridge');

const session = await login('lead_investigator_01', 'Judicial3!TestPass2026', { ip: '127.0.0.1', header: () => undefined } as any);
if (!session) throw new Error('test seed login failed');
const cookieReq = req({}, { [sessionCookieName()]: session!.token });
const cookieAuth = await run(requireApiUser, cookieReq);
if (!cookieAuth.nextCalled || cookieReq.userId !== session!.userId) throw new Error('valid cookie session was not accepted');

const csrfMissing = await run(requireCsrf, cookieReq);
if (csrfMissing.status !== 403) throw new Error('missing csrf token was not rejected for a cookie session');
const csrfWrong = await run(requireCsrf, { ...cookieReq, header: (name: string) => name === 'x-csrf-token' ? 'wrong-token' : undefined });
if (csrfWrong.status !== 403) throw new Error('wrong csrf token was not rejected');
const csrfOk = await run(requireCsrf, { ...cookieReq, header: (name: string) => name === 'x-csrf-token' ? session!.csrf : undefined });
if (!csrfOk.nextCalled) throw new Error('valid csrf token was rejected');

// Legacy bearer requests have no server-side session and therefore no CSRF
// token; they are development-only and production rejects them earlier.
process.env.NODE_ENV = 'production';
const productionLegacy = await run(requireApiUser, req({ authorization: `Bearer ${tokenFor('22222222-2222-2222-2222-222222222201')}` }));
if (productionLegacy.nextCalled || productionLegacy.status !== 401) throw new Error('legacy bearer token must be rejected in production');
process.env.NODE_ENV = 'test';

console.log('API_AUTH_PASS: middleware rejects missing, malformed, expired, tampered and production-legacy credentials; cookie session and CSRF enforced');
await closeDatabaseRuntime();
fs.rmSync(tempDb, { recursive: true, force: true });
