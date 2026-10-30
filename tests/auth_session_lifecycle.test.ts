import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const tempDb = fs.mkdtempSync(path.join(os.tmpdir(), 'judicial3-auth-'));
process.env.JUDICIAL3_DATABASE_PATH = tempDb;
process.env.JUDICIAL3_LOAD_TEST_SEED = 'true';
process.env.NODE_ENV = 'test';
delete process.env.JUDICIAL3_SESSION_SECRET;

const auth = await import('../src/server/auth');
const { getSqlClient, closeDatabaseRuntime } = await import('../src/server/databaseRuntime');

const username = 'lead_investigator_01';
const password = 'Judicial3!TestPass2026';
const userId = '22222222-2222-2222-2222-222222222201';
const otherUserId = '22222222-2222-2222-2222-222222222202';

const request = { ip: '127.0.0.1', header: (name: string) => name === 'user-agent' ? 'judicial3-test' : undefined } as any;

function cookieRequest(token: string) {
  return { cookies: { [auth.sessionCookieName()]: token }, header: () => undefined } as any;
}

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

try {
  const unknown = await auth.login('nobody_here', password, request);
  assert(unknown === null, 'unknown username must not authenticate');
  const wrong = await auth.login(username, 'wrong-password-value', request);
  assert(wrong === null, 'wrong password must not authenticate');

  const session = await auth.login(username, password, request);
  assert(session, 'valid credentials must authenticate');
  assert(session!.userId === userId, 'session subject must match the database user');
  assert(session!.token.length >= 40, 'session token must be long and unpredictable');
  assert(session!.csrf.length >= 40 && session!.csrf !== session!.token, 'csrf token must be distinct');

  const db = await getSqlClient();
  const stored = await db.query<any>('SELECT session_token_hash, csrf_token_hash FROM user_sessions WHERE user_id=$1::UUID', [userId]);
  assert(stored.rows.length === 1, 'exactly one session row must be stored');
  assert(stored.rows[0].session_token_hash !== session!.token, 'raw session token must never be stored');
  assert(/^[0-9a-f]{64}$/.test(stored.rows[0].session_token_hash), 'session token must be stored as a sha256 hash');

  const resolved = await auth.authenticateRequest(cookieRequest(session!.token));
  assert(resolved?.userId === userId, 'valid cookie session must resolve to its user');
  assert(!!resolved?.csrfTokenHash && resolved.csrfTokenHash !== session!.csrf, 'csrf must be stored hashed');

  const missing = await auth.authenticateRequest({ cookies: {}, header: () => undefined } as any);
  assert(missing === null, 'missing credential must be rejected');
  const tampered = await auth.authenticateRequest(cookieRequest(`${session!.token.slice(0, -1)}A`));
  assert(tampered === null, 'tampered session token must be rejected');
  const malformed = await auth.authenticateRequest(cookieRequest('short'));
  assert(malformed === null, 'malformed session token must be rejected');

  // Cookie flags for production and development.
  const devCookie = { name: '', options: {} as any };
  auth.setSessionCookie({ cookie: (name: string, _value: string, options: any) => { devCookie.name = name; devCookie.options = options; } } as any,
    session!.token, session!.expiresAt);
  assert(devCookie.options.httpOnly === true, 'session cookie must be HttpOnly');
  assert(devCookie.options.sameSite === 'strict', 'session cookie must be SameSite=Strict');
  assert(devCookie.options.path === '/', 'session cookie must be scoped to /');
  assert(devCookie.name === 'judicial3_session', 'development cookie name');

  const priorNodeEnv = process.env.NODE_ENV;
  process.env.NODE_ENV = 'production';
  const prodCookie = { name: '', options: {} as any };
  auth.setSessionCookie({ cookie: (name: string, _value: string, options: any) => { prodCookie.name = name; prodCookie.options = options; } } as any,
    session!.token, session!.expiresAt);
  assert(prodCookie.name === '__Host-judicial3_session', 'production cookie must use the __Host- prefix');
  assert(prodCookie.options.secure === true, 'production cookie must be Secure');
  process.env.NODE_ENV = priorNodeEnv;

  // Expiry is enforced by the database, not the client.
  await db.query(`UPDATE user_sessions SET expires_at = clock_timestamp() - interval '1 minute' WHERE user_id=$1::UUID`, [userId]);
  const expired = await auth.authenticateRequest(cookieRequest(session!.token));
  assert(expired === null, 'expired server-side session must be rejected');
  await db.query(`UPDATE user_sessions SET expires_at = clock_timestamp() + interval '8 hours' WHERE user_id=$1::UUID`, [userId]);

  // Server-side revocation: clearing the cookie in a browser is not enough.
  const active = await auth.authenticateRequest(cookieRequest(session!.token));
  assert(active?.userId === userId, 'session must be active before revocation');
  const revocable = { ...cookieRequest(session!.token), userId: active!.userId, sessionHash: active!.sessionHash } as any;
  await auth.revokeRequestSession(revocable);
  const revoked = await auth.authenticateRequest(cookieRequest(session!.token));
  assert(revoked === null, 'revoked session must be rejected even with the original cookie');

  // Suspension invalidates existing sessions and blocks fresh logins.
  const second = await auth.login(username, password, request);
  assert(second, 'second login must succeed');
  await auth.suspendUser(userId);
  const suspendedSession = await auth.authenticateRequest(cookieRequest(second!.token));
  assert(suspendedSession === null, 'suspension must invalidate existing sessions');
  const suspendedLogin = await auth.login(username, password, request);
  assert(suspendedLogin === null, 'suspended user must not be able to log in');
  const state = await db.query<any>('SELECT is_active FROM users WHERE id=$1::UUID', [userId]);
  assert(state.rows[0].is_active === false, 'suspension must be persisted');

  await auth.reactivateUser(userId);
  const afterReactivate = await auth.login(username, password, request);
  assert(afterReactivate, 'reactivated user must be able to log in again');
  const afterReactivateSession = await auth.authenticateRequest(cookieRequest(afterReactivate!.token));
  assert(afterReactivateSession?.userId === userId, 'reactivated session must resolve');

  // Session rows of other users are untouched by one user's revocation.
  const other = await auth.login('reviewer_captain_01', password, request);
  assert(other?.userId === otherUserId, 'other user must authenticate independently');
  await auth.revokeAllUserSessions(userId);
  const otherStillValid = await auth.authenticateRequest(cookieRequest(other!.token));
  assert(otherStillValid?.userId === otherUserId, 'revoking one user must not revoke another user');

  // Provisioning: role lookup, password policy and duplicate handling.
  const newId = await auth.provisionUser({
    username: 'phase3_test_user', email: 'phase3@simulated-police.gov.tw',
    password: 'Phase3!ProvisionPass', fullName: '測試帳號', roleCode: 'REVIEWER',
  });
  assert(/^[0-9a-f-]{36}$/.test(newId), 'provisioned user must have a UUID');
  let shortPasswordRejected = false;
  try { await auth.provisionUser({ username: 'short_pw', email: 'short@simulated-police.gov.tw', password: 'short', fullName: '短密碼' }); }
  catch { shortPasswordRejected = true; }
  assert(shortPasswordRejected, 'provisioning must reject short passwords');
  let duplicateRejected = false;
  try { await auth.provisionUser({ username: 'phase3_test_user', email: 'other@simulated-police.gov.tw', password: 'Phase3!ProvisionPass', fullName: '重複' }); }
  catch { duplicateRejected = true; }
  assert(duplicateRejected, 'provisioning must reject duplicate usernames');

  console.log('AUTH_SESSION_LIFECYCLE_PASS: login, hashed storage, cookie flags, expiry, revocation, suspension, provisioning');
} finally {
  await closeDatabaseRuntime();
  fs.rmSync(tempDb, { recursive: true, force: true });
}


