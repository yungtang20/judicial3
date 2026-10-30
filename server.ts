import express from 'express';
import cookieParser from 'cookie-parser';
import { rateLimit } from 'express-rate-limit';
import dotenv from 'dotenv';
import { createServer as createViteServer } from 'vite';
import { GoogleGenAI } from '@google/genai';
import {
  clearSessionCookie, login, requireApiUser, requireCsrf, revokeRequestSession, setSessionCookie,
} from './src/server/auth.js';
import type { AuthenticatedRequest } from './src/server/auth.js';
import { handleDevSession } from './src/server/devSession.js';
import { assertProductionConfig } from './src/server/config.js';
import { AppError } from './src/server/errors.js';

dotenv.config();

const production = process.env.NODE_ENV === 'production';
assertProductionConfig();

const app = express();
const PORT = Number(process.env.PORT || 3000);
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

app.disable('x-powered-by');
if (production) app.set('trust proxy', 1);
app.use(express.json({ limit: '1mb' }));
app.use(cookieParser());

app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Referrer-Policy', 'no-referrer');
  res.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  if (req.path.startsWith('/api')) res.setHeader('Cache-Control', 'no-store');
  if (production) {
    res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
    if (!req.path.startsWith('/api')) {
      res.setHeader('Content-Security-Policy', [
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data:",
        "font-src 'self' data:",
        "connect-src 'self'",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",
      ].join('; '));
    }
  }
  next();
});

function sendApiError(res: express.Response, error: unknown) {
  if (error instanceof AppError) {
    return res.status(error.status).json({ error: error.message, code: error.code });
  }
  const name = error instanceof Error ? error.name : 'UnknownError';
  console.error(`api_request_failed name=${name}`);
  return res.status(500).json({ error: 'internal error', code: 'INTERNAL_ERROR' });
}

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 8,
  standardHeaders: true,
  legacyHeaders: false,
  skipSuccessfulRequests: true,
});

app.post('/api/auth/login', loginLimiter, async (req, res) => {
  try {
    if (production && req.header('origin') !== process.env.JUDICIAL3_PUBLIC_ORIGIN) {
      return res.status(403).json({ error: 'request verification failed' });
    }
    const username = typeof req.body?.username === 'string' ? req.body.username.trim() : '';
    const password = typeof req.body?.password === 'string' ? req.body.password : '';
    if (!username || !password || username.length > 128 || password.length > 1024) {
      return res.status(401).json({ error: 'invalid credentials' });
    }
    const session = await login(username, password, req);
    if (!session) return res.status(401).json({ error: 'invalid credentials' });
    setSessionCookie(res, session.token, session.expiresAt);
    return res.json({ userId: session.userId, csrfToken: session.csrf, expiresAt: session.expiresAt.toISOString() });
  } catch {
    return res.status(503).json({ error: 'authentication service unavailable' });
  }
});

app.get('/api/auth/me', requireApiUser, (req: AuthenticatedRequest, res) => res.json({ userId: req.userId }));

app.post('/api/auth/logout', requireApiUser, requireCsrf, async (req: AuthenticatedRequest, res) => {
  try {
    await revokeRequestSession(req);
  } catch {
    // The cookie is still cleared; the server-side row remains revoked or expires.
  } finally {
    clearSessionCookie(res);
  }
  return res.status(204).end();
});

app.post('/api/auth/dev-session', (req, res) => handleDevSession(req, res));

const apiKey = process.env.GEMINI_API_KEY;
const modelName = process.env.GEMINI_MODEL?.trim();
const externalAiEnabled = process.env.JUDICIAL3_ALLOW_EXTERNAL_AI === 'true';
const ai = externalAiEnabled && apiKey && modelName
  ? new GoogleGenAI({ apiKey, httpOptions: { headers: { 'User-Agent': 'aistudio-build' } } })
  : null;

app.post('/api/chat', requireApiUser, requireCsrf, async (req, res) => {
  try {
    const { messages } = req.body;
    if (
      !Array.isArray(messages) ||
      messages.length === 0 ||
      messages.length > 50 ||
      messages.some((message: unknown) => {
        if (!message || typeof message !== 'object') return true;
        const item = message as { role?: unknown; content?: unknown };
        return !['user', 'assistant'].includes(String(item.role)) ||
          typeof item.content !== 'string' ||
          !item.content.trim() ||
          item.content.length > 20_000;
      })
    ) {
      return res.status(400).json({ error: 'messages must contain 1-50 user/assistant text items, each at most 20000 characters' });
    }

    if (!ai) {
      return res.status(503).json({
        error: 'external AI is disabled or not configured',
        code: 'LLM_NOT_CONFIGURED',
        hasGemini: false,
        reply: null,
      });
    }

    const contents = messages.map((m: { role: string; content: string }) => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content }],
    }));

    const defaultSystemInstruction = `你是專業的台灣刑事偵查法律輔助專家（專供司法警察與檢警調辦案人員參考，時區為 Asia/Taipei）。
核心辦案原則：
1. 不得單以案由定罪，嚴禁單一罪名偏見；務必客觀評估主位罪名、備位罪名（或競合關係）與排除罪名及其法理排除理由。
2. 嚴格區分「當事人自白（ADMITTED）」、「當事人否認（DENIED）」、「當事人主張（ASSERTED）」、「偵查推論（INFERRED）」與「客觀事證」。
3. 深入援引中華民國刑法條號（例如：刑法第 339 條之 4、第 339 條、第 320 條、第 337 條）、洗錢防制法第 14 條、刑事訴訟法等規範與實務見解。
4. 針對待證事實可產製 9 大類別偵詢問句（主觀犯意、金流與交付、通訊聯絡、共犯結構、時間軌跡、知情與否認、行為手段、利益流向、防禦補強），以利逐題突破核心爭點。
5. 產製或協助撰寫「刑事案件條陳」時，恪遵台灣司法警察機關公文規範，採用民國紀年（如民國 115 年），具備完整的案由、犯罪嫌疑人、調查經過與客觀事實、扣案證物、法律爭點分析、移送建言。
6. 回應風格嚴謹、客觀、邏輯清晰、使用標準台灣繁體中文，善用清晰的 Markdown 標題、條列與排版。`;

    const response = await ai.models.generateContent({
      model: modelName!,
      contents,
      config: { systemInstruction: defaultSystemInstruction },
    });

    return res.json({ hasGemini: true, reply: response.text || '' });
  } catch {
    return res.status(503).json({
      error: 'external AI service unavailable',
      code: 'LLM_UNAVAILABLE',
      hasGemini: false,
      reply: null,
    });
  }
});

app.get('/api/database/status', requireApiUser, async (req: AuthenticatedRequest, res) => {
  try {
    const { getDatabaseHealth } = await import('./src/server/databaseService.js');
    res.json(await getDatabaseHealth(req.userId));
  } catch (error) {
    sendApiError(res, error);
  }
});

app.get('/api/cases', requireApiUser, async (req: AuthenticatedRequest, res) => {
  try {
    const { listCases } = await import('./src/server/databaseService.js');
    res.json({ cases: await listCases(req.userId!) });
  } catch (error) {
    sendApiError(res, error);
  }
});

app.get('/api/cases/:id', requireApiUser, async (req: AuthenticatedRequest, res) => {
  try {
    if (!UUID_PATTERN.test(req.params.id)) return res.status(404).json({ error: 'Case not found' });
    const { getCaseDetails } = await import('./src/server/databaseService.js');
    const details = await getCaseDetails(req.params.id, req.userId!);
    if (!details) return res.status(404).json({ error: 'Case not found' });
    res.json(details);
  } catch (error) {
    sendApiError(res, error);
  }
});

const FACT_STATUSES = new Set(['ASSERTED', 'ADMITTED', 'DENIED', 'INFERRED', 'UNKNOWN']);
const CANDIDATE_STATUSES = new Set(['PRIMARY', 'ALTERNATIVE', 'LOW_CONFIDENCE', 'UNRESOLVED', 'REJECTED']);
const EVIDENCE_STATUSES = new Set(['OBTAINED', 'REQUESTED', 'PENDING_SEARCH', 'UNAVAILABLE']);
const ELEMENT_STATUSES = new Set(['SATISFIED', 'UNSUPPORTED', 'CONTESTED', 'INSUFFICIENT_DATA', 'PENDING_VERIFICATION']);
const stringArray = (value: unknown) => value === undefined || (Array.isArray(value) && value.every((item) => typeof item === 'string' && item.length <= 500));

function validCasePayload(body: any): string | null {
  if (typeof body.title !== 'string' || !body.title.trim() || body.title.length > 255) return 'title';
  if (typeof body.rawText !== 'string' || !body.rawText.trim() || body.rawText.length > 200_000) return 'rawText';
  if (typeof body.summary !== 'string' || body.summary.length > 20_000) return 'summary';
  if (body.caseNumber !== undefined && (typeof body.caseNumber !== 'string' || body.caseNumber.length > 64)) return 'caseNumber';
  if (body.expectedRevisionId !== undefined && body.expectedRevisionId !== null &&
    (typeof body.expectedRevisionId !== 'string' || !UUID_PATTERN.test(body.expectedRevisionId))) return 'expectedRevisionId';
  if (!Array.isArray(body.facts) || !body.facts.every((fact: any) =>
    Number.isInteger(fact?.seq) && fact.seq > 0 &&
    typeof fact.description === 'string' && fact.description.trim().length > 0 && fact.description.length <= 20_000 &&
    FACT_STATUSES.has(fact.status) &&
    (fact.confidenceScore === undefined || (typeof fact.confidenceScore === 'number' && fact.confidenceScore >= 0 && fact.confidenceScore <= 1))
  )) return 'facts';
  if (body.evidence !== undefined && (!Array.isArray(body.evidence) || !body.evidence.every((item: any) =>
    typeof item?.evidenceType === 'string' && item.evidenceType.trim().length > 0 && item.evidenceType.length <= 128 &&
    typeof item.description === 'string' && item.description.trim().length > 0 && item.description.length <= 20_000 &&
    EVIDENCE_STATUSES.has(item.collectionStatus) &&
    (item.source === undefined || (typeof item.source === 'string' && item.source.length <= 4_000)) &&
    (item.itemCode === undefined || (typeof item.itemCode === 'string' && item.itemCode.length <= 100)) &&
    stringArray(item.relatedFactRefs)
  ))) return 'evidence';
  if (!Array.isArray(body.candidates) || !body.candidates.every((candidate: any) =>
    typeof candidate?.chargeName === 'string' && candidate.chargeName.trim().length > 0 && candidate.chargeName.length <= 128 &&
    typeof candidate.rationale === 'string' && CANDIDATE_STATUSES.has(candidate.status) &&
    (candidate.statuteRef === undefined || (typeof candidate.statuteRef === 'string' && candidate.statuteRef.length <= 500)) &&
    (candidate.elements === undefined || (Array.isArray(candidate.elements) && candidate.elements.every((element: any) =>
      typeof element?.name === 'string' && element.name.trim().length > 0 && element.name.length <= 128 &&
      typeof element.description === 'string' && element.description.trim().length > 0 && element.description.length <= 20_000 &&
      ELEMENT_STATUSES.has(element.status) &&
      stringArray(element.factRefs) && stringArray(element.evidenceRefs) && stringArray(element.missingInformation) &&
      (element.reasoning === undefined || (typeof element.reasoning === 'string' && element.reasoning.length <= 20_000)) &&
      (element.sourceRef === undefined || (typeof element.sourceRef === 'string' && element.sourceRef.length <= 500))
    )))
  )) return 'candidates';
  if (!Array.isArray(body.questions) || !body.questions.every((question: any) =>
    Number.isInteger(question?.seq) && question.seq > 0 &&
    typeof question.questionText === 'string' && question.questionText.trim().length > 0 && question.questionText.length <= 5_000 &&
    (question.answerText === undefined || (typeof question.answerText === 'string' && question.answerText.length <= 50_000)) &&
    (question.targetFactRefs === undefined || stringArray(question.targetFactRefs)) &&
    (question.rationale === undefined || (typeof question.rationale === 'string' && question.rationale.length <= 20_000))
  )) return 'questions';
  return null;
}

app.post('/api/cases/save', requireApiUser, requireCsrf, async (req: AuthenticatedRequest, res) => {
  try {
    const body = req.body || {};
    const invalidField = validCasePayload(body);
    if (invalidField) return res.status(400).json({ error: 'invalid case analysis payload', field: invalidField });
    const idempotencyKey = req.header('idempotency-key');
    if (idempotencyKey && (idempotencyKey.length < 8 || idempotencyKey.length > 128)) {
      return res.status(400).json({ error: 'idempotency key must contain 8-128 characters' });
    }
    const { saveCaseAnalysis } = await import('./src/server/databaseService.js');
    const result = await saveCaseAnalysis({ ...body, ownerId: req.userId, idempotencyKey: idempotencyKey || undefined });
    res.json(result);
  } catch (error) {
    sendApiError(res, error);
  }
});

app.get(['/api/health', '/api/health/live'], (_req, res) => {
  res.json({ status: 'ok', externalAiEnabled });
});

app.get('/api/health/ready', async (_req, res) => {
  try {
    const { databaseReadiness } = await import('./src/server/databaseRuntime.js');
    const database = await databaseReadiness();
    return res.json({ status: 'ready', database: database.engine, appliedMigrations: database.appliedMigrations });
  } catch {
    return res.status(503).json({ status: 'not_ready', dependency: 'database' });
  }
});

app.post('/api/legal/retrieve', requireApiUser, requireCsrf, (_req, res) => {
  return res.status(501).json({ code: 'NOT_IMPLEMENTED', verificationStatus: 'UNKNOWN', result: null });
});

app.use('/api', (_req, res) => res.status(404).json({ error: 'not found' }));

if (!production) {
  const vite = await createViteServer({
    server: { middlewareMode: true, hmr: process.env.DISABLE_HMR === 'true' ? false : undefined },
    appType: 'spa',
  });
  app.use(vite.middlewares);
} else {
  app.use(express.static('dist', { index: false }));
  app.get('*', (_req, res) => {
    res.sendFile('dist/index.html', { root: '.' });
  });
}

if (production) {
  try {
    const { databaseReadiness } = await import('./src/server/databaseRuntime.js');
    await databaseReadiness();
  } catch (error) {
    console.error(`startup_failed dependency=database reason=${error instanceof Error ? error.name : 'unknown'}`);
    process.exit(1);
  }
}

const server = app.listen(PORT, '0.0.0.0', () => {
  console.log(`Criminal Investigation Assistant server active on port ${PORT}`);
});

async function shutdown(signal: string) {
  console.log(`shutdown signal=${signal}`);
  server.close();
  const { closeDatabaseRuntime } = await import('./src/server/databaseRuntime.js');
  await closeDatabaseRuntime().catch(() => undefined);
  process.exit(0);
}

process.on('SIGTERM', () => void shutdown('SIGTERM'));
process.on('SIGINT', () => void shutdown('SIGINT'));
