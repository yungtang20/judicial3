import { spawn, type ChildProcess } from 'node:child_process';
import path from 'node:path';

const root = process.cwd();
const secret = 'route-test-secret-for-local-mvp-only';
process.env.JUDICIAL3_SESSION_SECRET = secret;
const { createSessionToken } = await import('../src/server/auth');
const child: ChildProcess = spawn(
  path.join(root, 'node_modules', '.bin', process.platform === 'win32' ? 'tsx.exe' : 'tsx'),
  ['server.ts'],
  {
    cwd: root,
    env: { ...process.env, NODE_ENV: 'production', JUDICIAL3_SESSION_SECRET: secret },
    stdio: 'ignore',
  },
);

async function waitForHealth() {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    try {
      const response = await fetch('http://127.0.0.1:3000/api/health');
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
  const unauthenticated = await fetch('http://127.0.0.1:3000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages: [] }),
  });
  if (unauthenticated.status !== 401) throw new Error(`unauthenticated chat returned ${unauthenticated.status}`);

  const token = createSessionToken('22222222-2222-2222-2222-222222222201');
  const authenticated = await fetch('http://127.0.0.1:3000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ messages: [] }),
  });
  if (authenticated.status !== 200) throw new Error(`authenticated chat returned ${authenticated.status}`);

  console.log('API_ROUTE_AUTH_PASS: actual server route rejects unauthenticated and accepts verified session');
} finally {
  child.kill();
}
