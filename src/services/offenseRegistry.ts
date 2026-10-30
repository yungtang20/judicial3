import { EvidenceItem, FactItem, LegalCandidate, LegalElement } from '../types';

export interface RegisteredOffense {
  offenseId: string;
  legalName: string;
  statuteRef: string;
  statuteVersion: string;
  officialSource: string;
  elements: Array<{
    id: string;
    name: string;
    description: string;
    support: RegExp;
    contrary: RegExp;
    missing: string;
  }>;
}

export const PROPERTY_OFFENSE_REGISTRY: RegisteredOffense[] = [
  {
    offenseId: 'tw-penal-320-1',
    legalName: '中華民國刑法第320條第1項 普通竊盜罪',
    statuteRef: '中華民國刑法 §320 I',
    statuteVersion: '法務部全國法規資料庫現行法規；案件適用版本仍須依行為時核對',
    officialSource: 'https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=320',
    elements: [
      { id: 'possession', name: '他人持有之動產', description: '物品在行為時仍由他人或場所實際管領支配', support: /仍在|伸手可取|坐在|注意該|櫃檯旁|身旁|座位旁/i, contrary: /離開.{0,12}(一段時間|現場)|不在現場|已遺失|脫離持有/i, missing: '失主或場所管理者於取物時的實際支配範圍' },
      { id: 'taking', name: '破壞持有並建立新持有', description: '未經授權取得並控制該動產', support: /拿起|取走|拿走|帶離|攜離|拾得|撿到/i, contrary: /立即交給|交還|交付店員|未帶離/i, missing: '取得、攜離及控制物品的具體時序' },
      { id: 'intent', name: '不法所有意圖', description: '行為時具有排除權利人並為自己或第三人所有之意思', support: /據為己有|帶回家|關機|取出\s*(sim|sim卡)|變賣|處分/i, contrary: /交給店員|送警|尋找失主|誤以為.*不要|無人認領/i, missing: '行為時認知、目的及拿取後的具體處理' },
    ],
  },
  {
    offenseId: 'tw-penal-337',
    legalName: '中華民國刑法第337條 侵占遺失物、漂流物或其他離本人持有之物罪',
    statuteRef: '中華民國刑法 §337',
    statuteVersion: '法務部全國法規資料庫現行法規；案件適用版本仍須依行為時核對',
    officialSource: 'https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=337',
    elements: [
      { id: 'lost', name: '物品已離本人持有', description: '物品非出於權利人意思而脫離其實力支配範圍', support: /遺失|遺留|脫離持有|不在現場|離開.{0,12}(一段時間|現場)/i, contrary: /仍在|伸手可取|坐在|注意該|身旁|座位旁/i, missing: '物品脫離持有的時間、距離及現場支配狀態' },
      { id: 'acquisition', name: '拾得或取得離本人持有之物', description: '行為人取得該物並形成事實支配', support: /拿起|取走|拿走|帶離|攜離|拾得|撿到/i, contrary: /未取得|立即交給|交還/i, missing: '取得位置、方式及實際控制時間' },
      { id: 'intent', name: '意圖為自己或第三人不法所有', description: '取得後將遺失物易持有為所有之意思', support: /據為己有|帶回家|關機|取出\s*(sim|sim卡)|變賣|處分/i, contrary: /交給店員|送警|尋找失主|誤以為.*不要|無人認領/i, missing: '取得時認知及後續處理目的' },
    ],
  },
];

export const VIOLENCE_OFFENSE_REGISTRY: RegisteredOffense[] = [
  {
    offenseId: 'tw-penal-277-1',
    legalName: '中華民國刑法第277條第1項 普通傷害罪',
    statuteRef: '中華民國刑法 §277 I',
    statuteVersion: '法務部全國法規資料庫現行法規；案件適用版本仍須依行為時核對',
    officialSource: 'https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=277',
    elements: [
      { id: 'act_result', name: '傷害行為及身體健康結果', description: '有對他人身體或健康造成傷害的具體行為及結果', support: /打傷|毆打|揮擊|骨折|撕裂傷|流血|受傷/i, contrary: /未接觸|沒有受傷|未受傷/i, missing: '行為方式、受傷部位、傷勢及就醫資料' },
      { id: 'causation', name: '行為與傷勢的因果關係', description: '所描述的行為與傷勢發生時間及部位可以相互核對', support: /打傷|毆打|骨折|撕裂傷|就醫|驗傷/i, contrary: /原有傷勢|其他原因|與本次無關/i, missing: '受傷時間、傷勢形成經過及其他可能原因' },
      { id: 'intent', name: '傷害故意', description: '行為時對接觸或傷害他人身體具有認識及意思', support: /揮棒|揮擊|毆打|出拳|踢|推打/i, contrary: /意外|過失|不小心|防衛/i, missing: '行為當時的動作、力道、目的及是否有意避免傷害' },
    ],
  },
  {
    offenseId: 'tw-penal-305',
    legalName: '中華民國刑法第305條 恐嚇危害安全罪',
    statuteRef: '中華民國刑法 §305',
    statuteVersion: '法務部全國法規資料庫現行法規；案件適用版本仍須依行為時核對',
    officialSource: 'https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=305',
    elements: [
      { id: 'threat', name: '加害生命、身體、自由、名譽或財產的表示', description: '以言語、文字、動作或其他方式表示將加害他人或其關係人', support: /恐嚇|威脅|打死你|殺你|傷害你|報復/i, contrary: /沒有說|未表示|玩笑/i, missing: '原話內容、表示方式、對象及發生場合' },
      { id: 'fear', name: '使人心生畏懼而致危害於安全', description: '受影響者對該表示的理解、反應及安全感受', support: /害怕|畏懼|恐懼|不敢|擔心/i, contrary: /未害怕|不在意|未受影響/i, missing: '受影響者當時及其後的具體反應與可查證資料' },
    ],
  },
  {
    offenseId: 'tw-penal-271-2',
    legalName: '中華民國刑法第271條第2項 殺人未遂罪',
    statuteRef: '中華民國刑法 §271 II',
    statuteVersion: '法務部全國法規資料庫現行法規；案件適用版本仍須依行為時核對',
    officialSource: 'https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=271',
    elements: [
      { id: 'overt_act', name: '已著手實行殺人行為', description: '已開始實行足以造成死亡結果的具體行為，但死亡結果尚未發生', support: /頭部|頸部|胸部|重擊|揮棒|刺|勒|掐|打死你/i, contrary: /未動手|未接觸|僅口角|主動停止並救助/i, missing: '攻擊部位、工具、次數、力道及停止原因' },
      { id: 'intent', name: '殺人故意', description: '行為時對造成他人死亡結果有所認識並有意使其發生或容認', support: /打死你|殺你|致死|不讓你活|反覆攻擊/i, contrary: /意外|過失|救助|立即停手/i, missing: '行為前後言行、攻擊方式、持續程度及救助行為' },
    ],
  },
];

function elementFromDefinition(
  candidateId: string,
  offenseId: string,
  definition: RegisteredOffense['elements'][number],
  facts: FactItem[],
  evidence: EvidenceItem[]
): LegalElement {
  const matching = facts.filter((fact) => definition.support.test(fact.source_excerpt));
  const contrary = facts.filter((fact) => definition.contrary.test(fact.source_excerpt));
  const relatedEvidence = evidence
    .filter((item) => item.collection_status === 'OBTAINED')
    .filter((item) => (item.related_fact_refs || []).some((id) => matching.some((fact) => fact.id === id)))
    .map((item) => item.id);
  return {
    id: `elem-${candidateId}-${definition.id}`,
    candidate_id: candidateId,
    legal_norm: '中華民國刑法',
    norm_version: '行為時法規版本待核對',
    element_name: definition.name,
    element_description: definition.description,
    supporting_fact_refs: matching.map((fact) => fact.id),
    contrary_fact_refs: contrary.map((fact) => fact.id),
    related_evidence_refs: relatedEvidence,
    related_fact_refs: matching.map((fact) => fact.id),
    missing_information: [definition.missing],
    element_status: 'INSUFFICIENT_DATA',
    reasoning: '本要件由 registry 定義的區辨事實評估；尚未由此處直接推定法律成立。',
    source_ref: offenseId,
    requires_human_review: true,
  };
}

/**
 * 只把文字辨識為「財物取得事件可能存在」，同時建立第320、337兩條路線；
 * 不以任何單一關鍵字直接選定罪名。
 */
export function buildPropertyCandidates(
  rawText: string,
  facts: FactItem[],
  evidence: EvidenceItem[],
  caseId: string,
  revisionId: number
): LegalCandidate[] {
  const hasAcquisitionEvent = /拿起|取走|拿走|帶離|攜離|拾得|撿到/i.test(rawText);
  const hasPropertyContext = /手機|皮夾|包包|物品|財物|遺失|遺留|櫃檯|座位/i.test(rawText);
  if (!hasAcquisitionEvent || !hasPropertyContext) return [];

  const now = new Date().toISOString();
  return PROPERTY_OFFENSE_REGISTRY.map((definition, index) => {
    const candidateId = `cand-${caseId}-registry-${definition.offenseId}`;
    const elements = definition.elements.map((element) => elementFromDefinition(candidateId, definition.offenseId, element, facts, evidence));
    return {
      id: candidateId,
      case_id: caseId,
      revision_id: revisionId,
      legal_name: definition.legalName,
      statute_ref: definition.statuteRef,
      candidate_status: index === 0 ? 'UNRESOLVED' : 'ALTERNATIVE',
      support_fact_refs: [...new Set(elements.flatMap((element) => element.supporting_fact_refs || []))],
      contrary_fact_refs: [...new Set(elements.flatMap((element) => element.contrary_fact_refs || []))],
      unknown_fact_refs: facts.filter((fact) => fact.assertion_status === 'UNKNOWN').map((fact) => fact.id),
      alternative_explanations: [
        `${definition.legalName} 僅作為候選方向；持有狀態、取得行為與主觀認知仍須依事實及證據逐項核對。`,
      ],
      elements,
      statute_version: definition.statuteVersion,
      created_at: now,
    };
  });
}

export function buildViolenceCandidates(
  rawText: string,
  facts: FactItem[],
  evidence: EvidenceItem[],
  caseId: string,
  revisionId: number
): LegalCandidate[] {
  if (!/傷害|打傷|毆打|球棒|骨折|流血|撕裂傷|恐嚇|威脅|打死你|殺你/i.test(rawText)) return [];
  const now = new Date().toISOString();
  return VIOLENCE_OFFENSE_REGISTRY.map((definition, index) => {
    const candidateId = `cand-${caseId}-registry-${definition.offenseId}`;
    const elements = definition.elements.map((element) => elementFromDefinition(candidateId, definition.offenseId, element, facts, evidence));
    return {
      id: candidateId,
      case_id: caseId,
      revision_id: revisionId,
      legal_name: definition.legalName,
      statute_ref: definition.statuteRef,
      candidate_status: index === 0 ? 'UNRESOLVED' : 'ALTERNATIVE',
      support_fact_refs: [...new Set(elements.flatMap((element) => element.supporting_fact_refs || []))],
      contrary_fact_refs: [...new Set(elements.flatMap((element) => element.contrary_fact_refs || []))],
      unknown_fact_refs: facts.filter((fact) => fact.assertion_status === 'UNKNOWN').map((fact) => fact.id),
      alternative_explanations: [`${definition.legalName} 僅作為候選方向；行為、結果、主觀認知及反向事實仍須逐項核對。`],
      elements,
      statute_version: definition.statuteVersion,
      created_at: now,
    };
  });
}
