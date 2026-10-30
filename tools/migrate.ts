process.env.NODE_ENV = process.env.NODE_ENV || 'production';
process.env.JUDICIAL3_DATABASE_ENGINE = 'postgres';
process.env.JUDICIAL3_MIGRATION_MODE = 'true';
if (process.env.MIGRATION_DATABASE_URL) process.env.DATABASE_URL = process.env.MIGRATION_DATABASE_URL;

try {
  const { databaseReadiness, closeDatabaseRuntime } = await import('../src/server/databaseRuntime.js');
  const result = await databaseReadiness();
  console.log(`MIGRATION_PASS engine=${result.engine} applied=${result.appliedMigrations}`);
  await closeDatabaseRuntime();
} catch (error) {
  console.error(`MIGRATION_FAILED reason=${error instanceof Error ? error.message : 'unknown error'}`);
  process.exit(1);
}


