import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const tempDb = fs.mkdtempSync(path.join(os.tmpdir(), 'judicial3-mvp-'));
process.env.JUDICIAL3_DATABASE_PATH = tempDb;

const { getDatabase, getCaseDetails, listCases, saveCaseAnalysis } = await import('../src/server/databaseService');

const ownerId = '22222222-2222-2222-2222-222222222201';
const rawText = '甲於超商櫃檯旁手機遺失，乙拿起後離開；目前持有狀態及乙的認知仍待查。';

try {
  const saved = await saveCaseAnalysis({
    ownerId,
    caseNumber: `mvp-${Date.now()}`,
    title: 'MVP 完整流程測試案',
    rawText,
    facts: [
      { seq: 1, description: '甲表示手機是自己的', status: 'ASSERTED', confidenceScore: 0.7 },
      { seq: 2, description: '乙否認知道手機所有人', status: 'DENIED', confidenceScore: 0.6 },
      { seq: 3, description: '手機是否已脫離甲的持有仍未知', status: 'UNKNOWN', confidenceScore: 0.2 },
    ],
    evidence: [
      {
        itemCode: 'EV-001',
        evidenceType: '監視器影像',
        description: '影像是否已取得仍待確認',
        collectionStatus: 'PENDING_SEARCH',
        source: '便利商店店內系統',
        relatedFactRefs: ['local-fact-1'],
      },
    ],
    candidates: [
      {
        chargeName: '中華民國刑法第320條第1項 普通竊盜罪',
        status: 'UNRESOLVED',
        rationale: '持有狀態與主觀認知尚待查證',
        statuteRef: '中華民國刑法 §320 I',
        elements: [
          {
            name: '他人持有之動產',
            description: '手機是否仍在他人實力支配範圍',
            status: 'INSUFFICIENT_DATA',
            factRefs: ['local-fact-3'],
            missingInformation: ['取物時的實際支配範圍'],
            reasoning: '目前資料不足',
            sourceRef: 'tw-penal-320-1',
          },
        ],
      },
    ],
    questions: [
      {
        seq: 1,
        questionText: '請說明手機原本放置的位置及附近是否有人管理。',
        isMandatory: true,
        candidateRef: 'local-candidate-1',
        elementRef: 'local-element-1',
        questionType: '1_CORE_ELEMENT',
        rationale: '釐清手機是否仍在他人支配範圍',
        targetFactRefs: ['local-fact-3'],
        revisionNumber: 1,
      },
    ],
    summary: 'MVP 流程測試摘要',
    isLocked: false,
  });

  if (!saved.success || saved.revisionNumber !== 1) throw new Error('初次保存未建立 revision 1');
  const listed = await listCases(ownerId);
  if (!listed.some((item: any) => item.id === saved.caseId)) throw new Error('保存後案件清單未包含案件');

  const details = await getCaseDetails(saved.caseId, ownerId);
  if (!details?.case || details.case.raw_text !== rawText) throw new Error('重新讀取未保留原始案情');
  if (details.facts.length !== 3 || details.evidence.length !== 1) throw new Error('Fact/Evidence 未完整保存');
  if (details.evidence[0].collection_status !== 'PENDING_SEARCH') throw new Error('Evidence 狀態被錯誤提升');
  if (details.candidates.length !== 1) throw new Error('候選法律方向未保存');
  if (details.questions.length !== 1 || details.questions[0].candidate_ref !== 'local-candidate-1') throw new Error('問句追溯欄位未保存');

  const revised = await saveCaseAnalysis({
    ownerId,
    caseNumber: saved.caseNumber,
    title: 'MVP 完整流程測試案（修訂）',
    rawText: `${rawText} 已取得店內監視器影像。`,
    facts: [{ seq: 1, description: '影像顯示乙拿起手機離開', status: 'ADMITTED', confidenceScore: 0.9 }],
    evidence: [{ itemCode: 'EV-002', evidenceType: '監視器影像', description: '已取得清晰影像', collectionStatus: 'OBTAINED', source: '便利商店店內系統', relatedFactRefs: ['local-fact-1'] }],
    candidates: [{ chargeName: '中華民國刑法第320條第1項 普通竊盜罪', status: 'UNRESOLVED', rationale: '仍待完整要件核對' }],
    questions: [{ seq: 1, questionText: '請說明影像中每個動作。' }],
    summary: 'MVP 修訂摘要',
  });
  if (revised.revisionNumber !== 2) throw new Error(`修訂未建立 revision 2，實際為 ${revised.revisionNumber}`);
  const revisedDetails = await getCaseDetails(saved.caseId, ownerId);
  const revisedRawText = `${rawText} 已取得店內監視器影像。`;
  if (revisedDetails?.currentRevision?.revision_number !== 2 || revisedDetails.case.raw_text !== revisedRawText) {
    throw new Error('修訂後目前版本未正確更新');
  }
  const forbidden = await getCaseDetails(saved.caseId, '33333333-3333-3333-3333-333333333301');
  if (forbidden !== null) throw new Error('其他使用者仍可讀取案件');

  console.log('MVP_FLOW_PASS: create/save/read/revise/traceability/owner-isolation');
} finally {
  const db = await getDatabase();
  await db.close();
  fs.rmSync(tempDb, { recursive: true, force: true });
}
