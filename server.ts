import express from 'express';
import dotenv from 'dotenv';
import { createServer as createViteServer } from 'vite';
import { GoogleGenAI } from '@google/genai';
import { createSessionToken, requireApiUser } from './src/server/auth.js';
import type { AuthenticatedRequest } from './src/server/auth.js';

dotenv.config();

const app = express();
const PORT = Number(process.env.PORT || 3000);

app.use(express.json({ limit: '1mb' }));

// Local-only bridge for the browser MVP. Production deployments must provide a
// real login/session service and cannot use this endpoint.
app.post('/api/auth/dev-session', (req, res) => {
  const isLoopback = req.ip === '127.0.0.1' || req.ip === '::1' || req.ip === '::ffff:127.0.0.1';
  if (process.env.NODE_ENV === 'production' || process.env.JUDICIAL3_ALLOW_DEV_SESSION !== 'true' || !isLoopback) {
    return res.status(404).json({ error: 'not found' });
  }
  try {
    const userId = process.env.JUDICIAL3_DEV_USER_ID || '22222222-2222-2222-2222-222222222201';
    return res.json({ accessToken: createSessionToken(userId), userId, environment: 'local-only' });
  } catch (error: any) {
    return res.status(503).json({ error: error?.message || 'local session unavailable' });
  }
});

// Init Gemini client using the recommended @google/genai SDK
const apiKey = process.env.GEMINI_API_KEY;
const modelName = process.env.GEMINI_MODEL?.trim();
const externalAiEnabled = process.env.JUDICIAL3_ALLOW_EXTERNAL_AI === 'true';
const ai = externalAiEnabled && apiKey && modelName
  ? new GoogleGenAI({
      apiKey,
      httpOptions: {
        headers: {
          'User-Agent': 'aistudio-build',
        },
      },
    })
  : null;

// Chat endpoint supporting Taiwan Criminal Investigation context
app.post('/api/chat', requireApiUser, async (req, res) => {
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
      config: {
        systemInstruction: defaultSystemInstruction,
      },
    });

    const reply = response.text || '';
    return res.json({
      hasGemini: true,
      reply,
    });
  } catch (error: any) {
    return res.status(503).json({
      error: 'external AI service unavailable',
      code: 'LLM_UNAVAILABLE',
      hasGemini: false,
      reply: null,
      reason: error?.status === 403 || error?.message?.includes('403') ? 'KEY_RESTRICTED' : 'UNAVAILABLE'
    });
  }
});

// Database Health & Status endpoint
app.get('/api/database/status', requireApiUser, async (_req, res) => {
  try {
    const { getDatabaseHealth } = await import('./src/server/databaseService.js');
    const health = await getDatabaseHealth();
    res.json(health);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// List all cases in PostgreSQL
app.get('/api/cases', requireApiUser, async (req: AuthenticatedRequest, res) => {
  try {
    const { listCases } = await import('./src/server/databaseService.js');
    const cases = await listCases(req.userId!);
    res.json({ cases });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// Get case details by ID
app.get('/api/cases/:id', requireApiUser, async (req: AuthenticatedRequest, res) => {
  try {
    const { getCaseDetails } = await import('./src/server/databaseService.js');
    const details = await getCaseDetails(req.params.id, req.userId!);
    if (!details) return res.status(404).json({ error: 'Case not found' });
    res.json(details);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// Save case analysis into PostgreSQL with atomic revision snapshot
app.post('/api/cases/save', requireApiUser, async (req: AuthenticatedRequest, res) => {
  try {
    const body = req.body || {};
    const factStatuses = new Set(['ASSERTED', 'ADMITTED', 'DENIED', 'INFERRED', 'UNKNOWN']);
    const candidateStatuses = new Set(['PRIMARY', 'ALTERNATIVE', 'LOW_CONFIDENCE', 'UNRESOLVED', 'REJECTED']);
    if (
      typeof body.title !== 'string' || !body.title.trim() ||
      body.title.length > 500 ||
      typeof body.rawText !== 'string' || !body.rawText.trim() ||
      body.rawText.length > 200_000 ||
      typeof body.summary !== 'string' || body.summary.length > 500 ||
      !Array.isArray(body.facts) || !body.facts.every((fact: any) =>
        Number.isInteger(fact?.seq) && fact.seq > 0 && typeof fact.description === 'string' &&
        fact.description.trim().length > 0 && fact.description.length <= 20_000 && factStatuses.has(fact.status)
      ) ||
      !Array.isArray(body.candidates) || !body.candidates.every((candidate: any) =>
        typeof candidate?.chargeName === 'string' && candidate.chargeName.trim().length > 0 &&
        typeof candidate.rationale === 'string' && candidateStatuses.has(candidate.status) &&
        (candidate.statuteRef === undefined || typeof candidate.statuteRef === 'string')
      ) ||
      !Array.isArray(body.questions) || !body.questions.every((question: any) =>
        Number.isInteger(question?.seq) && question.seq > 0 && typeof question.questionText === 'string' &&
        question.questionText.trim().length > 0 && question.questionText.length <= 5_000 &&
        (question.answerText === undefined || (typeof question.answerText === 'string' && question.answerText.length <= 50_000))
      )
    ) {
      return res.status(400).json({ error: 'invalid case analysis payload' });
    }
    const { saveCaseAnalysis } = await import('./src/server/databaseService.js');
    const result = await saveCaseAnalysis({ ...body, ownerId: req.userId });
    res.json(result);
  } catch (err: any) {
    console.error('Error saving case analysis:', err);
    res.status(500).json({ error: err.message });
  }
});

// Health & configuration status endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    hasGemini: !!ai,
    externalAiEnabled,
    model: ai ? modelName : null,
  });
});

// Mount Vite middleware in development mode
if (process.env.NODE_ENV !== 'production') {
  const vite = await createViteServer({
    server: { middlewareMode: true },
    appType: 'spa',
  });
  app.use(vite.middlewares);
} else {
  app.use(express.static('dist'));
  app.get('*', (_req, res) => {
    res.sendFile('dist/index.html', { root: '.' });
  });
}

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Criminal Investigation Assistant server active on http://0.0.0.0:${PORT}`);
});
