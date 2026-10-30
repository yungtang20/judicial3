import { stripOuterTransaction } from '../src/server/databaseRuntime';

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

const wrapped = `-- leading comment
/* multi-line comment */
BEGIN;
CREATE TABLE parser_fixture (value TEXT);
DO $$
BEGIN
  PERFORM 'BEGIN; COMMIT;';
END
$$;
INSERT INTO parser_fixture VALUES ('COMMIT;');
COMMIT;
-- trailing comment`;
const body = stripOuterTransaction(wrapped);
assert(body.includes('-- leading comment'), 'leading comments must be preserved');
assert(body.includes('CREATE TABLE parser_fixture'), 'migration SQL must be preserved');
assert(body.includes("PERFORM 'BEGIN; COMMIT;';"), 'quoted content must be preserved');
assert(body.includes('COMMIT;'), 'inner block or literal commit must remain');
assert(body.includes('INSERT INTO parser_fixture'), 'inner statement must remain');
assert(!/^\s*BEGIN\s*;/m.test(body), 'outer BEGIN must be removed');
assert(!/\nCOMMIT;\s*-- trailing comment\s*$/m.test(body), 'outer COMMIT must be removed');

let rejected = false;
try { stripOuterTransaction('CREATE TABLE invalid_wrapper (id int);'); } catch { rejected = true; }
assert(rejected, 'unsupported transaction wrapper must be rejected');
console.log('MIGRATION_PARSER_PASS: comments, DO blocks, strings, outer wrapper and unsupported format');
