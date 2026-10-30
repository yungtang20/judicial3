import { spawn, type ChildProcess } from 'node:child_process';

const port = 36_000 + (process.pid % 10_000);
const command = process.platform === 'win32' ? (process.env.ComSpec || 'cmd.exe') : 'npm';
const args = process.platform === 'win32' ? ['/d', '/s', '/c', 'npm start'] : ['start'];
const child: ChildProcess = spawn(command, args, {
  cwd: process.cwd(),
  env: {
    ...process.env,
    NODE_ENV: 'production',
    PORT: String(port),
    JUDICIAL3_SESSION_SECRET: 'production-start-smoke-secret',
    JUDICIAL3_ALLOW_DEV_SESSION: 'false',
    JUDICIAL3_ALLOW_EXTERNAL_AI: 'false',
    GEMINI_API_KEY: '',
  },
  stdio: 'ignore',
});

try {
  let response: Response | undefined;
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      response = await fetch(`http://127.0.0.1:${port}/api/health`);
      if (response.ok) break;
    } catch {
      // server still starting
    }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  if (!response?.ok) throw new Error('production start command did not expose a healthy API');
  const health = await response.json() as { status?: string; externalAiEnabled?: boolean };
  if (health.status !== 'ok' || health.externalAiEnabled !== false) throw new Error('unexpected production health payload');
  const index = await fetch(`http://127.0.0.1:${port}/`);
  if (!index.ok || !(await index.text()).includes('<div id="root">')) throw new Error('production static UI was not served');
  console.log('PRODUCTION_START_PASS: npm start serves health and built UI with external AI disabled');
} finally {
  child.kill();
  await new Promise<void>((resolve) => {
    if (child.exitCode !== null) resolve();
    else child.once('exit', () => resolve());
  });
}
