import { PGlite } from '@electric-sql/pglite';
import { Pool, type PoolClient } from 'pg';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

export interface SqlClient {
  query<T = any>(sql: string, params?: unknown[]): Promise<{ rows: T[]; rowCount?: number | null }>;
  exec(sql: string): Promise<unknown>;
  close(): Promise<void>;
}

class PgClientAdapter implements SqlClient {
  constructor(private readonly client: Pool | PoolClient, private readonly role?: string) {}
  private async run<T>(operation: () => Promise<T>): Promise<T> {
    if (!this.role) return operation();
    await this.client.query(`SET ROLE ${this.role}`);
    try {
      return await operation();
    } finally {
      await this.client.query('RESET ROLE').catch(() => undefined);
    }
  }
  async query<T = any>(sql: string, params: unknown[] = []) {
    const run = async () => {
      const result = await this.client.query(sql, params);
      return { rows: result.rows as T[], rowCount: result.rowCount };
    };
    return this.run(run);
  }
  async exec(sql: string) { await this.run(() => this.client.query(sql)); }
  async close() { if (this.client instanceof Pool) await this.client.end(); }
}

class PgliteAdapter implements SqlClient {
  constructor(private readonly client: PGlite) {}
  query<T = any>(sql: string, params: unknown[] = []) { return this.client.query<T>(sql, params); }
  exec(sql: string) { return this.client.exec(sql); }
  async close() { await this.client.close(); }
}

type Runtime = { engine: 'postgres' | 'pglite'; client: SqlClient; pool?: Pool; postgresRole?: string };
let runtimePromise: Promise<Runtime> | null = null;
let pgliteTransaction: Promise<unknown> = Promise.resolve();

export function resetDatabaseRuntimeForTests() {
  runtimePromise = null;
  pgliteTransaction = Promise.resolve();
}

export async function closeDatabaseRuntime() {
  const runtime = await runtimePromise?.catch(() => null);
  runtimePromise = null;
  if (!runtime) return;
  await runtime.client.close();
}

function migrationFiles() {
  const dir = path.resolve(process.cwd(), 'database', 'migrations');
  return fs.readdirSync(dir).filter((name) => /^\d{4}_.+\.sql$/.test(name)).sort().map((name) => ({
    name,
    sql: fs.readFileSync(path.join(dir, name), 'utf8'),
  }));
}

type SqlToken = { kind: 'word' | 'semicolon'; value?: string; start: number; end: number };

function scanTransactionTokens(sql: string): SqlToken[] {
  const tokens: SqlToken[] = [];
  let i = 0;
  let dollarTag = '';
  while (i < sql.length) {
    if (dollarTag) {
      const end = sql.indexOf(dollarTag, i);
      if (end < 0) throw new Error('unsupported migration: unterminated dollar-quoted string');
      i = end + dollarTag.length;
      dollarTag = '';
      continue;
    }
    if (sql.startsWith('--', i)) {
      const end = sql.indexOf('\n', i + 2);
      i = end < 0 ? sql.length : end + 1;
      continue;
    }
    if (sql.startsWith('/*', i)) {
      const end = sql.indexOf('*/', i + 2);
      if (end < 0) throw new Error('unsupported migration: unterminated block comment');
      i = end + 2;
      continue;
    }
    const char = sql[i];
    if (char === "'") {
      const start = i;
      i += 1;
      while (i < sql.length) {
        if (sql[i] === "'" && sql[i + 1] === "'") { i += 2; continue; }
        if (sql[i] === "'") { i += 1; break; }
        i += 1;
      }
      if (i >= sql.length && sql[i - 1] !== "'") throw new Error(`unsupported migration: unterminated string at ${start}`);
      continue;
    }
    if (char === '"') {
      i += 1;
      while (i < sql.length) {
        if (sql[i] === '"' && sql[i + 1] === '"') { i += 2; continue; }
        if (sql[i] === '"') { i += 1; break; }
        i += 1;
      }
      continue;
    }
    if (char === '$') {
      const match = sql.slice(i).match(/^\$[A-Za-z_][A-Za-z0-9_]*\$|^\$\$/);
      if (match) { dollarTag = match[0]; i += dollarTag.length; continue; }
    }
    if (char === ';') {
      tokens.push({ kind: 'semicolon', start: i, end: i + 1 });
      i += 1;
      continue;
    }
    if (/[A-Za-z_]/.test(char)) {
      const start = i;
      i += 1;
      while (i < sql.length && /[A-Za-z0-9_$]/.test(sql[i])) i += 1;
      tokens.push({ kind: 'word', value: sql.slice(start, i).toUpperCase(), start, end: i });
      continue;
    }
    i += 1;
  }
  return tokens;
}

export function stripOuterTransaction(sql: string) {
  const tokens = scanTransactionTokens(sql);
  const firstWord = tokens.find((token) => token.kind === 'word');
  const firstSemicolon = tokens.find((token) => token.kind === 'semicolon' && firstWord && token.start >= firstWord.end);
  const lastWordIndex = tokens.map((token) => token.kind === 'word').lastIndexOf(true);
  const lastWord = lastWordIndex >= 0 ? tokens[lastWordIndex] : undefined;
  const lastSemicolon = [...tokens].reverse().find((token) => token.kind === 'semicolon');
  if (!firstWord || firstWord.value !== 'BEGIN' || !firstSemicolon || !lastWord || lastWord.value !== 'COMMIT' || !lastSemicolon || lastWord.start >= lastSemicolon.start || firstSemicolon.end >= lastWord.start) {
    throw new Error('unsupported migration transaction wrapper: expected outer BEGIN and COMMIT');
  }
  return sql.slice(0, firstWord.start) + sql.slice(firstSemicolon.end, lastWord.start) + sql.slice(lastSemicolon.end);
}

export async function runMigrations(db: SqlClient, useAdvisoryLock = false) {
  if (useAdvisoryLock) await db.query("SELECT pg_advisory_lock(hashtext('judicial3_schema_migrations'))");
  try {
    await db.query(`CREATE TABLE IF NOT EXISTS schema_migrations (
      version VARCHAR(255) PRIMARY KEY,
      checksum CHAR(64) NOT NULL,
      applied_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
    )`);
    const applied = await db.query<{ version: string; checksum: string }>('SELECT version, checksum FROM schema_migrations ORDER BY version');
    const appliedMap = new Map(applied.rows.map((row) => [row.version, row.checksum.trim()]));
    const legacy = await db.query<{ present: boolean }>("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='cases') AS present");
    if (legacy.rows[0]?.present && applied.rows.length === 0) {
      throw new Error('legacy schema has no migration ledger; backup and run the reviewed baseline procedure before migration');
    }
    const known = new Set<string>();
    for (const migration of migrationFiles()) {
      known.add(migration.name);
      const checksum = createHash('sha256').update(migration.sql).digest('hex');
      const prior = appliedMap.get(migration.name);
      if (prior && prior !== checksum) throw new Error(`migration checksum mismatch: ${migration.name}`);
      if (prior) continue;
      // The migration file and its ledger row commit together so a crash cannot
      // leave an applied-but-unrecorded schema.
      await db.query('BEGIN');
      try {
        await db.exec(stripOuterTransaction(migration.sql));
        await db.query('INSERT INTO schema_migrations(version, checksum) VALUES ($1, $2)', [migration.name, checksum]);
        await db.query('COMMIT');
      } catch (error) {
        await db.query('ROLLBACK').catch(() => undefined);
        throw error;
      }
    }
    for (const version of appliedMap.keys()) {
      if (!known.has(version)) throw new Error(`database has an unknown migration version: ${version}`);
    }
  } finally {
    if (useAdvisoryLock) await db.query("SELECT pg_advisory_unlock(hashtext('judicial3_schema_migrations'))").catch(() => undefined);
  }
}

export async function verifyMigrations(db: SqlClient) {
  const exists = await db.query<{ present: boolean }>("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='schema_migrations') AS present");
  if (!exists.rows[0]?.present) throw new Error('database migration ledger is missing');
  const applied = await db.query<{ version: string; checksum: string }>('SELECT version, checksum FROM schema_migrations');
  const appliedMap = new Map(applied.rows.map((row) => [row.version, row.checksum.trim()]));
  const known = new Set<string>();
  for (const migration of migrationFiles()) {
    known.add(migration.name);
    const expected = createHash('sha256').update(migration.sql).digest('hex');
    if (!appliedMap.has(migration.name)) throw new Error(`database migration is pending: ${migration.name}`);
    if (appliedMap.get(migration.name) !== expected) throw new Error(`migration checksum mismatch: ${migration.name}`);
  }
  for (const version of appliedMap.keys()) {
    if (!known.has(version)) throw new Error(`database has an unknown migration version: ${version}`);
  }
}

function engineFromEnv(production: boolean): 'postgres' | 'pglite' {
  const requested = (process.env.JUDICIAL3_DATABASE_ENGINE || (production ? 'postgres' : 'pglite')).toLowerCase();
  if (requested !== 'postgres' && requested !== 'pglite') {
    throw new Error("JUDICIAL3_DATABASE_ENGINE must be 'postgres' or 'pglite'");
  }
  if (production && requested !== 'postgres') {
    throw new Error('production requires JUDICIAL3_DATABASE_ENGINE=postgres and never falls back to PGlite');
  }
  return requested;
}

function redact(message: string): string {
  const url = process.env.DATABASE_URL;
  let output = String(message);
  if (url) output = output.split(url).join('[redacted-database-url]');
  return output.replace(/postgres(?:ql)?:\/\/[^\s"']+/gi, '[redacted-database-url]');
}

async function createRuntime(): Promise<Runtime> {
  const production = process.env.NODE_ENV === 'production';
  const engine = engineFromEnv(production);
  if (engine === 'postgres') {
    if (!process.env.DATABASE_URL) throw new Error('DATABASE_URL is required for the PostgreSQL engine');
    const pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      connectionTimeoutMillis: Number(process.env.JUDICIAL3_DB_CONNECT_TIMEOUT_MS || 5_000),
      idleTimeoutMillis: 30_000,
      max: Number(process.env.JUDICIAL3_DB_POOL_MAX || 10),
      application_name: 'judicial3-web',
      statement_timeout: Number(process.env.JUDICIAL3_DB_STATEMENT_TIMEOUT_MS || 15_000),
      query_timeout: Number(process.env.JUDICIAL3_DB_QUERY_TIMEOUT_MS || 20_000),
      ...(process.env.JUDICIAL3_DB_SSL === 'true' ? { ssl: { rejectUnauthorized: true } } : {}),
    });
    pool.on('error', () => { /* idle client errors must not crash the process; readiness reports them */ });
    const postgresRole = process.env.JUDICIAL3_PROVISIONING_MODE === 'true' ? 'judicial3_provisioner' : undefined;
    const db = new PgClientAdapter(pool, postgresRole);
    try {
      await db.query('SELECT 1');
      if (process.env.JUDICIAL3_MIGRATION_MODE === 'true') {
        const client = await pool.connect();
        try { await runMigrations(new PgClientAdapter(client), true); } finally { client.release(); }
      }
      // The dedicated provisioner has no migration-ledger or DDL privileges.
      // Its CLI validates current_user before any provisioning query instead.
      if (process.env.JUDICIAL3_PROVISIONING_MODE !== 'true') await verifyMigrations(db);
    } catch (error) {
      await pool.end().catch(() => undefined);
      throw new Error(`database initialization failed: ${redact(error instanceof Error ? error.message : 'unknown error')}`);
    }
    return { engine: 'postgres', client: db, pool, postgresRole };
  }

  const dbPath = process.env.JUDICIAL3_DATABASE_PATH
    ? path.resolve(process.env.JUDICIAL3_DATABASE_PATH)
    : path.resolve(process.cwd(), 'database', 'pglite_store');
  const pglite = new PGlite(dbPath);
  await pglite.waitReady;
  const db = new PgliteAdapter(pglite);
  try {
    await runMigrations(db);
    if (process.env.JUDICIAL3_LOAD_TEST_SEED === 'true' && process.env.NODE_ENV !== 'production') {
      const seeded = await db.query<{ count: string }>('SELECT COUNT(*)::text AS count FROM users');
      if (Number(seeded.rows[0]?.count || 0) === 0) {
        await db.exec(fs.readFileSync(path.resolve(process.cwd(), 'database', 'tests', 'test_data.sql'), 'utf8'));
      }
    }
  } catch (error) {
    await pglite.close().catch(() => undefined);
    throw error;
  }
  return { engine: 'pglite', client: db };
}

export async function getRuntime() {
  runtimePromise ??= createRuntime().catch((error) => { runtimePromise = null; throw error; });
  return runtimePromise;
}

export async function getSqlClient() { return (await getRuntime()).client; }

/**
 * PostgreSQL transactions set app.current_user_id with set_config(..., true),
 * which is transaction-local and therefore cannot leak across pooled requests.
 * PGlite uses one connection, so transactions are serialised with a promise
 * chain to avoid two requests interleaving BEGIN/COMMIT.
 */
export async function withTransaction<T>(userId: string | null, work: (db: SqlClient) => Promise<T>): Promise<T> {
  const runtime = await getRuntime();
  if (runtime.engine === 'postgres') {
    const client = await runtime.pool!.connect();
    const db = new PgClientAdapter(client, runtime.postgresRole);
    try {
      await db.query('BEGIN');
      if (userId) await db.query("SELECT set_config('app.current_user_id', $1, true)", [userId]);
      const result = await work(db);
      await db.query('COMMIT');
      return result;
    } catch (error) {
      await db.query('ROLLBACK').catch(() => undefined);
      throw error;
    } finally {
      client.release();
    }
  }

  const run = pgliteTransaction.then(async () => {
    const db = runtime.client;
    await db.query('BEGIN');
    try {
      const result = await work(db);
      await db.query('COMMIT');
      return result;
    } catch (error) {
      await db.query('ROLLBACK').catch(() => undefined);
      throw error;
    }
  });
  pgliteTransaction = run.then(() => undefined, () => undefined);
  return run;
}

export async function databaseReadiness() {
  const runtime = await getRuntime();
  await runtime.client.query('SELECT 1');
  const ledger = await runtime.client.query<{ count: string }>('SELECT COUNT(*)::text AS count FROM schema_migrations');
  return { engine: runtime.engine, ready: true, appliedMigrations: Number(ledger.rows[0]?.count || 0) };
}


