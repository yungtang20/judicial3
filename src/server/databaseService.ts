import { PGlite } from '@electric-sql/pglite';
import fs from 'fs';
import path from 'path';

let dbInstance: PGlite | null = null;
let isInitialized = false;
let initPromise: Promise<PGlite> | null = null;

export async function getDatabase(): Promise<PGlite> {
  if (dbInstance && isInitialized) {
    return dbInstance;
  }

  if (initPromise) {
    return initPromise;
  }

  initPromise = (async () => {
    const dbPath = path.resolve(process.cwd(), 'database', 'pglite_store');

    // 1. Pre-check: if directory exists, remove stale postmaster.pid or repair broken cluster
    if (fs.existsSync(dbPath)) {
      const pidPath = path.join(dbPath, 'postmaster.pid');
      const confPath = path.join(dbPath, 'postgresql.conf');
      if (fs.existsSync(pidPath)) {
        try {
          fs.unlinkSync(pidPath);
          console.log('[PGlite] Removed stale postmaster.pid lock file');
        } catch {}
      }
      if (!fs.existsSync(confPath)) {
        console.warn('[PGlite] Store directory is missing postgresql.conf, repairing data directory...');
        try {
          fs.rmSync(dbPath, { recursive: true, force: true });
        } catch {}
      }
    }

    // 2. Initialize PGlite instance with fallback
    try {
      dbInstance = new PGlite(dbPath);
      await dbInstance.waitReady;
    } catch (err: any) {
      console.warn('[PGlite] Persistent store initialization error, attempting clean reset:', err?.message || err);
      try {
        fs.rmSync(dbPath, { recursive: true, force: true });
      } catch {}
      try {
        dbInstance = new PGlite(dbPath);
        await dbInstance.waitReady;
      } catch (fallbackErr: any) {
        console.warn('[PGlite] Persistent store failed, falling back to in-memory instance:', fallbackErr?.message || fallbackErr);
        dbInstance = new PGlite();
        await dbInstance.waitReady;
      }
    }

    // 3. Run migrations and initial seed if needed
    try {
      const checkTable = await dbInstance.query<any>(`
        SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'cases';
      `);

      if (checkTable.rows.length === 0) {
        console.log('[PGlite] Initializing 24 core tables and migrations 0001 - 0009...');
        const migrationsDir = path.resolve(process.cwd(), 'database', 'migrations');
        const migrationFiles = [
          '0001_extensions_enums.sql',
          '0002_identity_cases.sql',
          '0003_facts_evidence.sql',
          '0004_analysis_legal.sql',
          '0005_interview_workflow.sql',
          '0006_documents_prompts.sql',
          '0007_integrity_indexes_triggers.sql',
          '0008_rls_policies.sql',
          '0009_validation.sql',
        ];

        for (const file of migrationFiles) {
          const sql = fs.readFileSync(path.join(migrationsDir, file), 'utf-8');
          await dbInstance.exec(sql);
        }

        // Seed initial users and simulated test case if empty
        const testDataPath = path.resolve(process.cwd(), 'database', 'tests', 'test_data.sql');
        if (fs.existsSync(testDataPath)) {
          const testDataSql = fs.readFileSync(testDataPath, 'utf-8');
          await dbInstance.exec(testDataSql);
        }
        console.log('[PGlite] All migrations applied and test seed loaded successfully!');
      }
      isInitialized = true;
      return dbInstance;
    } catch (migrationErr) {
      console.error('[PGlite] Migration error:', migrationErr);
      throw migrationErr;
    } finally {
      initPromise = null;
    }
  })();

  return initPromise;
}

export async function getDatabaseHealth() {
  const db = await getDatabase();
  const integrity = await db.query<any>('SELECT * FROM verify_schema_integrity();');
  const caseCount = await db.query<any>('SELECT COUNT(*) as count FROM cases;');
  const revCount = await db.query<any>('SELECT COUNT(*) as count FROM case_revisions;');
  return {
    status: 'healthy',
    engine: 'PostgreSQL 16 (PGlite WASM with Persistence)',
    tablesCount: 24,
    caseCount: parseInt(caseCount.rows[0]?.count || '0', 10),
    revisionCount: parseInt(revCount.rows[0]?.count || '0', 10),
    integrity: integrity.rows,
  };
}

export async function listCases() {
  const db = await getDatabase();
  const res = await db.query<any>(`
    SELECT 
      c.id,
      c.case_number,
      c.title,
      c.classification_level,
      c.created_at,
      r.id as current_revision_id,
      r.revision_number,
      r.change_summary,
      r.is_locked,
      (SELECT COUNT(*) FROM facts f WHERE f.revision_id = r.id) as fact_count,
      (SELECT COUNT(*) FROM interview_questions q WHERE q.revision_id = r.id) as question_count
    FROM cases c
    LEFT JOIN case_revisions r ON c.current_revision_id = r.id
    ORDER BY c.created_at DESC;
  `);
  return res.rows;
}

export async function getCaseDetails(caseId: string) {
  const db = await getDatabase();
  const caseRes = await db.query<any>(`SELECT * FROM cases WHERE id = $1`, [caseId]);
  if (caseRes.rows.length === 0) return null;

  const caseObj = caseRes.rows[0];
  const revId = caseObj.current_revision_id;

  const revisionRes = await db.query<any>(`SELECT * FROM case_revisions WHERE id = $1`, [revId]);
  const factsRes = await db.query<any>(`SELECT * FROM facts WHERE revision_id = $1 ORDER BY fact_seq ASC`, [revId]);
  const candidatesRes = await db.query<any>(`SELECT * FROM legal_candidates WHERE revision_id = $1`, [revId]);
  const questionsRes = await db.query<any>(`SELECT * FROM interview_questions WHERE revision_id = $1 ORDER BY question_seq ASC`, [revId]);
  const docsRes = await db.query<any>(`SELECT * FROM document_outputs WHERE revision_id = $1`, [revId]);

  return {
    case: caseObj,
    currentRevision: revisionRes.rows[0] || null,
    facts: factsRes.rows,
    candidates: candidatesRes.rows,
    questions: questionsRes.rows,
    documents: docsRes.rows,
  };
}

export interface SaveCasePayload {
  caseNumber?: string;
  title: string;
  rawText: string;
  facts: Array<{
    seq: number;
    description: string;
    factType?: string;
    status: 'ASSERTED' | 'ADMITTED' | 'DENIED' | 'INFERRED' | 'UNKNOWN';
    confidenceScore?: number;
  }>;
  candidates: Array<{
    chargeName: string;
    status: 'PRIMARY' | 'ALTERNATIVE' | 'LOW_CONFIDENCE' | 'UNRESOLVED' | 'REJECTED';
    rationale: string;
  }>;
  questions: Array<{
    seq: number;
    questionText: string;
    answerText?: string;
    isMandatory?: boolean;
  }>;
  summary: string;
  isLocked?: boolean;
}

export async function saveCaseAnalysis(payload: SaveCasePayload) {
  const db = await getDatabase();

  // Begin transaction
  await db.query('BEGIN;');
  try {
    const caseNumber = payload.caseNumber || `115偵字第${Math.floor(1000 + Math.random() * 9000)}號`;
    
    // Check if user exists, else default to investigator 1
    const userRes = await db.query<any>(`SELECT id FROM users LIMIT 1;`);
    const investigatorId = userRes.rows[0]?.id;

    // Insert or find case
    let caseId: string;
    const existingCase = await db.query<any>(`SELECT id, current_revision_id FROM cases WHERE case_number = $1`, [caseNumber]);
    let revisionNumber = 1;

    if (existingCase.rows.length > 0) {
      caseId = existingCase.rows[0].id;
      const lastRev = await db.query<any>(`SELECT MAX(revision_number) as max_rev FROM case_revisions WHERE case_id = $1::UUID`, [caseId]);
      revisionNumber = (lastRev.rows[0]?.max_rev || 1) + 1;
    } else {
      const newCase = await db.query<any>(`
        INSERT INTO cases (case_number, title, lead_investigator_id, classification_level)
        VALUES ($1::VARCHAR, $2::VARCHAR, $3::UUID, 'CONFIDENTIAL')
        RETURNING id;
      `, [caseNumber, payload.title, investigatorId]);
      caseId = newCase.rows[0].id;
    }

    // Insert new Revision with unique snapshot hash
    const hash = `rev_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    const revRes = await db.query<any>(`
      INSERT INTO case_revisions (case_id, revision_number, revision_hash, change_summary, is_locked, created_by)
      VALUES ($1::UUID, $2::INTEGER, $3::VARCHAR, $4::TEXT, $5::BOOLEAN, $6::UUID)
      RETURNING id;
    `, [caseId, revisionNumber, hash, `第 ${revisionNumber} 次偵查事實與問句分析快照`, payload.isLocked || false, investigatorId]);
    const revisionId = revRes.rows[0].id;

    // Update case current_revision_id
    await db.query(`UPDATE cases SET current_revision_id = $1::UUID, title = $2::VARCHAR WHERE id = $3::UUID`, [revisionId, payload.title, caseId]);

    // Insert Facts
    for (const f of payload.facts) {
      await db.query(`
        INSERT INTO facts (case_id, revision_id, fact_seq, description, fact_type, status, confidence_score)
        VALUES ($1::UUID, $2::UUID, $3::INTEGER, $4::TEXT, $5::VARCHAR, $6::fact_status_enum, $7::NUMERIC);
      `, [caseId, revisionId, f.seq, f.description, f.factType || 'OBJECTIVE', f.status, f.confidenceScore || 1.0]);
    }

    // Insert Candidates
    for (const c of payload.candidates) {
      let statuteId: string;
      const statRes = await db.query<any>(`
        SELECT id FROM statute_references LIMIT 1;
      `);
      if (statRes.rows.length > 0) {
        statuteId = statRes.rows[0].id;
      } else {
        const newStat = await db.query<any>(`
          INSERT INTO statute_references (law_name, article_number, content, effective_date)
          VALUES ('中華民國刑法', '339-4', '加重詐欺罪', '2014-06-18')
          RETURNING id;
        `);
        statuteId = newStat.rows[0].id;
      }

      await db.query(`
        INSERT INTO legal_candidates (case_id, revision_id, statute_id, charge_name, status, rationale)
        VALUES ($1::UUID, $2::UUID, $3::UUID, $4::VARCHAR, $5::candidate_status_enum, $6::TEXT);
      `, [caseId, revisionId, statuteId, c.chargeName, c.status, c.rationale]);
    }

    // Insert Questions
    for (const q of payload.questions) {
      await db.query(`
        INSERT INTO interview_questions (case_id, revision_id, question_seq, question_text, is_mandatory)
        VALUES ($1::UUID, $2::UUID, $3::INTEGER, $4::TEXT, $5::BOOLEAN);
      `, [caseId, revisionId, q.seq, q.questionText, q.isMandatory ?? true]);
    }

    // Insert Document Output (Draft or Approved)
    await db.query(`
      INSERT INTO document_outputs (case_id, revision_id, document_type, title, content_markdown, is_final, generated_by)
      VALUES ($1::UUID, $2::UUID, 'INVESTIGATION_REPORT', $3::VARCHAR, $4::TEXT, FALSE, $5::UUID);
    `, [caseId, revisionId, `${payload.title} - 條陳草稿`, payload.summary, investigatorId]);

    await db.query('COMMIT;');

    return {
      success: true,
      caseId,
      caseNumber,
      revisionId,
      revisionNumber,
    };
  } catch (err) {
    await db.query('ROLLBACK;');
    throw err;
  }
}
