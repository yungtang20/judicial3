import { requireApiUser } from '../src/server/auth';
import { createHmac } from 'crypto';

function tokenFor(userId: string) {
  const payload = Buffer.from(JSON.stringify({ sub: userId, exp: Math.floor(Date.now() / 1000) + 300 })).toString('base64url');
  return `${payload}.${createHmac('sha256', 'test-secret').update(payload).digest('base64url')}`;
}

function run(headers: Record<string, string>) {
  process.env.JUDICIAL3_SESSION_SECRET = 'test-secret';
  const req = { header: (name: string) => headers[name.toLowerCase()] } as any;
  let status = 200;
  let body: unknown;
  let nextCalled = false;
  const res = { status: (value: number) => { status = value; return res; }, json: (value: unknown) => { body = value; return res; } } as any;
  requireApiUser(req, res, () => { nextCalled = true; });
  return { status, body, nextCalled, userId: req.userId };
}

const unauthenticated = run({});
if (unauthenticated.status !== 401 || unauthenticated.nextCalled) throw new Error('unauthenticated request was not rejected');

const missingOwner = run({ authorization: `Bearer ${tokenFor('')}` });
if (missingOwner.status !== 401 || missingOwner.nextCalled) throw new Error('request without a token subject was not rejected');

const expiredPayload = Buffer.from(JSON.stringify({ sub: '11111111-1111-1111-1111-111111111101', exp: 1 })).toString('base64url');
const expiredToken = `${expiredPayload}.${createHmac('sha256', 'test-secret').update(expiredPayload).digest('base64url')}`;
const expired = run({ authorization: `Bearer ${expiredToken}` });
if (expired.status !== 401 || expired.nextCalled) throw new Error('expired token was not rejected');

const wrongSignature = run({ authorization: `Bearer ${tokenFor('11111111-1111-1111-1111-111111111101')}tampered` });
if (wrongSignature.status !== 401 || wrongSignature.nextCalled) throw new Error('wrong token signature was not rejected');

const malformed = run({ authorization: 'Bearer not-a-token' });
if (malformed.status !== 401 || malformed.nextCalled) throw new Error('malformed token was not rejected');

const authenticated = run({ authorization: `Bearer ${tokenFor('11111111-1111-1111-1111-111111111101')}`, 'x-user-id': 'attacker-supplied-id' });
if (!authenticated.nextCalled || authenticated.userId !== '11111111-1111-1111-1111-111111111101') throw new Error('authenticated owner was not passed to backend');

console.log('API_AUTH_PASS: backend middleware rejects missing, expired, malformed and wrong-signature tokens');
