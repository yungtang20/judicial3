import { randomUUID } from 'node:crypto';
import { login, startTestServer } from './helpers/httpServer';

const password = 'Judicial3!TestPass2026';
const server = await startTestServer();

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function headers(session: { cookie: string; csrf: string }, extra: Record<string, string> = {}) {
  return { 'Content-Type': 'application/json', cookie: session.cookie, 'X-CSRF-Token': session.csrf, ...extra };
}

function payload(overrides: Record<string, unknown> = {}) {
  return {
    title: 'owner isolation case',
    rawText: '虛構測試案情：被害人交付金錢後發現遭詐騙，尚未確認款項流向。',
    summary: '虛構測試摘要',
    facts: [
      { seq: 1, description: '被害人指稱交付金錢', status: 'ASSERTED', confidenceScore: 0.7 },
      { seq: 2, description: '款項流向仍待查明', status: 'UNKNOWN', confidenceScore: 0 },
    ],
    evidence: [],
    candidates: [{
      chargeName: '中華民國刑法 §339 I 詐欺取財', status: 'UNRESOLVED', rationale: '尚待查明',
      statuteRef: '中華民國刑法 §339 I',
    }],
    questions: [{ seq: 1, questionText: '請說明交付金錢的經過。', answerText: '' }],
    ...overrides,
  };
}

try {
  const ownerA = await login(server.base, 'lead_investigator_01', password);
  const ownerB = await login(server.base, 'reviewer_captain_01', password);
  assert(ownerA.status === 200 && ownerB.status === 200, 'both seeded users must log in');

  // Invalid nested evidence status is rejected before the database.
  const invalid = await fetch(`${server.base}/api/cases/save`, {
    method: 'POST', headers: headers(ownerA),
    body: JSON.stringify(payload({ evidence: [{ evidenceType: '虛構證據', description: 'x', collectionStatus: 'FALSE' }] })),
  });
  assert(invalid.status === 400, `invalid evidence status returned ${invalid.status}`);

  const caseNumber = `phase3-owner-${randomUUID()}`;
  const idempotencyKey = randomUUID();
  const saveA = await fetch(`${server.base}/api/cases/save`, {
    method: 'POST', headers: headers(ownerA, { 'Idempotency-Key': idempotencyKey }),
    body: JSON.stringify(payload({ caseNumber })),
  });
  assert(saveA.ok, `owner A save returned ${saveA.status}`);
  const saved = await saveA.json() as any;
  assert(saved.revisionNumber === 1 && saved.caseNumber === caseNumber, 'owner A first save must create revision 1');

  // Replaying the same idempotency key must not create a second case/revision.
  const replay = await fetch(`${server.base}/api/cases/save`, {
    method: 'POST', headers: headers(ownerA, { 'Idempotency-Key': idempotencyKey }),
    body: JSON.stringify(payload({ caseNumber })),
  });
  assert(replay.status === 200, `idempotent replay returned ${replay.status}`);
  const replayed = await replay.json() as any;
  assert(replayed.replayed === true && replayed.revisionId === saved.revisionId, 'replay must return the stored revision');

  // Same key with a different payload is a conflict, not a silent overwrite.
  const mismatch = await fetch(`${server.base}/api/cases/save`, {
    method: 'POST', headers: headers(ownerA, { 'Idempotency-Key': idempotencyKey }),
    body: JSON.stringify(payload({ caseNumber, title: 'different payload' })),
  });
  assert(mismatch.status === 409, `idempotency mismatch returned ${mismatch.status}`);
  assert((await mismatch.json() as any).code === 'IDEMPOTENCY_MISMATCH', 'idempotency mismatch code');

  const listA = await fetch(`${server.base}/api/cases`, { headers: { cookie: ownerA.cookie } });
  const listB = await fetch(`${server.base}/api/cases`, { headers: { cookie: ownerB.cookie } });
  const bodyA = await listA.json() as any;
  const bodyB = await listB.json() as any;
  assert(bodyA.cases.some((item: any) => item.id === saved.caseId), 'owner A must list their own case');
  assert(!bodyB.cases.some((item: any) => item.id === saved.caseId), 'owner B must not list owner A case');

  const readA = await fetch(`${server.base}/api/cases/${saved.caseId}`, { headers: { cookie: ownerA.cookie } });
  const readB = await fetch(`${server.base}/api/cases/${saved.caseId}`, { headers: { cookie: ownerB.cookie } });
  assert(readA.status === 200, 'owner A must read their own case');
  assert(readB.status === 404, 'owner B must receive 404 for owner A case');

  // Cross-owner writes using the victim's case number are refused.
  const crossSave = await fetch(`${server.base}/api/cases/save`, {
    method: 'POST', headers: headers(ownerB),
    body: JSON.stringify(payload({ caseNumber })),
  });
  assert(crossSave.status === 409, `cross-owner case number returned ${crossSave.status}`);
  assert((await crossSave.json() as any).code === 'CASE_NUMBER_UNAVAILABLE', 'cross-owner case number code');

  // Optimistic lock: stale revision and current revision.
  const stale = await fetch(`${server.base}/api/cases/save`, {
    method: 'POST', headers: headers(ownerA),
    body: JSON.stringify(payload({ caseNumber, expectedRevisionId: '11111111-1111-4111-8111-111111111111' })),
  });
  assert(stale.status === 409, `stale revision returned ${stale.status}`);
  assert((await stale.json() as any).code === 'REVISION_CONFLICT', 'stale revision code');

  const detailBefore = await readA.json() as any;
  const currentRevisionId = detailBefore.currentRevision.id;
  const second = await fetch(`${server.base}/api/cases/save`, {
    method: 'POST', headers: headers(ownerA),
    body: JSON.stringify(payload({
      caseNumber, expectedRevisionId: currentRevisionId,
      facts: [{ seq: 1, description: '被害人指稱交付金錢（已更新）', status: 'ASSERTED', confidenceScore: 0.8 }],
      questions: [{ seq: 1, questionText: '請說明交付金錢的經過。', answerText: '被害人表示於虛構日期交付。' }],
    })),
  });
  assert(second.ok, `second save returned ${second.status}`);
  const secondBody = await second.json() as any;
  assert(secondBody.revisionNumber === 2, 'second save must create revision 2');
  assert(secondBody.revisionId !== currentRevisionId, 'revision id must change');

  const detailAfter = await (await fetch(`${server.base}/api/cases/${saved.caseId}`, { headers: { cookie: ownerA.cookie } })).json() as any;
  assert(detailAfter.revisionHistory.length === 2, 'exactly two revisions must exist after replay + update');
  assert(detailAfter.questions.length === 1 && detailAfter.questions[0].answer_text === '被害人表示於虛構日期交付。', 'answer must persist');
  assert(detailAfter.facts[0].description.includes('已更新'), 'edited fact must persist');
  assert(detailAfter.currentRevision.parent_revision_id === currentRevisionId, 'revision lineage must be recorded');

  // Deleting a question is expressed as a new snapshot; older revisions remain intact.
  const third = await fetch(`${server.base}/api/cases/save`, {
    method: 'POST', headers: headers(ownerA),
    body: JSON.stringify(payload({ caseNumber, questions: [], expectedRevisionId: secondBody.revisionId })),
  });
  assert(third.status === 200, `third save returned ${third.status}`);
  const detailThird = await (await fetch(`${server.base}/api/cases/${saved.caseId}`, { headers: { cookie: ownerA.cookie } })).json() as any;
  assert(detailThird.questions.length === 0, 'deleted question must be absent from the new revision');
  assert(detailThird.revisionHistory.length === 3, 'history must preserve all revisions');

  // Owner B cannot modify owner A's case even with a direct revision id.
  const crossRevision = await fetch(`${server.base}/api/cases/save`, {
    method: 'POST', headers: headers(ownerB),
    body: JSON.stringify(payload({ caseNumber, expectedRevisionId: detailThird.currentRevision.id })),
  });
  assert(crossRevision.status === 409, 'owner B must not write to owner A case');

  console.log('API_OWNER_ISOLATION_PASS: owner list/read/write isolation, idempotent replay, optimistic locking, revision lineage');
} finally {
  await server.close();
}


