import { LegalReasoningEngine as Engine } from '../src/services/legalReasoningEngine';

function assert(condition: boolean, message: string) {
  if (!condition) throw new Error(message);
}

const base = '甲將手機放在便利商店櫃檯旁，乙拿起手機離開。甲表示手機是自己的；乙稱以為手機是別人遺留、不要的物品。手機當時是否仍在甲的持有範圍、乙的認知及其不法所有意圖均未確認。';
const output = Engine.analyzeFullCase(base, 'CORRECTIVE-BASE');
const names = output.candidates.map((candidate) => candidate.legal_name);

assert(names.some((name) => name.includes('320條')), '基準案應保留竊盜方向');
assert(names.some((name) => name.includes('337條')), '基準案應保留侵占遺失物方向');
assert(output.candidates.every((candidate) => candidate.id.includes('-registry-')), '手機案應由財物罪名 registry 產生，不得落回舊案型分支');
assert(output.evidence.length === 0, '僅提及未知客觀證據時不得虛構已取得證據');
assert(output.candidates.every((candidate) => candidate.elements.every((element) => element.element_status !== 'SATISFIED')),
  '無已取得證據時不得把要件標記為 SATISFIED');
assert(output.questions.some((question) => question.question_text.includes('物品原本放在哪裡')),
  'registry 路線應使用中立的持有範圍事實問句');
assert(!output.questions.some((question) => question.question_text.includes('是否具有不法所有意圖')),
  'registry 路線不得直接要求受詢問者回答法律評價');
assert(output.facts.some((fact) => fact.assertion_status === 'DENIED'), '乙的辯解須保留為 DENIED');

const withObtainedVideo = Engine.analyzeFullCase(
  `${base} 已取得店內監視器影像，畫面清晰錄得乙拿起手機離開。`,
  'CORRECTIVE-EVIDENCE'
);
assert(withObtainedVideo.evidence.some((evidence) => evidence.collection_status === 'OBTAINED'),
  '明示已取得影像時，證據狀態應為 OBTAINED');
assert(withObtainedVideo.candidates.some((candidate) => candidate.elements.some((element) =>
  element.element_status === 'SATISFIED' && (element.related_evidence_refs || []).length > 0)),
  'SATISFIED 必須同時可追溯至已取得 Evidence');

const possessionConfirmed = Engine.analyzeFullCase(
  '甲一直坐在櫃檯旁，手機放在伸手即可取回的位置，乙拿起手機離開；已取得監視器影像。',
  'CORRECTIVE-POSSESSION'
);
assert(possessionConfirmed.candidates.some((candidate) => candidate.legal_name.includes('320條') &&
  candidate.elements.some((element) => element.element_name.includes('他人持有') && element.element_status === 'SATISFIED')),
  '持有範圍與客觀影像確認後，第320條持有要件應被支持');

const lostConfirmed = Engine.analyzeFullCase(
  '甲離開店內一段時間後才發現手機遺失，手機留在原處，乙拾得後帶離；已取得監視器影像。',
  'CORRECTIVE-LOST'
);
assert(lostConfirmed.candidates.some((candidate) => candidate.legal_name.includes('337條') &&
  candidate.elements.some((element) => element.element_name.includes('已離本人持有') && element.element_status === 'SATISFIED')),
  '脫離持有與客觀影像確認後，第337條客體要件應被支持');

const returned = Engine.analyzeFullCase(
  '乙拿起手機後立即交給店員，表示要協助尋找失主；店員證述已取得。',
  'CORRECTIVE-RETURNED'
);
assert(returned.candidates.some((candidate) => candidate.elements.some((element) =>
  (element.contrary_fact_refs || []).length > 0)), '立即交付店員的有利事實必須進入要件反向事實');

const firstFact = output.caseRecord.facts[0];
assert(firstFact !== undefined, '基準案應有可修改事實');
output.caseRecord.reports[0].is_approved = true;
const revised = Engine.invalidateDownstreamOnFactChange(
  output.caseRecord,
  firstFact.id,
  { predicate: '甲一直坐在櫃檯旁且伸手即可取回手機', assertion_status: 'ASSERTED' },
  '補充持有範圍事實'
);
assert(revised.updatedCase.current_revision === output.caseRecord.current_revision + 1, '事實修改應建立新 revision');
assert(revised.updatedCase.reports.every((report) => !report.is_approved && report.validation_errors.some((error) => error.includes('[STALE]'))),
  '事實修改後舊報告核准必須失效');
assert(revised.updatedCase.audit_logs.length > output.caseRecord.audit_logs.length, '事實修改應留下稽核紀錄');
const history = revised.updatedCase.revision_history || [];
assert(history.length === 1, '事實修改應保存舊 revision 快照');
assert(history[0].reports[0]?.is_approved === true, '舊 revision 快照應保留原報告狀態');

const report = Engine.generateAndValidateReport(output.caseRecord);
assert(report.incident_time_roc.includes('待查證') || report.incident_time_roc.startsWith('民國'), '報告時間只能來自案件事實或明確待查');
assert(!report.station.includes('臺北') && !report.station.includes('中正'), '報告不得殘留硬編單位');

const violence = Engine.analyzeFullCase(
  '甲與乙在路口爭執，乙持球棒揮擊甲頭部造成流血，並說打死你；甲表示當時害怕，現場有監視器但尚未取得。',
  'CORRECTIVE-VIOLENCE-REGISTRY'
);
assert(violence.candidates.some((candidate) => candidate.id.includes('registry-tw-penal-277-1')), '傷害方向應由 violence registry 產生');
assert(violence.candidates.some((candidate) => candidate.id.includes('registry-tw-penal-305')), '恐嚇方向應由 violence registry 產生');
assert(violence.candidates.some((candidate) => candidate.id.includes('registry-tw-penal-271-2')), '殺人未遂區辨方向應由 violence registry 產生');
assert(violence.candidates.every((candidate) => candidate.elements.every((element) => element.element_status !== 'SATISFIED')),
  '暴力案件未取得客觀證據時不得由 registry 直接標記 SATISFIED');
assert(violence.questions.some((question) => question.question_text.includes('工具及每一個動作')),
  '暴力 registry 應產生行為、工具與動作的中立問句');
assert(!violence.questions.some((question) => question.question_text.includes('是否成立傷害罪')),
  '暴力 registry 問句不得直接要求受詢問者作法律評價');

console.log('CORRECTIVE_PASS: facts/evidence/element traceability, uncertainty, and revision invalidation');
