import { createHash, randomUUID } from 'crypto';
import { databaseReadiness, getSqlClient, withTransaction } from './databaseRuntime.js';
import { AppError, isUniqueViolation } from './errors.js';

export const getDatabase = getSqlClient;

export async function getDatabaseHealth(ownerId?: string) {
  if (!ownerId) throw new AppError(401, 'OWNER_CONTEXT_REQUIRED', 'authenticated owner context is required');
  const readiness = await databaseReadiness();
  return withTransaction(ownerId, async (db) => {
    const tables = await db.query<any>(`SELECT COUNT(*)::text AS count FROM information_schema.tables
      WHERE table_schema='public' AND table_type='BASE TABLE'`);
    const cases = await db.query<any>('SELECT COUNT(*)::text AS count FROM cases WHERE lead_investigator_id=$1::UUID', [ownerId]);
    const revisions = await db.query<any>(`SELECT COUNT(*)::text AS count FROM case_revisions r
      JOIN cases c ON c.id=r.case_id WHERE c.lead_investigator_id=$1::UUID`, [ownerId]);
    return {
      status: 'healthy',
      engine: readiness.engine,
      appliedMigrations: readiness.appliedMigrations,
      tablesCount: Number(tables.rows[0]?.count || 0),
      caseCount: Number(cases.rows[0]?.count || 0),
      revisionCount: Number(revisions.rows[0]?.count || 0),
    };
  });
}

export async function listCases(ownerId: string) {
  return withTransaction(ownerId, async (db) => {
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
      WHERE c.lead_investigator_id = $1::UUID
      ORDER BY c.created_at DESC;
    `, [ownerId]);
    return res.rows;
  });
}

export async function getCaseDetails(caseId: string, ownerId: string) {
  return withTransaction(ownerId, async (db) => {
    const caseRes = await db.query<any>(`SELECT * FROM cases WHERE id = $1::UUID AND lead_investigator_id = $2::UUID`, [caseId, ownerId]);
    if (caseRes.rows.length === 0) return null;

    const caseObj = caseRes.rows[0];
    const revId = caseObj.current_revision_id;

    const revisionRes = await db.query<any>(`SELECT * FROM case_revisions WHERE id = $1::UUID AND case_id = $2::UUID`, [revId, caseId]);
    const revisionHistoryRes = await db.query<any>(`SELECT * FROM case_revisions WHERE case_id = $1::UUID ORDER BY revision_number ASC`, [caseId]);
    const factsRes = await db.query<any>(`SELECT * FROM facts WHERE revision_id = $1::UUID ORDER BY fact_seq ASC`, [revId]);
    const evidenceRes = await db.query<any>(`SELECT * FROM evidence_items WHERE revision_id = $1::UUID ORDER BY item_code ASC`, [revId]);
    const candidatesRes = await db.query<any>(`
      SELECT c.*, s.law_name, s.article_number, s.paragraph, s.subparagraph, s.content AS statute_content, s.effective_date, s.is_current
      FROM legal_candidates c
      LEFT JOIN statute_references s ON s.id = c.statute_id
      WHERE c.revision_id = $1::UUID
      ORDER BY c.id
    `, [revId]);
    const elementsRes = await db.query<any>(`SELECT * FROM constituent_elements WHERE revision_id = $1::UUID ORDER BY candidate_id, id`, [revId]);
    const questionsRes = await db.query<any>(`SELECT * FROM interview_questions WHERE revision_id = $1::UUID ORDER BY question_seq ASC`, [revId]);
    const docsRes = await db.query<any>(`SELECT * FROM document_outputs WHERE revision_id = $1::UUID`, [revId]);

    return {
      case: caseObj,
      currentRevision: revisionRes.rows[0] || null,
      revisionHistory: revisionHistoryRes.rows,
      facts: factsRes.rows,
      evidence: evidenceRes.rows,
      candidates: candidatesRes.rows,
      elements: elementsRes.rows,
      questions: questionsRes.rows,
      documents: docsRes.rows,
    };
  });
}

export interface SaveCasePayload {
  ownerId: string;
  idempotencyKey?: string;
  expectedRevisionId?: string | null;
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
  evidence?: Array<{
    itemCode?: string;
    evidenceType: string;
    description: string;
    collectionStatus: 'OBTAINED' | 'REQUESTED' | 'PENDING_SEARCH' | 'UNAVAILABLE';
    source?: string;
    relatedFactRefs?: string[];
  }>;
  candidates: Array<{
    chargeName: string;
    status: 'PRIMARY' | 'ALTERNATIVE' | 'LOW_CONFIDENCE' | 'UNRESOLVED' | 'REJECTED';
    rationale: string;
    statuteRef?: string;
    elements?: Array<{
      name: string;
      description: string;
      status: 'SATISFIED' | 'UNSUPPORTED' | 'CONTESTED' | 'INSUFFICIENT_DATA' | 'PENDING_VERIFICATION';
      factRefs?: string[];
      evidenceRefs?: string[];
      missingInformation?: string[];
      reasoning?: string;
      sourceRef?: string;
    }>;
  }>;
  questions: Array<{
    seq: number;
    questionText: string;
    answerText?: string;
    isMandatory?: boolean;
    candidateRef?: string;
    elementRef?: string;
    questionType?: string;
    rationale?: string;
    targetFactRefs?: string[];
    revisionNumber?: number;
  }>;
  summary: string;
  isLocked?: boolean;
}

export interface SaveCaseResult {
  success: true;
  caseId: string;
  caseNumber: string;
  revisionId: string;
  revisionNumber: number;
  replayed?: boolean;
}

function canonicalize(value: unknown): string {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(',')}]`;
  const record = value as Record<string, unknown>;
  return `{${Object.keys(record).sort().filter((key) => record[key] !== undefined)
    .map((key) => `${JSON.stringify(key)}:${canonicalize(record[key])}`).join(',')}}`;
}

function sha256(value: string) {
  return createHash('sha256').update(value).digest('hex');
}

function parseStatuteReference(reference: string | undefined) {
  const normalized = (reference || '').trim();
  const match = normalized.match(/^(.+?)\s+§([0-9-]+)(?:\s+([IVX]+))?/i);
  if (!match) return null;
  const romanParagraphs: Record<string, number> = { I: 1, II: 2, III: 3, IV: 4, V: 5 };
  return {
    lawName: match[1].trim(),
    articleNumber: match[2],
    paragraph: romanParagraphs[(match[3] || 'I').toUpperCase()] || 1,
    original: normalized,
  };
}

async function findReplay(db: { query: <T = any>(sql: string, params?: unknown[]) => Promise<{ rows: T[] }> }, ownerId: string, key: string) {
  const result = await db.query<{ request_hash: string; response: SaveCaseResult }>(
    'SELECT request_hash, response FROM api_idempotency_keys WHERE user_id=$1::UUID AND idempotency_key=$2', [ownerId, key],
  );
  return result.rows[0] || null;
}

export async function saveCaseAnalysis(payload: SaveCasePayload): Promise<SaveCaseResult> {
  const requestHash = sha256(canonicalize({
    caseNumber: payload.caseNumber || null,
    title: payload.title,
    rawText: payload.rawText,
    facts: payload.facts,
    evidence: payload.evidence || [],
    candidates: payload.candidates,
    questions: payload.questions,
    summary: payload.summary,
    isLocked: !!payload.isLocked,
  }));

  try {
    return await withTransaction(payload.ownerId, async (db) => {
      if (payload.idempotencyKey) {
        const replay = await findReplay(db, payload.ownerId, payload.idempotencyKey);
        if (replay) {
          if (replay.request_hash !== requestHash) {
            throw new AppError(409, 'IDEMPOTENCY_MISMATCH', 'the same idempotency key was used for a different payload');
          }
          return { ...replay.response, replayed: true };
        }
      }

      const caseNumber = payload.caseNumber || `draft-${randomUUID()}`;

      const userRes = await db.query<any>('SELECT id FROM users WHERE id = $1::UUID LIMIT 1', [payload.ownerId]);
      const investigatorId = userRes.rows[0]?.id;
      if (!investigatorId) throw new AppError(401, 'UNKNOWN_OWNER', 'authenticated owner does not exist');

      const existingCase = await db.query<any>(
        'SELECT id, current_revision_id, lead_investigator_id FROM cases WHERE case_number = $1', [caseNumber],
      );
      let caseId: string;
      let parentRevisionId: string | null = null;
      let revisionNumber = 1;

      if (existingCase.rows.length > 0) {
        const existing = existingCase.rows[0];
        if (existing.lead_investigator_id !== investigatorId) {
          throw new AppError(409, 'CASE_NUMBER_UNAVAILABLE', 'case number is not available');
        }
        caseId = existing.id;
        parentRevisionId = existing.current_revision_id || null;
        if (payload.expectedRevisionId !== undefined && payload.expectedRevisionId !== parentRevisionId) {
          throw new AppError(409, 'REVISION_CONFLICT', 'the case was modified by another request; reload before saving');
        }
        const lastRev = await db.query<any>('SELECT MAX(revision_number) as max_rev FROM case_revisions WHERE case_id = $1::UUID', [caseId]);
        revisionNumber = Number(lastRev.rows[0]?.max_rev || 1) + 1;
      } else {
        if (payload.expectedRevisionId) {
          throw new AppError(409, 'REVISION_CONFLICT', 'the case no longer exists; reload before saving');
        }
        const newCase = await db.query<any>(`
          INSERT INTO cases (case_number, title, lead_investigator_id, classification_level)
          VALUES ($1::VARCHAR, $2::VARCHAR, $3::UUID, 'CONFIDENTIAL')
          RETURNING id;
        `, [caseNumber, payload.title, investigatorId]);
        caseId = newCase.rows[0].id;
      }

      const revisionHash = sha256(canonicalize({ caseId, revisionNumber, requestHash }));
      const revRes = await db.query<any>(`
        INSERT INTO case_revisions (case_id, revision_number, parent_revision_id, revision_hash, change_summary, is_locked, created_by)
        VALUES ($1::UUID, $2::INTEGER, $3::UUID, $4::VARCHAR, $5::TEXT, $6::BOOLEAN, $7::UUID)
        RETURNING id;
      `, [caseId, revisionNumber, parentRevisionId, revisionHash, `第 ${revisionNumber} 次偵查事實與問句分析快照`, payload.isLocked || false, investigatorId]);
      const revisionId = revRes.rows[0].id;

      await db.query(`UPDATE cases SET current_revision_id = $1::UUID, title = $2::VARCHAR, raw_text = $3::TEXT WHERE id = $4::UUID`,
        [revisionId, payload.title, payload.rawText, caseId]);

      for (const [index, evidence] of (payload.evidence || []).entries()) {
        await db.query(`
          INSERT INTO evidence_items
            (case_id, revision_id, item_code, name, category, description, source, collection_status, related_fact_refs)
          VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::VARCHAR, $5::VARCHAR, $6::TEXT, $7::TEXT, $8::VARCHAR, $9::JSONB);
        `, [
          caseId,
          revisionId,
          evidence.itemCode || `evidence-${index + 1}`,
          evidence.evidenceType,
          evidence.evidenceType,
          evidence.description,
          evidence.source || '',
          evidence.collectionStatus,
          JSON.stringify(evidence.relatedFactRefs || []),
        ]);
      }

      for (const f of payload.facts) {
        await db.query(`
          INSERT INTO facts (case_id, revision_id, fact_seq, description, fact_type, status, confidence_score)
          VALUES ($1::UUID, $2::UUID, $3::INTEGER, $4::TEXT, $5::VARCHAR, $6::fact_status_enum, $7::NUMERIC);
        `, [caseId, revisionId, f.seq, f.description, f.factType || 'OBJECTIVE', f.status, f.confidenceScore ?? 1.0]);
      }

      for (const c of payload.candidates) {
        const parsedStatute = parseStatuteReference(c.statuteRef);
        if (!parsedStatute) {
          throw new AppError(400, 'INVALID_STATUTE_REFERENCE', `candidate statuteRef is missing or invalid: ${c.chargeName}`);
        }
        const statRes = await db.query<any>(`
          SELECT id FROM statute_references
          WHERE law_name = $1 AND article_number = $2 AND paragraph = $3
          ORDER BY is_current DESC, effective_date DESC
          LIMIT 1;
        `, [parsedStatute.lawName, parsedStatute.articleNumber, parsedStatute.paragraph]);
        let statuteId: string;
        if (statRes.rows.length > 0) {
          statuteId = statRes.rows[0].id;
        } else {
          const newStat = await db.query<any>(`
            INSERT INTO statute_references (law_name, article_number, paragraph, content, effective_date, is_current)
            VALUES ($1, $2, $3, $4, '1900-01-01', FALSE)
            RETURNING id;
          `, [
            parsedStatute.lawName,
            parsedStatute.articleNumber,
            parsedStatute.paragraph,
            `[UNVERIFIED_SOURCE] ${parsedStatute.original}`,
          ]);
          statuteId = newStat.rows[0].id;
        }

        const candidateRes = await db.query<any>(`
          INSERT INTO legal_candidates (case_id, revision_id, statute_id, charge_name, status, rationale)
          VALUES ($1::UUID, $2::UUID, $3::UUID, $4::VARCHAR, $5::candidate_status_enum, $6::TEXT)
          RETURNING id;
        `, [caseId, revisionId, statuteId, c.chargeName, c.status, c.rationale]);
        const candidateId = candidateRes.rows[0].id;
        for (const [elementIndex, element] of (c.elements || []).entries()) {
          await db.query(`
            INSERT INTO constituent_elements
              (case_id, revision_id, candidate_id, element_type, element_name, description, status, fact_refs, evidence_refs, missing_information, reasoning, source_ref)
            VALUES ($1::UUID, $2::UUID, $3::UUID, $4::VARCHAR, $5::VARCHAR, $6::TEXT, $7::element_status_enum, $8::JSONB, $9::JSONB, $10::JSONB, $11::TEXT, $12::TEXT);
          `, [
            caseId,
            revisionId,
            candidateId,
            `ELEMENT_${elementIndex + 1}`,
            element.name,
            element.description,
            element.status === 'SATISFIED' ? 'SUPPORTED' : element.status === 'CONTESTED' ? 'CONTRADICTED' : 'UNRESOLVED',
            JSON.stringify(element.factRefs || []),
            JSON.stringify(element.evidenceRefs || []),
            JSON.stringify(element.missingInformation || []),
            element.reasoning || '',
            element.sourceRef || c.statuteRef || '',
          ]);
        }
      }

      for (const q of payload.questions) {
        await db.query(`
          INSERT INTO interview_questions
            (case_id, revision_id, question_seq, question_text, answer_text, is_mandatory, candidate_ref, element_ref, question_type, rationale, target_fact_refs, revision_number)
          VALUES ($1::UUID, $2::UUID, $3::INTEGER, $4::TEXT, $5::TEXT, $6::BOOLEAN, $7::TEXT, $8::TEXT, $9::VARCHAR, $10::TEXT, $11::JSONB, $12::INTEGER);
        `, [caseId, revisionId, q.seq, q.questionText, q.answerText || '', q.isMandatory ?? true, q.candidateRef || '', q.elementRef || '', q.questionType || '9_UNRESOLVED_INQUIRY', q.rationale || '', JSON.stringify(q.targetFactRefs || []), q.revisionNumber || revisionNumber]);
      }

      await db.query(`
        INSERT INTO document_outputs (case_id, revision_id, document_type, title, content_markdown, is_final, generated_by)
        VALUES ($1::UUID, $2::UUID, 'INVESTIGATION_REPORT', $3::VARCHAR, $4::TEXT, FALSE, $5::UUID);
      `, [caseId, revisionId, `${payload.title} - 條陳草稿`, payload.summary, investigatorId]);

      const response: SaveCaseResult = { success: true, caseId, caseNumber, revisionId, revisionNumber };
      if (payload.idempotencyKey) {
        await db.query(`INSERT INTO api_idempotency_keys(user_id, idempotency_key, request_hash, response)
          VALUES($1::UUID, $2, $3, $4::JSONB)`, [payload.ownerId, payload.idempotencyKey, requestHash, JSON.stringify(response)]);
      }
      return response;
    });
  } catch (error) {
    if (isUniqueViolation(error) && payload.idempotencyKey) {
      const replay = await withTransaction(payload.ownerId, (db) => findReplay(db, payload.ownerId, payload.idempotencyKey!));
      if (replay && replay.request_hash === requestHash) return { ...replay.response, replayed: true };
      if (replay) throw new AppError(409, 'IDEMPOTENCY_MISMATCH', 'the same idempotency key was used for a different payload');
    }
    if (isUniqueViolation(error)) {
      throw new AppError(409, 'CONCURRENT_WRITE_CONFLICT', 'the case was modified concurrently; reload and retry');
    }
    throw error;
  }
}
