import { spawn, type ChildProcess } from 'node:child_process';
import path from 'node:path';

const root = process.cwd();
const secret = 'route-test-secret-for-local-mvp-only';
const port = 32_000 + (process.pid % 10_000);
process.env.JUDICIAL3_SESSION_SECRET = secret;
const { createSessionToken } = await import('../src/server/auth');
const child: ChildProcess = spawn(
  path.join(root, 'node_modules', '.bin', process.platform === 'win32' ? 'tsx.exe' : 'tsx'),
  ['server.ts'],
  {
    cwd: root,
    env: {
      ...process.env,
      NODE_ENV: 'production',
      PORT: String(port),
      JUDICIAL3_SESSION_SECRET: secret,
      JUDICIAL3_ALLOW_EXTERNAL_AI: 'false',
      GEMINI_API_KEY: '',
    },
    stdio: 'ignore',
  },
);

async function waitForHealth() {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/api/health`);
      if (response.ok) return;
    } catch {
      // server still starting
    }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  throw new Error('server did not start');
}

try {
  await waitForHealth();
  const devSession = await fetch(`http://127.0.0.1:${port}/api/auth/dev-session`, { method: 'POST' });
  if (devSession.status !== 404) throw new Error(`production dev session returned ${devSession.status}`);
  const unauthenticated = await fetch(`http://127.0.0.1:${port}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages: [] }),
  });
  if (unauthenticated.status !== 401) throw new Error(`unauthenticated chat returned ${unauthenticated.status}`);

  const token = createSessionToken('22222222-2222-2222-2222-222222222201');
  const authenticated = await fetch(`http://127.0.0.1:${port}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ messages: [{ role: 'user', content: '合成測試訊息' }] }),
  });
  if (authenticated.status !== 503) throw new Error(`disabled external AI returned ${authenticated.status}`);
  const authenticatedBody = await authenticated.json() as { code?: string };
  if (authenticatedBody.code !== 'LLM_NOT_CONFIGURED') throw new Error(`unexpected AI status code: ${authenticatedBody.code}`);

  console.log('API_ROUTE_AUTH_PASS: actual server route rejects unauthenticated and fails closed when external AI is disabled');
} finally {
  child.kill();
}
