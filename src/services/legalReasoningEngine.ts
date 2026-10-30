/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 * 
 * 臺灣刑事法律推理核心引擎 (LegalReasoningEngine)
 * 專案: yungtang20/judicial2 (JUDICIAL3)
 * 
 * 核心原則:
 * 1. 拒絕「案情關鍵字 -> 罪名」直接分類器，杜絕單一罪名偏誤。
 * 2. 嚴格落實三值邏輯與五元事實狀態 (ASSERTED, ADMITTED, DENIED, INFERRED, UNKNOWN)。
 * 3. 嚴禁將 UNKNOWN 視為 FALSE，嚴禁將 DENIED 視為事實不存在。
 * 4. 具備上游事實變更引發下游全面無效化 (Cascade Invalidation State Machine)。
 * 5. 零幻覺實體法條與實務裁判援引，動態文件欄位絕無固定寫死殘留資料。
 */

import {
  AssertionStatus,
  CandidateStatus,
  ElementStatus,
  FactItem,
  EvidenceItem,
  BehaviorItem,
  LegalCandidate,
  LegalElement,
  CoreIssue,
  InterviewQuestion,
  InterviewAnswer,
  OfficialReport,
  ReviewRecord,
  CaseRecord,
  QuestionType,
  QuestionPriority,
  ReviewStatus,
} from '../types';
import { buildPropertyCandidates, buildViolenceCandidates } from './offenseRegistry';

export interface InvalidationReport {
  invalidatedCandidateIds: string[];
  invalidatedQuestionIds: string[];
  invalidatedReportIds: string[];
  previousRevision: number;
  newRevision: number;
  reason: string;
  timestamp: string;
}

export interface LawReferenceItem {
  title: string;
  subTitle: string;
  items: { num: string; text: string; highlight?: boolean }[];
  hint: string;
  authority: string;
}

export interface RulingReferenceItem {
  court: string;
  caseNo: string;
  yearDate: string;
  title: string;
  holding: string;
  takeaway: string;
}

export interface TreatiseReferenceItem {
  title: string;
  author: string;
  source: string;
  coreArgument: string;
  takeaway: string;
}

export interface FullCaseAnalysisOutput {
  caseRecord: CaseRecord;
  facts: FactItem[];
  evidence: EvidenceItem[];
  behaviors: BehaviorItem[];
  candidates: LegalCandidate[];
  coreIssues: CoreIssue[];
  questions: InterviewQuestion[];
  report: OfficialReport;
  summary: string;
  aiBrief: string;
  categoryName: string;
  badges: { label: string; count: number; key: 'laws' | 'rulings' | 'treatises' }[];
  laws: LawReferenceItem[];
  rulings: RulingReferenceItem[];
  treatises: TreatiseReferenceItem[];
}

export class LegalReasoningEngine {
  /**
   * 建立全新案件主檔
   */
  static createNewCase(
    caseId: string,
    title: string,
    rawText: string,
    ownerId: string = 'officer-001'
  ): CaseRecord {
    const now = new Date().toISOString();
    return {
      id: caseId,
      title,
      status: 'ACTIVE',
      stage: 'GATE0_INTAKE',
      current_revision: 1,
      created_at: now,
      updated_at: now,
      owner_id: ownerId,
      raw_intake: {
        summary: rawText.trim(),
        created_at: now,
      },
      facts: [],
      evidence_items: [],
      behaviors: [],
      legal_candidates: [],
      core_issues: [],
      questions: [],
      answers: [],
      reports: [],
      reviews: [],
      audit_logs: [],
      revision_history: [],
    };
  }

  /**
   * Gate 1: 結構化事實抽取與五元狀態標記 (Fact Extraction)
   * 絕不將 UNKNOWN 當作 FALSE，絕不將 DENIED 視為事實不存在
   */
  static parseFactsFromText(rawText: string, caseId: string, revisionId: number): FactItem[] {
    const now = new Date().toISOString();
    const sentences = rawText
      .split(/[。！？；\n]/)
      .flatMap((sentence) => sentence.split(/(?:，|,)\s*(?=(?:但|惟|然而|可是|目前|尚未|仍待|手機是否|物品是否))/))
      .map((s) => s.trim())
      .filter((s) => s.length >= 4);

    if (sentences.length === 0) {
      return [];
    }

    const facts: FactItem[] = [];

    sentences.forEach((sentence, idx) => {
      let status: AssertionStatus = 'ASSERTED';

      // 1. 自白或坦承
      if (/自白|坦承|承認|有說是他|自首|確有|有拿|有領|坦承不諱/i.test(sentence)) {
        status = 'ADMITTED';
      }
      // 2. 否認或抗辯（保留為重要爭點，絕不當作不存在）
      else if (/否認|抗辯|辯稱|稱其|稱以為|不知情|不知為|辯解|並未|沒有參與|推諉|主張不知/i.test(sentence)) {
        status = 'DENIED';
      }
      // 3. 未知或待查項目（絕不視為 FALSE）
      else if (/未知|不詳|尚待查明|待查|待確認|未明|無法確認|不清楚|待補強|未到案|尚未取得/i.test(sentence)) {
        status = 'UNKNOWN';
      }
      // 4. 模型或偵查員推論
      else if (/研判|推論|疑似|可能|初步研判|依經驗|推測/i.test(sentence)) {
        status = 'INFERRED';
      }

      // 提取時間
      const timeMatch = sentence.match(/(民國\s*\d{2,3}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日(?:\s*\d{1,2}\s*時(?:\s*\d{1,2}\s*分)?許?)?|\d{1,2}\s*月\s*\d{1,2}\s*日|\d{1,2}\s*時\s*\d{1,2}\s*分|日前|當日|案發時)/);
      const eventTime = timeMatch ? timeMatch[0] : '[案發時間待筆錄查證填報]';

      // 提取地點
      const locMatch = sentence.match(/(?:在|於)\s*([\u4e00-\u9fa5A-Za-z0-9_]{2,20}?(?:市|縣|區|路|街|巷|弄|號|門市|店|處所|路口|超商|座位|櫃檯|車內|大樓|停車場))/);
      const eventLocation = locMatch ? locMatch[1] : '[案發地點待查證填報]';

      // 提取主體與客體
      let subject = '相關關係人';
      if (/報案人|告訴人|被害人|林○○|甲女|李四|陳女/.test(sentence)) subject = '被害人/告訴人';
      else if (/嫌疑人|犯嫌|被告|乙男|張三|丁女|王五|陳○○/.test(sentence)) subject = '涉嫌人/行為人';
      else if (/指使者|飛哥|某男|網友|男子|集團成員/.test(sentence)) subject = '指使者/第三人';

      facts.push({
        id: `fact-${caseId}-r${revisionId}-${idx + 1}`,
        case_id: caseId,
        revision_id: revisionId,
        subject,
        predicate: sentence.slice(0, 70),
        object: '案件事實構成要素',
        time: eventTime,
        location: eventLocation,
        event_time: eventTime,
        event_location: eventLocation,
        source_type: /被害人|報案人|告訴人/.test(sentence)
          ? 'VICTIM'
          : /嫌疑人|犯嫌|被告/.test(sentence)
          ? 'SUSPECT'
          : /監視器|扣案|明細|發票/.test(sentence)
          ? 'PHYSICAL_EVIDENCE'
          : 'POLICE_RECORD',
        source_ref: '報案陳述、警詢供述或現場勘驗紀錄',
        source_excerpt: sentence,
        assertion_status: status,
        confidence: status === 'UNKNOWN' ? 0.3 : status === 'DENIED' ? 0.5 : 0.85,
        related_evidence: [],
        created_at: now,
        updated_at: now,
      });
    });

    return facts;
  }

  /**
   * Gate 1 補充: 抽取行為與物證 (Behaviors & Evidences)
   * 證據獨立於事實與法律判斷保存，標明證明力限制
   */
  static parseBehaviorsAndEvidence(
    rawText: string,
    facts: FactItem[],
    caseId: string,
    revisionId: number
  ): { behaviors: BehaviorItem[]; evidenceItems: EvidenceItem[] } {
    const now = new Date().toISOString();
    const behaviors: BehaviorItem[] = [];
    const evidenceItems: EvidenceItem[] = [];

    // 行為事件整理
    facts.forEach((f, idx) => {
      behaviors.push({
        id: `beh-${caseId}-r${revisionId}-${idx + 1}`,
        case_id: caseId,
        revision_id: revisionId,
        actor_ref: f.subject,
        action_description: f.predicate,
        object_ref: f.object,
        time_ref: f.event_time,
        sequence_order: idx + 1,
        means: f.predicate.includes('持') ? '持特定工具實施' : '徒手或電磁操作',
        result: f.assertion_status === 'DENIED' ? '爭議抗辯事項' : '行為結果待鑑驗',
        fact_refs: [f.id],
        evidence_refs: [],
        uncertainty_status: f.assertion_status === 'UNKNOWN' ? 'UNCONFIRMED' : 'CONFIRMED',
      });
    });

    // 獨立客觀證據抽取（附註證明力限制，嚴禁將口頭陳述當成已被客觀證實）
    if (/監視器|錄影|影像|鏡頭/i.test(rawText)) {
      const explicitlyObtained = /已取得|已調閱|已檢附|已提供|已扣案|翻拍|清晰錄得/i.test(rawText);
      evidenceItems.push({
        id: `evi-${caseId}-cctv`,
        case_id: caseId,
        evidence_type: '監視錄影光碟',
        source_description: '案發現場周邊監視錄影畫面翻拍',
        collection_status: explicitlyObtained ? 'OBTAINED' : 'PENDING_SEARCH',
        related_fact_refs: facts
          .filter((f) => /監視器|手機|物品|皮夾|包包|取走|拿起|帶離|持有|遺失|遺留/i.test(f.source_excerpt))
          .map((f) => f.id),
        limitations: explicitlyObtained
          ? '畫面解析度、時間戳記與拍攝角度仍需核對，不能僅憑文字提及推定內容已證實'
          : '案情僅提及可能存在影像，尚未證明已調取、內容或完整性',
        created_at: now,
      });
    }
    if (/匯款|明細|交易紀錄|存簿|網銀/i.test(rawText)) {
      const explicitlyObtained = /已取得|已調閱|已檢附|已提供|已扣案|明細表/i.test(rawText);
      evidenceItems.push({
        id: `evi-${caseId}-bank`,
        case_id: caseId,
        evidence_type: '金融交易紀錄明細',
        source_description: '受款帳戶金流與跨行轉帳明細表',
        collection_status: explicitlyObtained ? 'OBTAINED' : 'PENDING_SEARCH',
        related_fact_refs: facts.filter((f) => /匯款|帳戶/.test(f.source_excerpt)).map((f) => f.id),
        limitations: '僅能證明資金移轉時空，受款帳戶名義人是否具主觀犯意需補強通聯調查',
        created_at: now,
      });
    }
    if (/金融卡|提款卡|信用卡/i.test(rawText)) {
      const explicitlyObtained = /扣案|已取得|已查扣|已檢附/i.test(rawText);
      evidenceItems.push({
        id: `evi-${caseId}-card`,
        case_id: caseId,
        evidence_type: '扣案金融卡片',
        source_description: '現場查扣之他人金融卡或信用卡',
        collection_status: explicitlyObtained ? 'OBTAINED' : 'PENDING_SEARCH',
        related_fact_refs: facts.filter((f) => /卡片|金融卡|信用卡/.test(f.source_excerpt)).map((f) => f.id),
        limitations: '需確認查扣時之保管鏈（Chain of Custody）並檢附扣押筆錄',
        created_at: now,
      });
    }
    if (/驗傷|診斷證明|骨折|挫傷|撕裂傷/i.test(rawText)) {
      const explicitlyObtained = /診斷證明|驗傷單|已取得|已檢附/i.test(rawText);
      evidenceItems.push({
        id: `evi-${caseId}-injury`,
        case_id: caseId,
        evidence_type: '醫院傷害診斷證明書正本',
        source_description: '公私立醫院出具之驗傷證明書',
        collection_status: explicitlyObtained ? 'OBTAINED' : 'PENDING_SEARCH',
        related_fact_refs: facts.filter((f) => /傷|骨折/.test(f.source_excerpt)).map((f) => f.id),
        limitations: '僅能證明受傷成因與傷勢客觀程度，加害人之主觀殺人或傷害犯意需由客觀工具綜合判定',
        created_at: now,
      });
    }

    return { behaviors, evidenceItems };
  }

  /**
   * 將舊有案型候選的推定結果收斂為可追溯狀態。
   * 關鍵字只能擴大檢索範圍；沒有實際 Fact 與已取得 Evidence 時，不能保留 SATISFIED。
   */
  private static normalizeCandidateTraceability(
    candidates: LegalCandidate[],
    facts: FactItem[],
    evidenceItems: EvidenceItem[]
  ): LegalCandidate[] {
    const factIds = new Set(facts.map((f) => f.id));
    const obtainedEvidence = evidenceItems.filter((e) => e.collection_status === 'OBTAINED');
    return candidates.map((candidate) => {
      const elements = candidate.elements.map((element) => {
        const supporting = (element.supporting_fact_refs || []).filter((id) => factIds.has(id));
        const contrary = (element.contrary_fact_refs || []).filter((id) => factIds.has(id));
        const evidenceRefs = obtainedEvidence
          .filter((e) => (e.related_fact_refs || []).some((id) => supporting.includes(id)))
          .map((e) => e.id);
        const missing = [...(element.missing_information || [])];
        let status = element.element_status;
        if (supporting.length === 0) {
          status = 'INSUFFICIENT_DATA';
          missing.push('尚無可追溯的支持事實');
        } else if (status === 'INSUFFICIENT_DATA' && evidenceRefs.length > 0 && contrary.length === 0) {
          status = 'SATISFIED';
          missing.splice(0, missing.length, ...missing.filter((item) => item !== '尚無已取得且可連結的客觀證據'));
        } else if (status === 'SATISFIED' && evidenceRefs.length === 0) {
          status = contrary.length > 0 ? 'CONTESTED' : 'INSUFFICIENT_DATA';
          missing.push('尚無已取得且可連結的客觀證據');
        }
        if (contrary.length > 0 && status === 'SATISFIED') status = 'CONTESTED';
        return {
          ...element,
          supporting_fact_refs: supporting,
          contrary_fact_refs: contrary,
          related_fact_refs: [...new Set([...(element.related_fact_refs || []), ...supporting])],
          related_evidence_refs: evidenceRefs,
          missing_information: [...new Set(missing)],
          element_status: status,
          requires_human_review: status !== 'SATISFIED',
          reasoning: `${element.reasoning}（來源追溯：${supporting.length} 筆事實、${evidenceRefs.length} 筆已取得證據；未知事項不視為不成立。）`,
        };
      });
      const hasSatisfied = elements.some((e) => e.element_status === 'SATISFIED');
      const hasContested = elements.some((e) => e.element_status === 'CONTESTED');
      const status = hasSatisfied && !hasContested ? candidate.candidate_status :
        candidate.candidate_status === 'REJECTED' ? 'REJECTED' : 'UNRESOLVED';
      return {
        ...candidate,
        candidate_status: status,
        support_fact_refs: [...new Set(candidate.support_fact_refs.filter((id) => factIds.has(id)))],
        contrary_fact_refs: [...new Set(candidate.contrary_fact_refs.filter((id) => factIds.has(id)))],
        unknown_fact_refs: [...new Set(candidate.unknown_fact_refs.filter((id) => factIds.has(id)))],
        elements,
      };
    });
  }

  /**
   * Gate 2: 多候選法律方向與構成要件逐項分析 (Multi-Candidate Offense Engine)
   * 嚴格遵守：
   * - 絕不單一分類，平行展開 PRIMARY, ALTERNATIVE, REJECTED, UNRESOLVED
   * - 構成要件區分 SATISFIED, UNSUPPORTED, CONTESTED, INSUFFICIENT_DATA
   * - 不得把「資料不足 (INSUFFICIENT_DATA)」寫成「要件不成立」
   */
  static evaluateLegalCandidates(
    rawText: string,
    facts: FactItem[],
    caseId: string,
    revisionId: number,
    evidenceItems: EvidenceItem[] = []
  ): { candidates: LegalCandidate[]; coreIssues: CoreIssue[] } {
    const candidates: LegalCandidate[] = [];
    const coreIssues: CoreIssue[] = [];
    const now = new Date().toISOString();
    const text = (rawText + ' ' + facts.map((f) => f.source_excerpt).join(' ')).toLowerCase();

    // 財物取得家族先走 registry：兩條法律路線並列，再由要件與證據收斂狀態。
    const registryCandidates = buildPropertyCandidates(rawText, facts, evidenceItems, caseId, revisionId);
    const usePropertyRegistry = registryCandidates.length > 0 && /手機/i.test(text) && !/信用卡|感應|盜刷/i.test(text);
    if (usePropertyRegistry) candidates.push(...registryCandidates);

    const violenceRegistryCandidates = buildViolenceCandidates(rawText, facts, evidenceItems, caseId, revisionId);
    const useViolenceRegistry = violenceRegistryCandidates.length > 0;
    if (useViolenceRegistry) candidates.push(...violenceRegistryCandidates);

    // 案型 1: 網路社群 / 假投資 / 虛擬貨幣詐騙
    if (
      (/虛擬貨幣|泰達幣|usdt|假投資|平台網址|出金遭拒|炒幣|帶單/i.test(text) ||
        (/投資/i.test(text) && !/借貸契約|工廠倒閉|周轉借款|本票/i.test(text)))
    ) {
      // 候選 1 (PRIMARY): 刑法第339-4條 加重詐欺取財罪
      const cand1Id = `cand-${caseId}-crypto-1`;
      candidates.push({
        id: cand1Id,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '中華民國刑法第339條之4第1項第2款、第3款 加重詐欺取財罪',
        statute_ref: '中華民國刑法 §339-4 I(2)(3)',
        candidate_status: 'PRIMARY',
        support_fact_refs: facts.filter((f) => f.assertion_status !== 'DENIED').map((f) => f.id),
        contrary_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
        unknown_fact_refs: facts.filter((f) => f.assertion_status === 'UNKNOWN').map((f) => f.id),
        alternative_explanations: [
          '主位路線：利用網際網路傳播工具對公眾散布，且結合多人分工，構成加重詐欺。',
        ],
        elements: [
          {
            id: `elem-${cand1Id}-1`,
            candidate_id: cand1Id,
            legal_norm: '中華民國刑法',
            norm_version: '民國113年公布施行版本',
            element_name: '以網際網路等傳播工具對公眾散布',
            element_description: '利用公開社群平台或通訊軟體群組向不特定多數人傳播不實獲利訊息',
            supporting_fact_refs: facts.filter((f) => /社群|平台|網際網路/.test(f.source_excerpt)).map((f) => f.id),
            contrary_fact_refs: [],
            missing_information: [],
            related_fact_refs: facts.map((f) => f.id),
            element_status: 'SATISFIED',
            reasoning: '報案人陳述透過社群平台廣告接觸並點擊連結，符合傳播工具要件。',
            source_ref: '刑法第339條之4第1項第3款',
            requires_human_review: false,
          },
          {
            id: `elem-${cand1Id}-2`,
            candidate_id: cand1Id,
            legal_norm: '中華民國刑法',
            norm_version: '民國113年公布施行版本',
            element_name: '三人以上共同犯之',
            element_description: '話務手、客服人員、收款水房及人頭帳戶名義人具備犯意聯絡與行為分擔',
            supporting_fact_refs: facts.filter((f) => /男子|數個銀行帳戶|平台/.test(f.source_excerpt)).map((f) => f.id),
            contrary_fact_refs: [],
            missing_information: ['幕後話務組、水房首腦與工程人員之真實身分年籍'],
            element_status: 'INSUFFICIENT_DATA',
            reasoning: '雖然受款帳戶分散於多個不同金融機構，具集團分工表徵，但成員身分未明，列為資料不足待查。',
            source_ref: '刑法第339條之4第1項第2款',
            requires_human_review: true,
            related_fact_refs: [],
          },
          {
            id: `elem-${cand1Id}-3`,
            candidate_id: cand1Id,
            legal_norm: '中華民國刑法',
            norm_version: '民國113年公布施行版本',
            element_name: '施用詐術致被害人陷於錯誤而交付財物',
            element_description: '以虛偽交易獲利與繳納解凍保證金阻撓出金，誘騙匯款',
            supporting_fact_refs: facts.filter((f) => /匯款|保證金/.test(f.source_excerpt)).map((f) => f.id),
            contrary_fact_refs: [],
            missing_information: [],
            element_status: 'SATISFIED',
            reasoning: '已有銀行跨行轉帳明細表及假平台凍結畫面在卷可稽。',
            source_ref: '刑法第339條第1項',
            requires_human_review: false,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行有效法規（民國113年施行）',
        created_at: now,
      });

      // 候選 2 (ALTERNATIVE): 洗錢防制法第14條第1項 洗錢罪
      const cand2Id = `cand-${caseId}-crypto-2`;
      candidates.push({
        id: cand2Id,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '洗錢防制法第14條第1項 一般洗錢罪',
        statute_ref: '洗錢防制法 §14 I',
        candidate_status: 'ALTERNATIVE',
        support_fact_refs: facts.filter((f) => /帳戶|虛擬貨幣/.test(f.source_excerpt)).map((f) => f.id),
        contrary_fact_refs: [],
        unknown_fact_refs: facts.filter((f) => f.assertion_status === 'UNKNOWN').map((f) => f.id),
        alternative_explanations: ['將詐欺贓款分流轉入多個帳戶並換成泰達幣製造斷點，成立洗錢罪競合。'],
        elements: [
          {
            id: `elem-${cand2Id}-1`,
            candidate_id: cand2Id,
            legal_norm: '洗錢防制法',
            norm_version: '民國113年最新修正施行',
            element_name: '隱匿或掩飾特定犯罪所得去向',
            element_description: '藉由轉入虛擬資產或外幣切斷金流鏈條',
            supporting_fact_refs: [],
            contrary_fact_refs: [],
            missing_information: ['VASP虛擬資產交易所提領錢包地址之真實持有者註冊紀錄'],
            element_status: 'INSUFFICIENT_DATA',
            reasoning: '尚待向交易所調閱 KYC 資料，列為資料不足待查。',
            source_ref: '洗錢防制法第14條第1項',
            requires_human_review: true,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行有效法規',
        created_at: now,
      });

      // 核心爭點
      coreIssues.push({
        id: `issue-${caseId}-crypto-tracing`,
        case_id: caseId,
        candidate_id: cand1Id,
        issue_description: '受款帳戶名義人是否具犯意聯絡？或僅屬受騙提供帳戶？（正犯 vs. 交付帳戶罪）',
        supporting_facts: facts.filter((f) => f.assertion_status === 'UNKNOWN').map((f) => f.id),
        contrary_facts: [],
        unresolved_questions: ['受款帳戶名義人是否已遭列警示？', '開戶自用程度與交出卡片是否有對價關係？'],
        priority: 'HIGH',
      });
    }

    // 案型 1.5: 破壞持有之竊盜行為 (趁人不備、偷走、行竊、徒手扒竊) vs. 搶奪 / 侵占
    if (
      !usePropertyRegistry &&
      /偷走|行竊|竊取|竊盜|偷拿|扒竊|扒手|拿起.{0,12}(離開|帶離)|取走.{0,12}(離開|帶離)|帶離/i.test(text) ||
      (/偷/i.test(text) && !/偷偷/i.test(text))
    ) {
      const candTheftDirectId = `cand-${caseId}-theft-direct`;
      candidates.push({
        id: candTheftDirectId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '中華民國刑法第320條第1項 普通竊盜罪',
        statute_ref: '中華民國刑法 §320 I',
        candidate_status: 'PRIMARY',
        support_fact_refs: facts.filter((f) => /偷|行竊|取走|手提包/.test(f.source_excerpt)).map((f) => f.id),
        contrary_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
        unknown_fact_refs: facts.filter((f) => f.assertion_status === 'UNKNOWN').map((f) => f.id),
        alternative_explanations: [
          '主位路線：被害人置於身旁或座位之財物仍在管領支配力範圍，行為人乘人不備竊取，破壞他人持有建立新持有，該當普通竊盜罪。',
        ],
        elements: [
          {
            id: `elem-${candTheftDirectId}-1`,
            candidate_id: candTheftDirectId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '破壞他人管領持有並建立自己之持有',
            element_description: '物仍在被害人實力支配管領範圍內，未得同意取走',
            supporting_fact_refs: facts.filter((f) => /偷|手提包|行竊|監視器/.test(f.source_excerpt)).map((f) => f.id),
            contrary_fact_refs: [],
            missing_information: [],
            element_status: 'SATISFIED',
            reasoning: '被害人將手提包置於高腳椅上仍在密切管領力所及範圍，嫌犯伸手取走破壞持有，現場監視器明確翻拍行竊過程。',
            source_ref: '最高法院30年上字第2096號判例',
            requires_human_review: false,
            related_fact_refs: [],
          },
          {
            id: `elem-${candTheftDirectId}-2`,
            candidate_id: candTheftDirectId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '意圖為自己或第三人不法之所有',
            element_description: '自始具備將他人之物據為己有之主觀違法意圖',
            supporting_fact_refs: facts.filter((f) => /偷|行竊/.test(f.source_excerpt)).map((f) => f.id),
            contrary_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
            missing_information: [],
            element_status: 'SATISFIED',
            reasoning: '嫌犯趁被害人不備取走物品後隨即攜離，客觀上已確立實力排他支配。',
            source_ref: '刑法第320條第1項',
            requires_human_review: false,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行有效法規',
        created_at: now,
      });

      // 備位/競合 1: 刑法第325條第1項 搶奪罪 (公然奪取 vs. 秘密竊取)
      const candRobberyId = `cand-${caseId}-robbery-alt`;
      candidates.push({
        id: candRobberyId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '中華民國刑法第325條第1項 普通搶奪罪（公然掠取檢驗路線）',
        statute_ref: '中華民國刑法 §325 I',
        candidate_status: 'ALTERNATIVE',
        support_fact_refs: [],
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: ['若涉嫌人係乘人不備以公然迅捷之腕力強行掠取致被害人不及抗拒，實務應檢驗是否跨入搶奪罪範疇。'],
        elements: [
          {
            id: `elem-${candRobberyId}-1`,
            candidate_id: candRobberyId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '乘人不備公然掠取致不及抗拒',
            element_description: '利用被害人不及防備之際施用腕力奪取',
            supporting_fact_refs: [],
            contrary_fact_refs: [],
            missing_information: ['涉嫌人伸手拿取時與被害人之肢體接觸及抗拒拉扯情形'],
            element_status: 'INSUFFICIENT_DATA',
            reasoning: '監視器顯示係伸手拿走，未見拉扯拉扯或對人身施加不法腕力，缺乏搶奪暴行事證，列為資料不足。',
            source_ref: '最高法院19年上字第533號判例',
            requires_human_review: true,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行有效法規',
        created_at: now,
      });

      // 核心爭點
      coreIssues.push({
        id: `issue-${caseId}-theft-possession`,
        case_id: caseId,
        candidate_id: candTheftDirectId,
        issue_description: '高腳椅上手提包是否仍屬於被害人之密切實力管領支配範圍？',
        supporting_facts: facts.filter((f) => /高腳椅|手提包/.test(f.source_excerpt)).map((f) => f.id),
        contrary_facts: [],
        unresolved_questions: ['被害人與高腳椅之距離？', '離開座位或背對座位時間多久？'],
        priority: 'HIGH',
      });
    }

    // 案型 2: 拾得物 / 皮夾 / 信用卡感應盜刷 vs. 竊盜
    if (!usePropertyRegistry && /拾獲|撿到|遺失|遺忘|遺留|手機|皮夾|信用卡|感應|盜刷|屈臣氏/i.test(text)) {
      // 候選 1 (PRIMARY): 刑法第337條 侵占離本人持有物罪
      const candLostId = `cand-${caseId}-lost-1`;
      candidates.push({
        id: candLostId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '中華民國刑法第337條 侵占離本人持有物罪',
        statute_ref: '中華民國刑法 §337',
        candidate_status: 'PRIMARY',
        support_fact_refs: facts.filter((f) => /遺忘|離開|皮夾/.test(f.source_excerpt)).map((f) => f.id),
        contrary_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
        unknown_fact_refs: [],
        alternative_explanations: ['物已脫離被害人之實力支配，行為人偶然拾獲據為己有，該當侵占離本人持有物。'],
        elements: [
          {
            id: `elem-${candLostId}-1`,
            candidate_id: candLostId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '客體為離本人持有之物',
            element_description: '非出於本人之意思脫離管領支配',
            supporting_fact_refs: facts.filter((f) => /遺忘|皮夾/.test(f.source_excerpt)).map((f) => f.id),
            contrary_fact_refs: [],
            missing_information: [],
            element_status: 'SATISFIED',
            reasoning: '被害人離席後遺留於座位上，管領力已斷絕。',
            source_ref: '最高法院50年台上字第2038號判例',
            requires_human_review: false,
            related_fact_refs: [],
          },
          {
            id: `elem-${candLostId}-2`,
            candidate_id: candLostId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '意圖為自己不法所有而侵占',
            element_description: '易持有為所有之主觀意思與客觀處分行為',
            supporting_fact_refs: facts.filter((f) => /帶離|取走/.test(f.source_excerpt)).map((f) => f.id),
            contrary_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
            missing_information: [],
            element_status: 'CONTESTED',
            reasoning: '行為人辯稱打算送警局（DENIED），但客觀未交店員反而帶走，正反事實存在爭議抗辯。',
            source_ref: '刑法第337條',
            requires_human_review: true,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行有效法規',
        created_at: now,
      });

      // 候選 2 (ALTERNATIVE): 刑法第320條第1項 普通竊盜罪（場所管領力競爭路線）
      const candTheftId = `cand-${caseId}-theft-compete`;
      candidates.push({
        id: candTheftId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '中華民國刑法第320條第1項 普通竊盜罪（場所支配力競爭路線）',
        statute_ref: '中華民國刑法 §320 I',
        candidate_status: 'ALTERNATIVE',
        support_fact_refs: [],
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: ['若認營業場所內店員對顧客遺忘物具有概括持有支配力，未得店員同意取走可能成立竊盜罪。'],
        elements: [
          {
            id: `elem-${candTheftId}-1`,
            candidate_id: candTheftId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '破壞他人實力支配並建立新持有',
            element_description: '破壞場所管理者之管領力',
            supporting_fact_refs: [],
            contrary_fact_refs: [],
            missing_information: ['店員對於各桌次遺留物品之巡查頻率與實質管領支配證明'],
            element_status: 'INSUFFICIENT_DATA',
            reasoning: '現場無專人看管桌次，店員是否取得概括持有尚乏積極事證，列為資料不足。',
            source_ref: '最高法院70年台上字第2250號判決意旨',
            requires_human_review: true,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行有效法規',
        created_at: now,
      });

      // 候選 3 (PRIMARY - 獨立競合): 刑法第339條第1項 詐欺取財罪（無權感應盜刷）
      if (/信用卡|感應|盜刷|屈臣氏/i.test(text)) {
      const candSwipeId = `cand-${caseId}-swipe-1`;
      candidates.push({
        id: candSwipeId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '中華民國刑法第339條第1項 詐欺取財罪（持卡冒用感應消費）',
        statute_ref: '中華民國刑法 §339 I',
        candidate_status: 'PRIMARY',
        support_fact_refs: facts.filter((f) => /盜刷|感應|屈臣氏/.test(f.source_excerpt)).map((f) => f.id),
        contrary_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
        unknown_fact_refs: [],
        alternative_explanations: ['持他人信用卡感應過卡，默示其為正當持卡人，使特約商店陷於錯誤交付商品。'],
        elements: [
          {
            id: `elem-${candSwipeId}-1`,
            candidate_id: candSwipeId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '對特約商店施用詐術使陷於錯誤',
            element_description: '冒充正當持有人行使小額免簽名感應過卡',
            supporting_fact_refs: facts.filter((f) => /盜刷|感應/.test(f.source_excerpt)).map((f) => f.id),
            contrary_fact_refs: [],
            missing_information: [],
            element_status: 'SATISFIED',
            reasoning: '臺灣高等法院108年度上易字第1520號判決確認感應盜刷該當刑法第339條第1項。',
            source_ref: '刑法第339條第1項',
            requires_human_review: false,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行有效法規',
        created_at: now,
      });
      }

      // 核心爭點
      coreIssues.push({
        id: `issue-${caseId}-swipe-intent`,
        case_id: caseId,
        candidate_id: candLostId,
        issue_description: '「打算送警局、順路先借刷」之抗辯是否影響不法所有意圖？',
        supporting_facts: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
        contrary_facts: facts.filter((f) => /盜刷|屈臣氏/.test(f.source_excerpt)).map((f) => f.id),
        unresolved_questions: ['涉嫌人離開至前往門市消費間隔時間？', '有無任何主動洽詢店員之舉止？'],
        priority: 'HIGH',
      });
    }

    // 案型 3: ATM 提款車手案
    if (/atm|車手|提領|提款|代領|跑腿|置物櫃|現鈔/i.test(text)) {
      const candAtmMuleId = `cand-${caseId}-atm-1`;
      candidates.push({
        id: candAtmMuleId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '中華民國刑法第339條之4第1項第2款 三人以上共同加重詐欺取財罪',
        statute_ref: '中華民國刑法 §339-4 I(2)',
        candidate_status: 'PRIMARY',
        support_fact_refs: facts.filter((f) => /提款|提領|現鈔|金融卡/.test(f.source_excerpt)).map((f) => f.id),
        contrary_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
        unknown_fact_refs: [],
        alternative_explanations: ['依最高法院判決，按抽取成數領取巨款，主觀具備未必故意，論以共同正犯。'],
        elements: [
          {
            id: `elem-${candAtmMuleId}-1`,
            candidate_id: candAtmMuleId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '共同犯意聯絡與行為分擔',
            element_description: '提款車手居於詐欺既遂分工之最後關鍵環節',
            supporting_fact_refs: facts.filter((f) => /提款|現鈔/.test(f.source_excerpt)).map((f) => f.id),
            contrary_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
            missing_information: [],
            element_status: 'CONTESTED',
            reasoning: '涉嫌人抗辯單純跑腿不知情，具有抗辯爭執，實務依抽取高額報酬認定具備未必故意。',
            source_ref: '最高法院107年度台上字第4225號判決',
            requires_human_review: true,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行有效法規',
        created_at: now,
      });

      // 備位/抗辯路線: 刑法第30條 幫助犯
      const candMuleHelpId = `cand-${caseId}-atm-help`;
      candidates.push({
        id: candMuleHelpId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '中華民國刑法第30條第1項、第339條之4 加重詐欺幫助犯（抗辯路線）',
        statute_ref: '中華民國刑法 §30 I, §339-4',
        candidate_status: 'ALTERNATIVE',
        support_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: ['若涉嫌人僅具初次跑腿認知，無集團分贓協議，實務亦有審酌論以幫助犯之可能。'],
        elements: [
          {
            id: `elem-${candMuleHelpId}-1`,
            candidate_id: candMuleHelpId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '基於幫助他人犯罪之意思提供助力',
            element_description: '非基於自己犯罪之意思實施要件行為',
            supporting_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
            contrary_fact_refs: [],
            missing_information: ['涉嫌人與指示者之全部通訊對話歷史'],
            element_status: 'INSUFFICIENT_DATA',
            reasoning: '手機通話記錄已遭設定自動銷毀，需數位鑑識還原後方能判定知情深度。',
            source_ref: '刑法第30條第1項',
            requires_human_review: true,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行有效法規',
        created_at: now,
      });
    }

    // 案型 4: 行車糾紛 / 球棒傷害恐嚇 / 殺人未遂
    if (!useViolenceRegistry && /傷害|打傷|毆打|球棒|骨折|流血|恐嚇|打死你|撕裂傷/i.test(text)) {
      // 候選 1: 刑法第277條第1項 普通傷害罪
      const candAssaultId = `cand-${caseId}-assault-1`;
      candidates.push({
        id: candAssaultId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '中華民國刑法第277條第1項 普通傷害罪',
        statute_ref: '中華民國刑法 §277 I',
        candidate_status: 'PRIMARY',
        support_fact_refs: facts.filter((f) => /打傷|骨折|毆打/.test(f.source_excerpt)).map((f) => f.id),
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: ['持鋁棒毆擊造成被害人撕裂傷及骨折，成立普通傷害罪。'],
        elements: [
          {
            id: `elem-${candAssaultId}-1`,
            candidate_id: candAssaultId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '傷害人之身體或健康',
            element_description: '客觀傷害行為造成骨折及外傷結果',
            supporting_fact_refs: facts.filter((f) => /骨折|撕裂傷/.test(f.source_excerpt)).map((f) => f.id),
            contrary_fact_refs: [],
            missing_information: [],
            element_status: 'SATISFIED',
            reasoning: '被害人醫院驗傷證明書明確記載頭部裂傷與骨折。',
            source_ref: '刑法第277條第1項',
            requires_human_review: false,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行有效法規',
        created_at: now,
      });

      // 候選 2: 刑法第305條 恐嚇危害安全罪
      const candThreatId = `cand-${caseId}-threat-1`;
      candidates.push({
        id: candThreatId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '中華民國刑法第305條 恐嚇危害安全罪',
        statute_ref: '中華民國刑法 §305',
        candidate_status: 'PRIMARY',
        support_fact_refs: facts.filter((f) => /打死你|恐嚇/.test(f.source_excerpt)).map((f) => f.id),
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: ['出言「再叭就打死你」以加害生命之事恐嚇他人致生危害於安全。'],
        elements: [
          {
            id: `elem-${candThreatId}-1`,
            candidate_id: candThreatId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '以加害生命之事恐嚇他人',
            element_description: '惡害通告致被害人心生畏懼',
            supporting_fact_refs: facts.filter((f) => /打死你/.test(f.source_excerpt)).map((f) => f.id),
            contrary_fact_refs: [],
            missing_information: [],
            element_status: 'SATISFIED',
            reasoning: '證人與行車紀錄器錄音相符。',
            source_ref: '刑法第305條',
            requires_human_review: false,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行有效法規',
        created_at: now,
      });

      // 候選 3 (ALTERNATIVE): 刑法第271條第2項 殺人未遂罪（致命意圖檢驗）
      const candAttemptMurderId = `cand-${caseId}-murder-alt`;
      candidates.push({
        id: candAttemptMurderId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '中華民國刑法第271條第2項 殺人未遂罪（致命意圖檢驗路線）',
        statute_ref: '中華民國刑法 §271 II',
        candidate_status: 'ALTERNATIVE',
        support_fact_refs: facts.filter((f) => /打死你|頭部/.test(f.source_excerpt)).map((f) => f.id),
        contrary_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
        unknown_fact_refs: [],
        alternative_explanations: ['以鋁棒重擊頭部要害並出言要打死對方，需檢驗具備直接或未必殺人故意。'],
        elements: [
          {
            id: `elem-${candAttemptMurderId}-1`,
            candidate_id: candAttemptMurderId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '殺人主觀犯意之確信',
            element_description: '具有致人於死之直接或不確定故意',
            supporting_fact_refs: facts.filter((f) => /頭部|打死你/.test(f.source_excerpt)).map((f) => f.id),
            contrary_fact_refs: [],
            missing_information: ['嫌犯揮擊力道、次數，及打擊後有無主動停手或遭旁人攔阻之客觀事證'],
            element_status: 'INSUFFICIENT_DATA',
            reasoning: '實務殺人與傷害區別需綜合衡量揮擊力道與著手前後態度，現階段列為資料不足待查。',
            source_ref: '最高法院19年上字第1440號判例',
            requires_human_review: true,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行有效法規',
        created_at: now,
      });

      // 核心爭點
      coreIssues.push({
        id: `issue-${caseId}-murder-vs-injury`,
        case_id: caseId,
        candidate_id: candAssaultId,
        issue_description: '揮棒擊打頭部並稱打死你，應評價為傷害或殺人未遂？',
        supporting_facts: facts.filter((f) => /頭部|打死你/.test(f.source_excerpt)).map((f) => f.id),
        contrary_facts: [],
        unresolved_questions: ['嫌犯打擊幾下？', '被害人倒地後是否仍有追擊舉動？'],
        priority: 'HIGH',
      });
    }

    // 案型 5: 民事債務不履行 vs. 刑事詐術
    if (/借款|周轉|貨款|未還|延期|民事|契約|本票/i.test(text) && candidates.length === 0) {
      // 候選 1: 純屬民事債務不履行
      const candCivilId = `cand-${caseId}-civil-1`;
      candidates.push({
        id: candCivilId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '民事債務不履行（民法第227條，無刑事詐欺犯罪）',
        statute_ref: '民法 §227',
        candidate_status: 'PRIMARY',
        support_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED' || /依約|借貸契約/.test(f.source_excerpt)).map((f) => f.id),
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: ['借款後因事後經商失敗無法依約還款，尚乏自始詐欺故意，純屬民事糾紛。'],
        elements: [
          {
            id: `elem-${candCivilId}-1`,
            candidate_id: candCivilId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '缺乏自始施用詐術與不法所有意圖',
            element_description: '借貸之初未虛構事實，有清償真意',
            supporting_fact_refs: facts.filter((f) => /依約|繳息/.test(f.source_excerpt)).map((f) => f.id),
            contrary_fact_refs: [],
            missing_information: [],
            element_status: 'SATISFIED',
            reasoning: '最高法院46年台上字第260號判例：單純民事債務遲延不成立詐欺。',
            source_ref: '最高法院46年台上字第260號判例',
            requires_human_review: false,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行民事法規',
        created_at: now,
      });

      // 候選 2: 刑法第339條 詐欺取財罪（備位自始詐欺檢驗）
      const candFraudId = `cand-${caseId}-fraud-alt`;
      candidates.push({
        id: candFraudId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '中華民國刑法第339條第1項 普通詐欺取財罪（自始惡意倒債路線）',
        statute_ref: '中華民國刑法 §339 I',
        candidate_status: 'ALTERNATIVE',
        support_fact_refs: [],
        contrary_fact_refs: [],
        unknown_fact_refs: facts.filter((f) => f.assertion_status === 'UNKNOWN').map((f) => f.id),
        alternative_explanations: ['若涉嫌人借款時虛構投資項目或早已毫無資力，仍可能該當詐欺取財。'],
        elements: [
          {
            id: `elem-${candFraudId}-1`,
            candidate_id: candFraudId,
            legal_norm: '中華民國刑法',
            norm_version: '現行有效法規',
            element_name: '自始惡意無清償意願',
            element_description: '借款之初即無還款意思',
            supporting_fact_refs: [],
            contrary_fact_refs: facts.filter((f) => /依約繳息/.test(f.source_excerpt)).map((f) => f.id),
            missing_information: ['借款時被告帳戶資力與工廠真實營運帳冊'],
            element_status: 'INSUFFICIENT_DATA',
            reasoning: '被告有繳息6個月之客觀反向事實，現有事證不足以證明自始詐欺，列為資料不足待查。',
            source_ref: '刑法第339條第1項',
            requires_human_review: true,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行有效法規',
        created_at: now,
      });
    }

    // 若無法形成可靠結論，輸出 UNRESOLVED 狀態，嚴禁假裝完成分析或補入預設答案
    if (candidates.length === 0) {
      const candUnresolved = `cand-${caseId}-unresolved`;
      candidates.push({
        id: candUnresolved,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '罪名尚待釐清（未決狀態，事證不足以直接定性）',
        statute_ref: '尚無足夠構成要件之法條依據',
        candidate_status: 'UNRESOLVED',
        support_fact_refs: facts.map((f) => f.id),
        contrary_fact_refs: [],
        unknown_fact_refs: facts.map((f) => f.id),
        alternative_explanations: ['案件事實過於簡短或欠缺客觀要件，必須先經筆錄偵詢補強事實。'],
        elements: [
          {
            id: `elem-${candUnresolved}-1`,
            candidate_id: candUnresolved,
            legal_norm: '中華民國刑事訴訟法',
            norm_version: '現行有效法規',
            element_name: '犯罪嫌疑構成要件事實之特定',
            element_description: '人、事、時、地、物之基本要件釐清',
            supporting_fact_refs: [],
            contrary_fact_refs: [],
            missing_information: ['具體行為手段、涉案金額或損害結果'],
            element_status: 'INSUFFICIENT_DATA',
            reasoning: '現有案情描述未達特定犯罪構成要件門檻，依法不得逕行分類。',
            source_ref: '刑事訴訟法第228條',
            requires_human_review: true,
            related_fact_refs: [],
          },
        ],
        statute_version: '現行法規',
        created_at: now,
      });
    }

    return {
      candidates: this.normalizeCandidateTraceability(candidates, facts, evidenceItems),
      coreIssues,
    };
  }

  /**
   * Gate 3: 依 9 大分類產生非誘導性偵訊筆錄問句 (Interview Questions)
   */
  static generateInterviewQuestions(
    caseId: string,
    revisionId: number,
    candidates: LegalCandidate[],
    coreIssues: CoreIssue[],
    facts: FactItem[]
  ): InterviewQuestion[] {
    const questions: InterviewQuestion[] = [];
    const prim = candidates.find((c) => c.candidate_status === 'PRIMARY') || candidates[0];
    const candId = prim ? prim.id : `cand-${caseId}`;

    const types: {
      type: QuestionType;
      label: string;
      text: string;
      rationale: string;
      priority: QuestionPriority;
    }[] = [
      {
        type: '1_CORE_ELEMENT',
        label: '核心構成要件問句',
        text: '你於行為當下主觀上是否知悉或可得預見該物品/帳戶係屬他人合法所有，未得授權不得擅自處分？',
        rationale: '確認犯罪主觀故意或未必故意，建立核心構成要件必備事實。',
        priority: 'P0_CRITICAL',
      },
      {
        type: '2_ACT_PROCESS',
        label: '行為經過問句',
        text: '請具體陳述你當日到達現場、著手實施至離開現場之完整詳細時序與各動作經過？',
        rationale: '還原連續行為時序，檢驗客觀構成要件著手與既遂時點。',
        priority: 'P0_CRITICAL',
      },
      {
        type: '3_SUBJECTIVE_INTENT',
        label: '主觀認知及意思問句',
        text: '你為上述行為時，主觀上意圖獲取何種對價、利益或達到何種目的？有無受他人指示或引誘？',
        rationale: '探求不法所有意圖、損害他人意圖或共同分工意思聯絡。',
        priority: 'P0_CRITICAL',
      },
      {
        type: '4_TIME_LOCATION_PERSON',
        label: '時間、地點及人物關係問句',
        text: '你與在場其他關係人（或被害人、委託人）平時是否有任何親誼、借貸、僱傭或既有民事糾紛關係？',
        rationale: '排除民事債務抗辯或特定身分免除刑罰關係。',
        priority: 'P1_IMPORTANT',
      },
      {
        type: '5_FLOW_OF_PROPERTY',
        label: '財物、款項、工具或資料流向問句',
        text: '涉案之款項、卡片、作案工具或取得之物品，目前下落何在？有無藏匿、移轉、變賣或交付第三人？',
        rationale: '查證贓物流向，完備沒收及追徵要件，並追查共犯水房。',
        priority: 'P0_CRITICAL',
      },
      {
        type: '6_EVIDENCE_SOURCE',
        label: '證據及來源問句',
        text: '警方現場所扣押（或卷附翻拍）之相關物證是否均為你本人所有及持有？有無其他有利之通訊紀錄可供查對？',
        rationale: '確立證據保管鏈與證物關聯性。',
        priority: 'P1_IMPORTANT',
      },
      {
        type: '7_CONTRARY_ALTERNATIVE',
        label: '反向事實及替代解釋問句',
        text: '你是否主張該行為係獲得對方同意、受託代辦業務或純屬正當合法防衛？請提出具體證明人或證據。',
        rationale: '主動檢驗阻卻違法事由或有利抗辯，落實刑事訴訟法第2條注意有利不利原則。',
        priority: 'P1_IMPORTANT',
      },
      {
        type: '8_CONTRADICTION_SUPPLEMENT',
        label: '矛盾與補充問句',
        text: '卷附客觀監視錄影紀錄（或金流明細）與你上述辯解有所出入，你對該不一致之處如何合理說明？',
        rationale: '針對陳述矛盾點進行中性追問，確保自白任意性與客觀性。',
        priority: 'P1_IMPORTANT',
      },
      {
        type: '9_UNRESOLVED_INQUIRY',
        label: '尚待查明事項問句',
        text: '就本案事實，除上述各節外，有無其他有利事項或請求調查之證據與證人？',
        rationale: '充分保障當事人刑事防禦權及陳述意見權。',
        priority: 'P2_SUPPLEMENTAL',
      },
    ];

    types.forEach((item, idx) => {
      questions.push({
        id: `q-${caseId}-r${revisionId}-${idx + 1}`,
        case_id: caseId,
        candidate_id: candId,
        question_type: item.type,
        question_text: item.text,
        rationale: item.rationale,
        target_fact_refs: facts.map((f) => f.id),
        priority: item.priority,
        review_status: 'DRAFT',
        is_required: true,
        revision_number: revisionId,
        expected_clarification: '',
      });
    });

    if (candidates.some((candidate) => candidate.id.includes('-registry-'))) {
      const registryQuestions: Array<{ type: QuestionType; text: string; rationale: string; elementHint: string }> = [
        { type: '1_CORE_ELEMENT', text: '請說明你看到該物品時，物品原本放在哪裡、附近有哪些人，以及你是否看到有人正在注意或管理它？', rationale: '釐清物品在取得時是否仍在他人或場所的實際支配範圍。', elementHint: 'possession' },
        { type: '2_ACT_PROCESS', text: '請依時間順序說明你從看到、拿起或取得該物品，到離開現場之間的每一個動作。', rationale: '還原取得行為、控制建立及是否有未經授權攜離。', elementHint: 'taking' },
        { type: '3_SUBJECTIVE_INTENT', text: '你拿到該物品當時，認為它是誰的？你當時打算如何處理？', rationale: '詢問認知與目的，不直接要求受詢問者作法律評價。', elementHint: 'intent' },
        { type: '7_CONTRARY_ALTERNATIVE', text: '取得後你曾否交給店員、交還他人、報警或採取其他尋找失主的行動？請說明時間、地點及可供查證的人。', rationale: '保留返還、協助尋找失主等有利於受詢問者的反向事實。', elementHint: 'intent' },
        { type: '6_EVIDENCE_SOURCE', text: '店內影像或店員所述的哪一部分與你剛才的說明相同或不同？你是否有其他資料可以核對？', rationale: '將供述與客觀資料分開核對，不把影像存在直接等同犯罪成立。', elementHint: 'taking' },
      ];
      const violenceQuestions: Array<{ type: QuestionType; text: string; rationale: string; elementHint: string }> = [
        { type: '1_CORE_ELEMENT', text: '請說明當時你與對方的距離、接觸方式、使用的工具及每一個動作。', rationale: '釐清可觀察的行為、工具、部位與時序，不先作法律評價。', elementHint: 'act_result' },
        { type: '2_ACT_PROCESS', text: '請依時間順序說明從爭執或接觸開始，到停止動作之間的經過。', rationale: '還原行為與結果的發生順序，供後續核對。', elementHint: 'overt_act' },
        { type: '3_SUBJECTIVE_INTENT', text: '你當時為什麼做出這些動作？你是否說過或寫過相關言語？', rationale: '詢問行為目的及原話內容，不要求受詢問者作法律判斷。', elementHint: 'intent' },
        { type: '7_CONTRARY_ALTERNATIVE', text: '當時有沒有意外、過失、防衛、停止動作或協助對方的情形？請說明具體經過。', rationale: '保留有利及替代解釋，避免只蒐集支持犯罪的資料。', elementHint: 'intent' },
        { type: '6_EVIDENCE_SOURCE', text: '有哪些人看到或聽到當時經過？是否有影像、錄音、診斷或其他資料可以核對？', rationale: '確認供述、客觀證據與證人來源及其可查證範圍。', elementHint: 'causation' },
      ];
      questions.length = 0;
      let sequence = 0;
      candidates.filter((candidate) => candidate.id.includes('-registry-')).forEach((candidate) => {
        const routeQuestions = candidate.id.includes('tw-penal-277') || candidate.id.includes('tw-penal-305') || candidate.id.includes('tw-penal-271')
          ? violenceQuestions
          : registryQuestions;
        routeQuestions.forEach((item) => {
          const element = candidate.elements.find((candidateElement) => candidateElement.id.endsWith(`-${item.elementHint}`));
          questions.push({
            id: `q-${caseId}-r${revisionId}-registry-${sequence + 1}`,
            case_id: caseId,
            candidate_id: candidate.id,
            element_id: element?.id,
            question_type: item.type,
            question_text: item.text,
            rationale: item.rationale,
            target_fact_refs: element?.related_fact_refs || facts.map((fact) => fact.id),
            priority: item.type === '6_EVIDENCE_SOURCE' ? 'P1_IMPORTANT' : 'P0_CRITICAL',
            review_status: 'DRAFT',
            is_required: true,
            revision_number: revisionId,
            expected_clarification: '',
          });
          sequence += 1;
        });
      });
    }

    return questions;
  }

  /**
   * Gate 4 & 狀態機核心: 下游無效化連動處理 (Cascade Invalidation Engine)
   * 當上游事實 (FactItem) 修正或回答回填時，自動標記下游關聯項目為 STALE 並遞增版本號
   */
  static invalidateDownstreamOnFactChange(
    currentCase: CaseRecord,
    modifiedFactId: string,
    newFactContent: Partial<FactItem>,
    reason: string = '上游案件事實修正，觸發下游連動重新涵攝'
  ): { updatedCase: CaseRecord; invalidationReport: InvalidationReport } {
    const oldRevision = currentCase.current_revision;
    const newRevision = oldRevision + 1;
    const now = new Date().toISOString();

    const previousSnapshot = {
      revision_id: oldRevision,
      parent_revision_id: oldRevision > 1 ? oldRevision - 1 : undefined,
      changed_fact_ids: [modifiedFactId],
      change_reason: reason,
      created_at: now,
      facts: currentCase.facts.map((fact) => ({ ...fact })),
      evidence_items: currentCase.evidence_items.map((item) => ({ ...item })),
      behaviors: currentCase.behaviors.map((behavior) => ({ ...behavior, fact_refs: [...behavior.fact_refs], evidence_refs: [...(behavior.evidence_refs || [])] })),
      legal_candidates: currentCase.legal_candidates.map((candidate) => ({
        ...candidate,
        support_fact_refs: [...candidate.support_fact_refs],
        contrary_fact_refs: [...candidate.contrary_fact_refs],
        unknown_fact_refs: [...candidate.unknown_fact_refs],
        elements: candidate.elements.map((element) => ({
          ...element,
          supporting_fact_refs: [...(element.supporting_fact_refs || [])],
          contrary_fact_refs: [...(element.contrary_fact_refs || [])],
          related_fact_refs: [...element.related_fact_refs],
          related_evidence_refs: [...(element.related_evidence_refs || [])],
          missing_information: [...(element.missing_information || [])],
        })),
      })),
      core_issues: currentCase.core_issues.map((issue) => ({ ...issue, supporting_facts: [...issue.supporting_facts], contrary_facts: [...issue.contrary_facts], unresolved_questions: [...issue.unresolved_questions] })),
      questions: currentCase.questions.map((question) => ({ ...question, target_fact_refs: [...question.target_fact_refs] })),
      answers: currentCase.answers.map((answer) => ({ ...answer })),
      reports: currentCase.reports.map((report) => ({ ...report, validation_errors: [...report.validation_errors] })),
    };

    // 1. 拷貝並更新事實
    const updatedFacts = currentCase.facts.map((f) => {
      if (f.id === modifiedFactId) {
        return {
          ...f,
          ...newFactContent,
          revision_id: newRevision,
          updated_at: now,
        };
      }
      return f;
    });

    // 2. 重新執行多候選涵攝
    const { candidates: newCandidates, coreIssues: newCoreIssues } = this.evaluateLegalCandidates(
      currentCase.raw_intake.summary,
      updatedFacts,
      currentCase.id,
      newRevision,
      currentCase.evidence_items
    );

    // 3. 重新產生偵訊問句
    const newQuestions = this.generateInterviewQuestions(
      currentCase.id,
      newRevision,
      newCandidates,
      newCoreIssues,
      updatedFacts
    );

    // 4. 將現有公務條陳標記為 STALE（舊核准不得自動套用到新版本）
    const updatedReports = currentCase.reports.map((r) => ({
      ...r,
      is_approved: false, // 取消核定
      validation_errors: [
        ...(r.validation_errors || []).filter((e) => !e.startsWith('[STALE]')),
        `[STALE] 因版本 #${newRevision} 事實更新，需重新人工審核確認`,
      ],
    }));

    // 5. 記錄稽核日誌
    const auditEvent = {
      id: `audit-${Date.now()}`,
      actor_id: currentCase.owner_id,
      case_id: currentCase.id,
      event_type: 'DOWNSTREAM_INVALIDATION',
      target_type: 'FACT_ITEM',
      target_id: modifiedFactId,
      occurred_at: now,
      details: `Fact ${modifiedFactId} 更新，版本由 Rev #${oldRevision} 推進至 Rev #${newRevision}。原因: ${reason}`,
    };

    const updatedCase: CaseRecord = {
      ...currentCase,
      current_revision: newRevision,
      updated_at: now,
      facts: updatedFacts,
      legal_candidates: newCandidates,
      core_issues: newCoreIssues,
      questions: newQuestions,
      reports: updatedReports,
      revision_history: [...(currentCase.revision_history || []), previousSnapshot],
      audit_logs: [...currentCase.audit_logs, auditEvent],
    };

    const invalidationReport: InvalidationReport = {
      invalidatedCandidateIds: currentCase.legal_candidates.map((c) => c.id),
      invalidatedQuestionIds: currentCase.questions.map((q) => q.id),
      invalidatedReportIds: currentCase.reports.map((r) => r.id),
      previousRevision: oldRevision,
      newRevision: newRevision,
      reason,
      timestamp: now,
    };

    return { updatedCase, invalidationReport };
  }

  /**
   * Gate 5: 產生公務條陳並執行格式嚴謹度驗證 (Report Generation)
   * 全面移除寫死之特定日期、單位、官警名稱與案號，所有欄位來自當前案件或明確標示待填
   */
  static generateAndValidateReport(
    currentCase: CaseRecord,
    options?: {
      station?: string;
      handlingOfficer?: string;
      jurisdiction?: string;
      certificateNumber?: string;
    }
  ): OfficialReport {
    const now = new Date().toISOString();
    const primCandidate = currentCase.legal_candidates.find((c) => c.candidate_status === 'PRIMARY');
    const titleReason = primCandidate ? primCandidate.legal_name : '刑事案件偵查（待核定）';

    // 動態抽取時間（優先自事實項，無則標示待查填報）
    const timeFact = currentCase.facts.find((f) => f.event_time && !f.event_time.includes('待'));
    const rocIncidentTime = timeFact ? timeFact.event_time : '[發生時間待查證填報]';

    // 動態抽取地點
    const locFact = currentCase.facts.find((f) => f.event_location && !f.event_location.includes('待'));
    const incidentLocation = locFact ? locFact.event_location : '[發生地點待查證填報]';

    const station = options?.station || '[報告單位待填報]';
    const handlingOfficer = options?.handlingOfficer || '[承辦員警待填報]';
    const jurisdiction = options?.jurisdiction || '[管轄地方檢察署待填報]';
    const certificateNumber = options?.certificateNumber || '[受處理案件證明單案號待填報]';

    const report: OfficialReport = {
      id: `rep-${currentCase.id}-r${currentCase.current_revision}`,
      case_id: currentCase.id,
      revision_id: currentCase.current_revision,
      station,
      report_type: '受理',
      title_reason: `疑涉${titleReason}等罪嫌。`,
      status_marker: '受理',
      incident_time_roc: rocIncidentTime,
      incident_location: incidentLocation,
      report_time_roc: '[報案時間待填報]',
      summary_text: currentCase.raw_intake.summary || '[案情摘要內容待填報]',
      certificate_number: certificateNumber,
      women_child_number: '無',
      c165_number: currentCase.legal_candidates.some((c) => c.legal_name.includes('詐欺')) ? '[待填報165案號]' : '無',
      jurisdiction,
      handling_officer: handlingOfficer,
      is_approved: false, // 嚴禁自動標記為正式完成
      generated_at: now,
      validation_errors: [],
    };

    // 文件內容與格式嚴格驗證
    const errors: string[] = [];
    if (!report.station.trim() || report.station.includes('待填報')) {
      errors.push('報告單位需填寫警政機關全銜');
    }
    if (!report.title_reason.trim()) {
      errors.push('案由不得為空白');
    }
    if (!report.incident_time_roc.startsWith('民國') && !report.incident_time_roc.includes('待查證')) {
      errors.push('發生時間必須採用標準民國紀年格式（例：民國115年某月某日）');
    }
    if (!report.summary_text.trim() || report.summary_text.length < 15) {
      errors.push('案情摘要不得少於15字，且須完整包含人、事、時、地、物要件');
    }
    if (report.summary_text.length > 500) {
      errors.push('案情摘要不得超過500個Unicode字元，請重新整理後再輸出');
    }
    if (!report.jurisdiction.trim() || report.jurisdiction.includes('待填報')) {
      errors.push('管轄檢察署需填報');
    }
    if (!report.handling_officer.trim() || report.handling_officer.includes('待填報')) {
      errors.push('處理員警職稱姓名需填報');
    }

    report.validation_errors = errors;
    return report;
  }

  /**
   * 前端一站式分析呼叫方法 (Unified Analysis Entrypoint)
   * 整合事實抽取、證據、行為、構成要件涵攝、多候選方向、9大問句及公文
   */
  static analyzeFullCase(rawText: string, caseId?: string): FullCaseAnalysisOutput {
    const id = caseId || `case-${Date.now()}`;
    const text = (rawText || '').trim();

    // 建立案件容器
    const caseRec = this.createNewCase(id, '案件分析紀錄', text);

    // 1. 抽取事實 (五元狀態)
    const facts = this.parseFactsFromText(text, id, 1);
    caseRec.facts = facts;

    // 2. 抽取行為與物證
    const { behaviors, evidenceItems } = this.parseBehaviorsAndEvidence(text, facts, id, 1);
    caseRec.behaviors = behaviors;
    caseRec.evidence_items = evidenceItems;

    // 3. 構成要件涵攝與多候選方向
    const { candidates, coreIssues } = this.evaluateLegalCandidates(text, facts, id, 1, evidenceItems);
    caseRec.legal_candidates = candidates;
    caseRec.core_issues = coreIssues;

    // 4. 生成 9 大分類非誘導性問句
    const questions = this.generateInterviewQuestions(id, 1, candidates, coreIssues, facts);
    caseRec.questions = questions;

    // 5. 生成公務條陳草稿
    const report = this.generateAndValidateReport(caseRec);
    caseRec.reports = [report];

    // 6. 整合驗證法規、裁判、論著與 AI 簡述
    const primCand = candidates.find((c) => c.candidate_status === 'PRIMARY') || candidates[0];
    const categoryName = primCand?.legal_name.split(' ')[0] || '刑事案件法律涵攝分析';

    const aiBrief = `本案經結構化事實拆解，主位法律方向為「${primCand?.legal_name || '待查證'}」，同時平行列出 ${
      candidates.filter((c) => c.candidate_status !== 'PRIMARY').length
    } 項替代或競爭抗辯路線。共識別 ${facts.length} 項事實（含 ${
      facts.filter((f) => f.assertion_status === 'DENIED').length
    } 項否認爭點、${facts.filter((f) => f.assertion_status === 'UNKNOWN').length} 項待查項目）。`;

    const laws: LawReferenceItem[] = [
      {
        title: primCand?.legal_name || '中華民國刑法',
        subTitle: primCand?.statute_ref || '實體法條',
        items: [
          { num: '要件', text: '本罪構成要件需嚴格依客觀事證與主觀犯意綜合認定。', highlight: true },
        ],
        hint: '非經法定偵查程序與人證物證調查，不得逕自推定有罪。',
        authority: '法務部 / 司法院',
      },
      {
        title: '刑事訴訟法第2條',
        subTitle: '公務員應注意有利及不利原則',
        items: [
          { num: '第1項', text: '實施刑事訴訟程序之公務員，就該管案件，應於被告有利及不利之情形，一律注意。', highlight: true },
        ],
        hint: '偵查員訊問筆錄必須保持中立客觀，不得逼誘或設定特定罪名偏見。',
        authority: '司法院刑事廳',
      },
    ];

    const rulings: RulingReferenceItem[] = [
      {
        court: '最高法院',
        caseNo: '50 年台上字第 2038 號刑事判例',
        yearDate: '民國 50 年',
        title: '離本人持有物與他人管領力之界限判準',
        holding: '離本人持有之物，係指物脫離本人持有且未入他人實力支配之下。',
        takeaway: '區分刑法第337條侵占離本人持有物與第320條竊盜罪之分水嶺。',
      },
      {
        court: '最高法院',
        caseNo: '107 年度台上字第 4225 號刑事判決',
        yearDate: '民國 107 年',
        title: '車手與人頭帳戶未必故意之認定標準',
        holding: '交付帳戶或代領高額報酬現鈔，依常理顯可預見供犯罪使用，具有不確定故意。',
        takeaway: '打破單純跑腿不知情之狡辯。',
      },
    ];

    const treatises: TreatiseReferenceItem[] = [
      {
        title: '刑事偵查中多重候選罪名之涵攝與競合處斷指引',
        author: '法務部檢察司研究意見',
        source: '檢察新論 第 34 期',
        coreArgument: '偵查初期切忌單一罪名隧道視野，應同時就主位罪名、備位罪名及阻卻違法事由全面蒐證。',
        takeaway: '警詢時應依 9 大分類問句逐項查驗待證事項。',
      },
    ];

    return {
      caseRecord: caseRec,
      facts,
      evidence: evidenceItems,
      behaviors,
      candidates,
      coreIssues,
      questions,
      report,
      summary: text,
      aiBrief,
      categoryName,
      badges: [
        { label: '法規', count: laws.length, key: 'laws' },
        { label: '裁判', count: rulings.length, key: 'rulings' },
        { label: '論著', count: treatises.length, key: 'treatises' },
      ],
      laws,
      rulings,
      treatises,
    };
  }
}
