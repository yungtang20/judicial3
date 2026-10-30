import { spawn, type ChildProcess } from 'node:child_process';
import fs from 'node:fs';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';

function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      const port = typeof address === 'object' && address ? address.port : 0;
      server.close(() => resolve(port));
    });
  });
}

function killTree(child: ChildProcess) {
  if (child.exitCode !== null || !child.pid) return;
  if (process.platform === 'win32') {
    spawn('taskkill', ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore' });
    return;
  }
  child.kill('SIGKILL');
}

export interface TestServer {
  base: string;
  port: number;
  child: ChildProcess;
  output: () => string;
  close: () => Promise<void>;
}

export async function startTestServer(extraEnv: Record<string, string> = {}): Promise<TestServer> {
  const root = process.cwd();
  const tempDb = fs.mkdtempSync(path.join(os.tmpdir(), 'judicial3-http-'));
  const port = await freePort();
  let stdout = '';
  let stderr = '';
  const child = spawn(
    process.execPath,
    [path.join(root, 'node_modules', 'tsx', 'dist', 'cli.mjs'), 'server.ts'],
    {
      cwd: root,
      env: {
        ...process.env,
        NODE_ENV: 'test',
        PORT: String(port),
        JUDICIAL3_DATABASE_PATH: tempDb,
        JUDICIAL3_LOAD_TEST_SEED: 'true',
        JUDICIAL3_ALLOW_DEV_SESSION: 'false',
        JUDICIAL3_ALLOW_EXTERNAL_AI: 'false',
        DISABLE_HMR: 'true',
        GEMINI_API_KEY: '',
        GEMINI_MODEL: '',
        ...extraEnv,
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    },
  );
  child.stdout?.on('data', (chunk) => { stdout += String(chunk); });
  child.stderr?.on('data', (chunk) => { stderr += String(chunk); });

  const base = `http://127.0.0.1:${port}`;
  for (let attempt = 0; attempt < 80; attempt += 1) {
    if (child.exitCode !== null) break;
    try {
      const response = await fetch(`${base}/api/health/ready`);
      if (response.ok) {
        return {
          base, port, child,
          output: () => `${stdout}\n${stderr}`.slice(-3000),
          close: async () => {
            killTree(child);
            if (child.exitCode === null) await new Promise<void>((resolve) => child.once('exit', () => resolve()));
            fs.rmSync(tempDb, { recursive: true, force: true });
          },
        };
      }
    } catch {
      // server still starting
    }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  killTree(child);
  await new Promise((resolve) => setTimeout(resolve, 300));
  fs.rmSync(tempDb, { recursive: true, force: true });
  throw new Error(`test server did not become ready: ${`${stdout}\n${stderr}`.slice(-1000)}`);
}

export interface LoginResult {
  status: number;
  cookie: string;
  csrf: string;
  userId: string;
  body: any;
}

export async function login(base: string, username: string, password: string): Promise<LoginResult> {
  const response = await fetch(`${base}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  const body = await response.json().catch(() => ({})) as any;
  const setCookies = typeof (response.headers as any).getSetCookie === 'function'
    ? (response.headers as any).getSetCookie() as string[]
    : [response.headers.get('set-cookie') || ''];
  const session = setCookies.map((value) => value.split(';')[0]).find((value) => value.includes('judicial3_session=')) || '';
  return { status: response.status, cookie: session, csrf: body.csrfToken || '', userId: body.userId || '', body };
}
