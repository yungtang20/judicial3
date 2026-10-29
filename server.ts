import express from 'express';
import dotenv from 'dotenv';
import { createServer as createViteServer } from 'vite';
import { GoogleGenAI } from '@google/genai';
import { requireApiUser } from './src/server/auth.js';
import type { AuthenticatedRequest } from './src/server/auth.js';

dotenv.config();

const app = express();
const PORT = 3000;

app.use(express.json({ limit: '10mb' }));

// Init Gemini client using the recommended @google/genai SDK
const apiKey = process.env.GEMINI_API_KEY;
const ai = apiKey
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
app.post('/api/chat', async (req, res) => {
  try {
    const { messages, systemInstruction } = req.body;
    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ error: 'messages array required' });
    }

    if (!ai) {
      return res.json({
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
      model: 'gemini-3.8-flash',
      contents,
      config: {
        systemInstruction: systemInstruction || defaultSystemInstruction,
      },
    });

    const reply = response.text || '';
    return res.json({
      hasGemini: true,
      reply,
    });
  } catch (error: any) {
    // Graceful fallback to local rule-based investigation assistant when API key is unavailable or restricted
    return res.json({
      hasGemini: false,
      reply: null,
      fallback: true,
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
    const { saveCaseAnalysis } = await import('./src/server/databaseService.js');
    const result = await saveCaseAnalysis({ ...req.body, ownerId: req.userId });
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
    model: 'gemini-3.8-flash',
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
