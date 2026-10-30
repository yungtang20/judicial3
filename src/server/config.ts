/**
 * Production configuration validation.
 *
 * Only variable names are ever reported. Values (connection strings, keys,
 * tokens) must never appear in errors, logs or health responses.
 */

export interface ProductionConfigReport {
  production: boolean;
  ok: boolean;
  missing: string[];
  forbidden: string[];
  invalid: string[];
}

function isPostgresUrl(value: string | undefined): boolean {
  if (!value) return false;
  try {
    const parsed = new URL(value);
    return parsed.protocol === 'postgres:' || parsed.protocol === 'postgresql:';
  } catch {
    return false;
  }
}

function isHttpsOrigin(value: string | undefined): boolean {
  if (!value) return false;
  try {
    const parsed = new URL(value);
    return parsed.protocol === 'https:' && parsed.origin === value.replace(/\/$/, '');
  } catch {
    return false;
  }
}

export function inspectProductionConfig(env: NodeJS.ProcessEnv = process.env): ProductionConfigReport {
  const production = env.NODE_ENV === 'production';
  const missing: string[] = [];
  const forbidden: string[] = [];
  const invalid: string[] = [];
  if (!production) return { production, ok: true, missing, forbidden, invalid };

  if (!env.DATABASE_URL) missing.push('DATABASE_URL');
  else if (!isPostgresUrl(env.DATABASE_URL)) invalid.push('DATABASE_URL (must be a postgres:// or postgresql:// URL)');

  if (!env.JUDICIAL3_PUBLIC_ORIGIN) missing.push('JUDICIAL3_PUBLIC_ORIGIN');
  else if (!isHttpsOrigin(env.JUDICIAL3_PUBLIC_ORIGIN)) invalid.push('JUDICIAL3_PUBLIC_ORIGIN (must be an https origin without a trailing slash)');

  if ((env.JUDICIAL3_DATABASE_ENGINE || 'postgres') !== 'postgres') {
    invalid.push('JUDICIAL3_DATABASE_ENGINE (production requires postgres)');
  }
  if (env.JUDICIAL3_ALLOW_DEV_SESSION === 'true') forbidden.push('JUDICIAL3_ALLOW_DEV_SESSION=true');
  if (env.JUDICIAL3_LOAD_TEST_SEED === 'true') forbidden.push('JUDICIAL3_LOAD_TEST_SEED=true');
  if (env.JUDICIAL3_ALLOW_EXTERNAL_AI === 'true' && (!env.GEMINI_API_KEY || !env.GEMINI_MODEL)) {
    invalid.push('JUDICIAL3_ALLOW_EXTERNAL_AI=true requires GEMINI_API_KEY and GEMINI_MODEL');
  }

  return {
    production,
    ok: missing.length === 0 && forbidden.length === 0 && invalid.length === 0,
    missing,
    forbidden,
    invalid,
  };
}

export function assertProductionConfig(env: NodeJS.ProcessEnv = process.env): void {
  const report = inspectProductionConfig(env);
  if (report.ok) return;
  const problems = [
    ...report.missing.map((name) => `missing ${name}`),
    ...report.forbidden.map((name) => `forbidden ${name}`),
    ...report.invalid.map((name) => `invalid ${name}`),
  ];
  throw new Error(`production configuration rejected: ${problems.join('; ')}`);
}


