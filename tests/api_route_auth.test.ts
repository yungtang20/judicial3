import { login, startTestServer } from './helpers/httpServer';

const username = 'lead_investigator_01';
const password = 'Judicial3!TestPass2026';
const server = await startTestServer();

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

try {
  // dev-session is disabled unless explicitly opted in.
  const devSession = await fetch(`${server.base}/api/auth/dev-session`, { method: 'POST' });
  assert(devSession.status === 404, `disabled dev-session returned ${devSession.status}`);

  // Failed login is generic and does not disclose whether the user exists.
  const unknown = await login(server.base, 'no_such_user', password);
  const wrong = await login(server.base, username, 'wrong-password');
  assert(unknown.status === 401 && wrong.status === 401, 'invalid credentials must return 401');
  assert(JSON.stringify(unknown.body) === JSON.stringify({ error: 'invalid credentials' }), 'login failure must not leak account state');
  assert(JSON.stringify(wrong.body) === JSON.stringify({ error: 'invalid credentials' }), 'login failure must not distinguish password from account');

  const authenticated = await login(server.base, username, password);
  assert(authenticated.status === 200, `valid login returned ${authenticated.status}`);
  assert(authenticated.cookie.startsWith('judicial3_session='), 'login must set an HttpOnly session cookie');
  assert(!authenticated.body.accessToken && !JSON.stringify(authenticated.body).includes('session_token'), 'login must not return a bearer token');

  const me = await fetch(`${server.base}/api/auth/me`, { headers: { cookie: authenticated.cookie } });
  assert(me.status === 200, 'cookie session must authenticate /api/auth/me');
  const meBody = await me.json() as any;
  assert(meBody.userId === authenticated.userId, 'me must return the authenticated user');

  // Protected APIs reject anonymous requests, including every case route.
  for (const [method, route] of [
    ['GET', '/api/cases'], ['GET', '/api/cases/22222222-2222-2222-2222-222222222201'],
    ['POST', '/api/cases/save'], ['POST', '/api/chat'], ['GET', '/api/database/status'],
    ['POST', '/api/legal/retrieve'],
  ] as const) {
    const response = await fetch(`${server.base}${route}`, { method, headers: { 'Content-Type': 'application/json' }, body: method === 'POST' ? '{}' : undefined });
    assert(response.status === 401, `${method} ${route} without a session returned ${response.status}`);
  }

  // Cookie-authenticated mutations require the CSRF token.
  const withoutCsrf = await fetch(`${server.base}/api/cases/save`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', cookie: authenticated.cookie }, body: '{}',
  });
  assert(withoutCsrf.status === 403, `save without CSRF returned ${withoutCsrf.status}`);
  const badCsrf = await fetch(`${server.base}/api/chat`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', cookie: authenticated.cookie, 'X-CSRF-Token': 'wrong' },
    body: JSON.stringify({ messages: [{ role: 'user', content: 'test' }] }),
  });
  assert(badCsrf.status === 403, `chat with wrong CSRF returned ${badCsrf.status}`);

  const chat = await fetch(`${server.base}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', cookie: authenticated.cookie, 'X-CSRF-Token': authenticated.csrf },
    body: JSON.stringify({ messages: [{ role: 'user', content: '測試訊息' }] }),
  });
  assert(chat.status === 503, `external AI must fail closed, got ${chat.status}`);
  assert((await chat.json() as any).code === 'LLM_NOT_CONFIGURED', 'external AI must report LLM_NOT_CONFIGURED');

  // Invalid identifiers must not reach the database as a 500.
  const badId = await fetch(`${server.base}/api/cases/not-a-uuid`, { headers: { cookie: authenticated.cookie } });
  assert(badId.status === 404, `invalid case id returned ${badId.status}`);

  const unknownApi = await fetch(`${server.base}/api/does-not-exist`, { headers: { cookie: authenticated.cookie } });
  assert(unknownApi.status === 404, 'unknown API route must return JSON 404');

  // Logout revokes the server-side session: the old cookie must stop working.
  const logout = await fetch(`${server.base}/api/auth/logout`, {
    method: 'POST', headers: { cookie: authenticated.cookie, 'X-CSRF-Token': authenticated.csrf },
  });
  assert(logout.status === 204, `logout returned ${logout.status}`);
  const afterLogout = await fetch(`${server.base}/api/auth/me`, { headers: { cookie: authenticated.cookie } });
  assert(afterLogout.status === 401, 'revoked session cookie must be rejected after logout');

  console.log('API_ROUTE_AUTH_PASS: real cookie login, CSRF, route protection, generic failures, fail-closed AI, logout revocation');
} finally {
  await server.close();
}
