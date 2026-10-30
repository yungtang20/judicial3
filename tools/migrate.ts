process.env.NODE_ENV = process.env.NODE_ENV || 'production';
process.env.JUDICIAL3_DATABASE_ENGINE = 'postgres';
process.env.JUDICIAL3_MIGRATION_MODE = 'true';

let closeDatabaseRuntime: (() => Promise<void>) | undefined;
try {
  const runtime = await import('../src/server/databaseRuntime.js');
  closeDatabaseRuntime = runtime.closeDatabaseRuntime;
  const { databaseReadiness } = runtime;
  const result = await databaseReadiness();
  console.log(`MIGRATION_PASS engine=${result.engine} applied=${result.appliedMigrations}`);
} catch (error) {
  console.error(`MIGRATION_FAILED reason=${error instanceof Error ? error.message : 'unknown error'}`);
  process.exitCode = 1;
} finally {
  await closeDatabaseRuntime?.().catch(() => undefined);
}


