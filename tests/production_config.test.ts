import { assertProductionConfig, inspectProductionConfig } from '../src/server/config';
import { handleDevSession } from '../src/server/devSession';
import { createSessionToken } from '../src/server/auth';

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

const base = { NODE_ENV: 'production' } as NodeJS.ProcessEnv;
const empty = inspectProductionConfig(base);
assert(!empty.ok && empty.missing.includes('DATABASE_URL') && empty.missing.includes('JUDICIAL3_PUBLIC_ORIGIN'), 'missing production settings must be detected');

const valid = inspectProductionConfig({
  NODE_ENV: 'production',
  DATABASE_URL: 'postgresql://app_user:placeholder@db.internal:5432/judicial3',
  JUDICIAL3_PUBLIC_ORIGIN: 'https://judicial3.example.gov.tw',
  JUDICIAL3_DATABASE_ENGINE: 'postgres',
} as NodeJS.ProcessEnv);
assert(valid.ok, `expected valid production config, got ${JSON.stringify(valid)}`);

const pglite = inspectProductionConfig({
  NODE_ENV: 'production',
  DATABASE_URL: 'postgresql://app_user:placeholder@db.internal:5432/judicial3',
  JUDICIAL3_PUBLIC_ORIGIN: 'https://judicial3.example.gov.tw',
  JUDICIAL3_DATABASE_ENGINE: 'pglite',
} as NodeJS.ProcessEnv);
assert(!pglite.ok && pglite.invalid.some((item) => item.includes('JUDICIAL3_DATABASE_ENGINE')), 'PGlite must be rejected in production');

const devAuth = inspectProductionConfig({
  NODE_ENV: 'production',
  DATABASE_URL: 'postgresql://app_user:placeholder@db.internal:5432/judicial3',
  JUDICIAL3_PUBLIC_ORIGIN: 'https://judicial3.example.gov.tw',
  JUDICIAL3_ALLOW_DEV_SESSION: 'true',
} as NodeJS.ProcessEnv);
assert(!devAuth.ok && devAuth.forbidden.some((item) => item.includes('JUDICIAL3_ALLOW_DEV_SESSION')), 'dev-session must be forbidden in production');

const seed = inspectProductionConfig({
  NODE_ENV: 'production',
  DATABASE_URL: 'postgresql://app_user:placeholder@db.internal:5432/judicial3',
  JUDICIAL3_PUBLIC_ORIGIN: 'https://judicial3.example.gov.tw',
  JUDICIAL3_LOAD_TEST_SEED: 'true',
} as NodeJS.ProcessEnv);
assert(!seed.ok && seed.forbidden.some((item) => item.includes('JUDICIAL3_LOAD_TEST_SEED')), 'test seed must be forbidden in production');

for (const privilegedName of ['MIGRATION_DATABASE_URL', 'JUDICIAL3_PROVISIONING_DATABASE_URL', 'JUDICIAL3_MIGRATION_MODE', 'JUDICIAL3_PROVISIONING_MODE']) {
  const privileged = inspectProductionConfig({
    NODE_ENV: 'production',
    DATABASE_URL: 'postgresql://app_user:placeholder@db.internal:5432/judicial3',
    JUDICIAL3_PUBLIC_ORIGIN: 'https://judicial3.example.gov.tw',
    [privilegedName]: 'present',
  } as NodeJS.ProcessEnv);
  assert(!privileged.ok && privileged.forbidden.includes(privilegedName), `${privilegedName} must be forbidden in web production`);
}

const externalAi = inspectProductionConfig({
  NODE_ENV: 'production',
  DATABASE_URL: 'postgresql://app_user:placeholder@db.internal:5432/judicial3',
  JUDICIAL3_PUBLIC_ORIGIN: 'https://judicial3.example.gov.tw',
  JUDICIAL3_ALLOW_EXTERNAL_AI: 'true',
} as NodeJS.ProcessEnv);
assert(!externalAi.ok && externalAi.invalid.some((item) => item.includes('GEMINI')), 'enabled external AI without credentials must be rejected');

let thrown = '';
try {
  assertProductionConfig({
    NODE_ENV: 'production',
    DATABASE_URL: 'postgresql://app_user:placeholder@db.internal:5432/judicial3',
  } as NodeJS.ProcessEnv);
} catch (error) {
  thrown = error instanceof Error ? error.message : String(error);
}
assert(thrown.includes('JUDICIAL3_PUBLIC_ORIGIN'), 'config failure must name the missing setting');
assert(!thrown.includes('super-secret-value'), 'config failure must never print the connection string');

// dev-session handler gating.
function responseRecorder() {
  const state = { status: 200, body: undefined as any };
  const res = {
    status: (value: number) => { state.status = value; return res; },
    json: (value: unknown) => { state.body = value; return res; },
  } as any;
  return { state, res };
}

const loopback = { ip: '127.0.0.1', header: () => undefined } as any;
const productionCall = responseRecorder();
handleDevSession(loopback, productionCall.res, { NODE_ENV: 'production', JUDICIAL3_ALLOW_DEV_SESSION: 'true' } as NodeJS.ProcessEnv);
assert(productionCall.state.status === 404, 'dev-session must be 404 in production even when the flag is set');

const unsetCall = responseRecorder();
handleDevSession(loopback, unsetCall.res, { NODE_ENV: 'development', JUDICIAL3_ALLOW_DEV_SESSION: 'false' } as NodeJS.ProcessEnv);
assert(unsetCall.state.status === 404, 'dev-session must be 404 without explicit opt-in');

const remoteCall = responseRecorder();
handleDevSession({ ip: '203.0.113.9', header: () => undefined } as any, remoteCall.res,
  { NODE_ENV: 'development', JUDICIAL3_ALLOW_DEV_SESSION: 'true' } as NodeJS.ProcessEnv);
assert(remoteCall.state.status === 404, 'dev-session must be loopback-only');

const devCall = responseRecorder();
const priorSecret = process.env.JUDICIAL3_SESSION_SECRET;
process.env.JUDICIAL3_SESSION_SECRET = 'dev-session-test-secret';
handleDevSession(loopback, devCall.res, {
  NODE_ENV: 'development', JUDICIAL3_ALLOW_DEV_SESSION: 'true', JUDICIAL3_SESSION_SECRET: 'dev-session-test-secret',
} as NodeJS.ProcessEnv);
if (priorSecret === undefined) delete process.env.JUDICIAL3_SESSION_SECRET;
else process.env.JUDICIAL3_SESSION_SECRET = priorSecret;
assert(devCall.state.status === 200 && typeof devCall.state.body.accessToken === 'string', 'explicit loopback dev-session must work');

let productionTokenRejected = false;
const prior = process.env.NODE_ENV;
process.env.NODE_ENV = 'production';
try { createSessionToken('22222222-2222-2222-2222-222222222201'); } catch { productionTokenRejected = true; }
process.env.NODE_ENV = prior;
assert(productionTokenRejected, 'legacy bearer token creation must be disabled in production');

console.log('PRODUCTION_CONFIG_PASS: fail-closed database/auth/external-AI settings and production dev-session rejection');

