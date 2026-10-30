import { spawn } from 'node:child_process';
import net from 'node:net';
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

interface StartResult { code: number | null; output: string; durationMs: number }

async function runProduction(env: Record<string, string>): Promise<StartResult> {
  const started = Date.now();
  const command = process.platform === 'win32' ? (process.env.ComSpec || 'cmd.exe') : 'npm';
  const args = process.platform === 'win32' ? ['/d', '/s', '/c', 'npm start'] : ['start'];
  const child = spawn(command, args, {
    cwd: process.cwd(),
    env: { ...process.env, NODE_ENV: 'production', PORT: String(await freePort()), ...env },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let output = '';
  child.stdout?.on('data', (chunk) => { output += String(chunk); });
  child.stderr?.on('data', (chunk) => { output += String(chunk); });
  const code = await new Promise<number | null>((resolve) => {
    const timer = setTimeout(() => {
      if (process.platform === 'win32' && child.pid) spawn('taskkill', ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore' });
      else child.kill('SIGKILL');
      resolve(-1);
    }, 45_000);
    child.once('exit', (exitCode) => { clearTimeout(timer); resolve(exitCode); });
  });
  await new Promise((resolve) => setTimeout(resolve, 500));
  return { code, output, durationMs: Date.now() - started };
}

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

// 1. Production must reject missing database configuration instead of silently
//    falling back to PGlite or an empty in-memory database.
const missing = await runProduction({ JUDICIAL3_DATABASE_ENGINE: 'postgres' });
assert(missing.code !== null && missing.code !== 0, `production start without DATABASE_URL exited ${missing.code}`);
assert(missing.output.includes('DATABASE_URL'), 'production failure must name DATABASE_URL');
assert(!missing.output.includes('Criminal Investigation Assistant server active'), 'server must not start without production database configuration');

// 2. PGlite is explicitly rejected in production.
const pglite = await runProduction({
  JUDICIAL3_DATABASE_ENGINE: 'pglite',
  DATABASE_URL: 'postgresql://placeholder:placeholder@127.0.0.1:1/judicial3',
  JUDICIAL3_PUBLIC_ORIGIN: 'https://judicial3.example.gov.tw',
});
assert(pglite.code !== null && pglite.code !== 0, 'production start with PGlite must fail');
assert(pglite.output.includes('JUDICIAL3_DATABASE_ENGINE'), 'production failure must name the database engine');

// 3. An unreachable PostgreSQL must fail startup, not degrade to local storage.
const unreachable = await runProduction({
  JUDICIAL3_DATABASE_ENGINE: 'postgres',
  DATABASE_URL: 'postgresql://placeholder:placeholder@127.0.0.1:1/judicial3',
  JUDICIAL3_PUBLIC_ORIGIN: 'https://judicial3.example.gov.tw',
  JUDICIAL3_DB_CONNECT_TIMEOUT_MS: '2000',
});
assert(unreachable.code !== null && unreachable.code !== 0, 'unreachable PostgreSQL must fail startup');
assert(/database initialization failed|startup_failed/.test(unreachable.output), 'startup must report a database dependency failure');
assert(!unreachable.output.includes('Criminal Investigation Assistant server active'), 'server must not listen when PostgreSQL is unavailable');
assert(!unreachable.output.includes('placeholder:placeholder'), 'startup output must not print the database URL');

console.log(`PRODUCTION_START_FAIL_CLOSED_PASS: missing config=${missing.code}, pglite=${pglite.code}, unreachable-db=${unreachable.code}`);


