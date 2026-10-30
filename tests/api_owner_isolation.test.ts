import { spawn, type ChildProcess } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const root = process.cwd();
const tempDb = fs.mkdtempSync(path.join(os.tmpdir(), 'judicial3-api-owner-'));
const secret = 'owner-route-test-secret';
const port = 34_000 + (process.pid % 10_000);
process.env.JUDICIAL3_SESSION_SECRET = secret;
const { createSessionToken } = await import('../src/server/auth');
const userA = '22222222-2222-2222-2222-222222222201';
const userB = '22222222-2222-2222-2222-222222222202';
const tokenA = createSessionToken(userA);
const tokenB = createSessionToken(userB);
const child: ChildProcess = spawn(
  path.join(root, 'node_modules', '.bin', process.platform === 'win32' ? 'tsx.exe' : 'tsx'),
  ['server.ts'],
  {
    cwd: root,
    env: {
      ...process.env,
      NODE_ENV: 'production',
      PORT: String(port),
      JUDICIAL3_DATABASE_PATH: tempDb,
      JUDICIAL3_SESSION_SECRET: secret,
      JUDICIAL3_ALLOW_DEV_SESSION: 'false',
      JUDICIAL3_ALLOW_EXTERNAL_AI: 'false',
      GEMINI_API_KEY: '',
    },
    stdio: 'ignore',
  },
);

async function waitForHealth() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
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

const headers = (token: string) => ({ 'Content-Type': 'application/json', Authorization: `Bearer ${token}` });

try {
  await waitForHealth();
  const invalidSave = await fetch(`http://127.0.0.1:${port}/api/cases/save`, {
    method: 'POST',
    headers: headers(tokenA),
    body: JSON.stringify({ title: 'invalid', rawText: 'x', summary: '', facts: [{ seq: 1, description: '', status: 'FALSE' }], candidates: [], questions: [] }),
  });
  if (invalidSave.status !== 400) throw new Error(`invalid nested payload returned ${invalidSave.status}`);

  const saveResponse = await fetch(`http://127.0.0.1:${port}/api/cases/save`, {
    method: 'POST',
    headers: headers(tokenA),
    body: JSON.stringify({
      ownerId: userB,
      title: 'owner A isolated case',
      rawText: '合成測試案件，不含真實個資。',
      summary: '隔離測試',
      facts: [{ seq: 1, description: '合成事實', status: 'ASSERTED' }],
      candidates: [],
      questions: [],
    }),
  });
  if (saveResponse.status !== 200) throw new Error(`owner A save returned ${saveResponse.status}`);
  const saved = await saveResponse.json() as { caseId: string };

  const listA = await fetch(`http://127.0.0.1:${port}/api/cases`, { headers: headers(tokenA) });
  const listB = await fetch(`http://127.0.0.1:${port}/api/cases`, { headers: headers(tokenB) });
  const bodyA = await listA.json() as { cases: Array<{ id: string }> };
  const bodyB = await listB.json() as { cases: Array<{ id: string }> };
  if (!bodyA.cases.some((item) => item.id === saved.caseId)) throw new Error('owner A cannot list own case');
  if (bodyB.cases.some((item) => item.id === saved.caseId)) throw new Error('owner B can list owner A case');

  const readA = await fetch(`http://127.0.0.1:${port}/api/cases/${saved.caseId}`, { headers: headers(tokenA) });
  const readB = await fetch(`http://127.0.0.1:${port}/api/cases/${saved.caseId}`, { headers: headers(tokenB) });
  const readNone = await fetch(`http://127.0.0.1:${port}/api/cases/${saved.caseId}`);
  if (readA.status !== 200 || readB.status !== 404 || readNone.status !== 401) {
    throw new Error(`unexpected ownership statuses: A=${readA.status} B=${readB.status} none=${readNone.status}`);
  }

  console.log('API_OWNER_ISOLATION_PASS: owner payload ignored; list/read enforce server-authenticated owner');
} finally {
  child.kill();
  await new Promise<void>((resolve) => {
    if (child.exitCode !== null) resolve();
    else child.once('exit', () => resolve());
  });
  fs.rmSync(tempDb, { recursive: true, force: true });
}
