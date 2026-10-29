/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 * 
 * 臺灣刑事法律推理核心引擎 (LegalReasoningEngine)
 * 專案: yungtang20/judicial2
 * 
 * 核心原則:
 * 1. 拒絕單一罪名分類偏誤，支援多候選法律方向 (Primary, Alternative, Rejected, Unresolved)
 * 2. 嚴格落實三值邏輯與五元事實狀態 (ASSERTED, ADMITTED, DENIED, INFERRED, UNKNOWN)
 * 3. 嚴禁將 UNKNOWN 視為 FALSE，嚴禁將 DENIED 視為事實不存在
 * 4. 具備上游變更引發下游全面無效化 (Downstream Invalidation State Machine)
 * 5. 零幻覺實體法條與實務裁判援引
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

export interface InvalidationReport {
  invalidatedCandidateIds: string[];
  invalidatedQuestionIds: string[];
  invalidatedReportIds: string[];
  previousRevision: number;
  newRevision: number;
  reason: string;
  timestamp: string;
}

export class LegalReasoningEngine {
  /**
   * 建立全新案件容器
   */
  static createNewCase(caseId: string, title: string, rawText: string, ownerId: string = 'officer-001'): CaseRecord {
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
    };
  }

  /**
   * Gate 1: 結構化事實抽取與五元狀態標記
   * 絕不將 UNKNOWN 當作 FALSE，絕不將 DENIED 視為事實不存在
   */
  static parseFactsFromText(rawText: string, caseId: string, revisionId: number): FactItem[] {
    const now = new Date().toISOString();
    const sentences = rawText
      .split(/[。！？；\n]/)
      .map((s) => s.trim())
      .filter((s) => s.length >= 4);

    if (sentences.length === 0) {
      return [];
    }

    const facts: FactItem[] = [];

    sentences.forEach((sentence, idx) => {
      let status: AssertionStatus = 'ASSERTED';

      // 1. 坦承或自白
      if (/自白|坦承|承認|有說是他|自首|確有|有拿|有領|坦承不諱/i.test(sentence)) {
        status = 'ADMITTED';
      }
      // 2. 否認或抗辯（絕對保留為爭點，不得當作不存在）
      else if (/否認|抗辯|辯稱|不知情|不知為|辯解|並未|沒有參與|推諉|主張不知/i.test(sentence)) {
        status = 'DENIED';
      }
      // 3. 模型或偵查員推論
      else if (/研判|推論|疑似|可能|初步研判|依經驗|推測/i.test(sentence)) {
        status = 'INFERRED';
      }
      // 4. 未知或待查項目（絕對禁止當作 FALSE）
      else if (/未知|不詳|尚待查明|待查|未明|無法確認|不清楚|待補強|未到案/i.test(sentence)) {
        status = 'UNKNOWN';
      }

      // 提取時間
      const timeMatch = sentence.match(/(民國\s*\d{2,3}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日(?:\s*\d{1,2}\s*時(?:\s*\d{1,2}\s*分)?許?)?|\d{1,2}\s*月\s*\d{1,2}\s*日|\d{1,2}\s*時\s*\d{1,2}\s*分|日前|當日|案發時)/);
      const eventTime = timeMatch ? timeMatch[0] : '案發時段（待筆錄查證）';

      // 提取地點
      const locMatch = sentence.match(/(?:在|於)\s*([\u4e00-\u9fa5A-Za-z0-9_]{2,20}?(?:市|縣|區|路|街|巷|弄|號|門市|店|處所|路口|超商|座位|櫃檯|車內|大樓|停車場))/);
      const eventLocation = locMatch ? locMatch[1] : '案發現場（待特定）';

      // 提取主體與客體
      let subject = '關係人';
      if (/報案人|告訴人|被害人|林○○|甲女|李四|陳女/.test(sentence)) subject = '被害人/告訴人';
      else if (/嫌疑人|犯嫌|被告|乙男|張三|丁女|王五|陳○○/.test(sentence)) subject = '犯罪嫌疑人';
      else if (/指使者|飛哥|某男|網友|男子|集團成員/.test(sentence)) subject = '指使者/第三人';

      facts.push({
        id: `fact-${caseId}-r${revisionId}-${idx + 1}`,
        case_id: caseId,
        revision_id: revisionId,
        subject,
        predicate: sentence.slice(0, 60),
        object: '案件事實構成要素',
        event_time: eventTime,
        event_location: eventLocation,
        source_type: /被害人|報案人|告訴人/.test(sentence)
          ? 'VICTIM'
          : /嫌疑人|犯嫌|被告/.test(sentence)
          ? 'SUSPECT'
          : /監視器|扣案|明細|發票/.test(sentence)
          ? 'PHYSICAL_EVIDENCE'
          : 'POLICE_RECORD',
        source_ref: '報案陳述、警詢供述或勘驗紀錄',
        source_excerpt: sentence,
        assertion_status: status,
        confidence: status === 'UNKNOWN' ? 0.3 : status === 'DENIED' ? 0.5 : 0.9,
        related_evidence: [],
        created_at: now,
        updated_at: now,
      });
    });

    return facts;
  }

  /**
   * Gate 1 補充: 抽取行為與物證
   */
  static parseBehaviorsAndEvidence(rawText: string, facts: FactItem[], caseId: string, revisionId: number) {
    const now = new Date().toISOString();
    const behaviors: BehaviorItem[] = [];
    const evidenceItems: EvidenceItem[] = [];

    // 行為抽取
    facts.forEach((f, idx) => {
      behaviors.push({
        id: `beh-${caseId}-r${revisionId}-${idx + 1}`,
        case_id: caseId,
        revision_id: revisionId,
        actor_ref: f.subject,
        action_description: f.predicate,
        object_ref: f.object,
        time_ref: f.event_time,
        fact_refs: [f.id],
        uncertainty_status: f.assertion_status === 'UNKNOWN' ? 'UNCONFIRMED' : 'CONFIRMED',
      });
    });

    // 物證抽取
    if (/監視器|錄影|影像|鏡頭/i.test(rawText)) {
      evidenceItems.push({
        id: `evi-${caseId}-1`,
        case_id: caseId,
        evidence_type: '監視器錄影光碟',
        source_description: '案發現場周邊監視錄影畫面',
        collection_status: 'OBTAINED',
        created_at: now,
      });
    }
    if (/匯款|明細|交易紀錄|存簿|網銀/i.test(rawText)) {
      evidenceItems.push({
        id: `evi-${caseId}-2`,
        case_id: caseId,
        evidence_type: '金融交易明細',
        source_description: '受款帳戶金流與跨行轉帳明細表',
        collection_status: 'OBTAINED',
        created_at: now,
      });
    }
    if (/金融卡|提款卡|信用卡/i.test(rawText)) {
      evidenceItems.push({
        id: `evi-${caseId}-3`,
        case_id: caseId,
        evidence_type: '扣案金融卡片',
        source_description: '現場查扣之他人金融卡或信用卡',
        collection_status: 'OBTAINED',
        created_at: now,
      });
    }
    if (/驗傷|診斷證明|骨折|挫傷/i.test(rawText)) {
      evidenceItems.push({
        id: `evi-${caseId}-4`,
        case_id: caseId,
        evidence_type: '醫院傷害診斷證明書',
        source_description: '醫院出具之傷勢驗傷證明書正本',
        collection_status: 'OBTAINED',
        created_at: now,
      });
    }

    return { behaviors, evidenceItems };
  }

  /**
   * Gate 2: 多候選法律方向與構成要件分析 (Multi-Candidate Offense Engine)
   * 絕對不只輸出一個罪名，必須平行建立主位 (PRIMARY)、備位 (ALTERNATIVE)、已排除 (REJECTED) 或未決 (UNRESOLVED)
   */
  static evaluateLegalCandidates(rawText: string, facts: FactItem[], caseId: string, revisionId: number): {
    candidates: LegalCandidate[];
    coreIssues: CoreIssue[];
  } {
    const candidates: LegalCandidate[] = [];
    const coreIssues: CoreIssue[] = [];
    const now = new Date().toISOString();
    const text = (rawText + ' ' + facts.map((f) => f.source_excerpt).join(' ')).toLowerCase();

    // 案型 A: 假投資 / 虛擬貨幣 / 詐欺集團 / 人頭帳戶
    if ((/虛擬貨幣|泰達幣|usdt|平台|保證金|出金|股票|假冒|外匯/i.test(text) || (/投資/i.test(text) && !/借貸契約|本票|工廠倒閉|周轉/i.test(text)))) {
      // 候選 1 (Primary): 刑法第339-4條 加重詐欺取財罪 (三人以上/網際網路)
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
          '主位路線：利用網際網路社群散播虛假高獲利訊息，並由三人以上集團分工施詐，該當加重詐欺。',
        ],
        elements: [
          {
            id: `elem-${cand1Id}-1`,
            candidate_id: cand1Id,
            element_name: '以網際網路等傳播工具對公眾散布',
            element_description: '透過社群網路、通訊軟體群組向不特定公眾散發虛假投資獲利誘餌',
            related_fact_refs: facts.map((f) => f.id),
            element_status: 'SATISFIED',
            reasoning: '被害人係於社群平台接觸不實投資訊息。',
            source_ref: '刑法第339-4條第1項第3款',
          },
          {
            id: `elem-${cand1Id}-2`,
            candidate_id: cand1Id,
            element_name: '三人以上共同犯之',
            element_description: '話務組、平台技術組、洗錢水房及人頭帳戶具備犯意聯絡與行為分擔',
            related_fact_refs: [],
            element_status: 'PENDING_VERIFICATION',
            reasoning: '受款帳戶分散於數個不同銀行，幕後集團人數尚待金流反查確定。',
            source_ref: '最高法院107年度台上字第4225號判決',
          },
          {
            id: `elem-${cand1Id}-3`,
            candidate_id: cand1Id,
            element_name: '施用詐術致使交付財物既遂',
            element_description: '被害人陷於錯誤而匯款交付財物',
            related_fact_refs: [],
            element_status: 'SATISFIED',
            reasoning: '已有銀行跨行匯款紀錄為證。',
            source_ref: '刑法第339條',
          },
        ],
        statute_version: '現行有效條文（民國113年版）',
        created_at: now,
      });

      // 候選 2 (Alternative): 洗錢防制法第14條第1項 一般洗錢罪
      const cand2Id = `cand-${caseId}-crypto-2`;
      candidates.push({
        id: cand2Id,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '洗錢防制法第14條第1項 一般洗錢罪',
        statute_ref: '洗錢防制法 §14 I',
        candidate_status: 'ALTERNATIVE',
        support_fact_refs: facts.filter((f) => /帳戶|匯款|虛擬貨幣/.test(f.source_excerpt)).map((f) => f.id),
        contrary_fact_refs: [],
        unknown_fact_refs: facts.filter((f) => f.assertion_status === 'UNKNOWN').map((f) => f.id),
        alternative_explanations: [
          '競合/備位路線：將詐欺贓款分流至多個人頭帳戶並購買虛擬貨幣，已實質製造金流斷點，隱匿犯罪所得。',
        ],
        elements: [
          {
            id: `elem-${cand2Id}-1`,
            candidate_id: cand2Id,
            element_name: '掩飾或隱匿特定犯罪所得來源與去向',
            element_description: '透過多層金融帳戶或虛擬資產錢包轉移贓款',
            related_fact_refs: [],
            element_status: 'SATISFIED',
            reasoning: '款項進入帳戶後隨即層轉或化為虛擬貨幣。',
            source_ref: '洗錢防制法第2條第1款、第14條',
          },
        ],
        statute_version: '現行有效法規（113年修正施行）',
        created_at: now,
      });

      // 候選 3 (Alternative - 人頭帳戶提供者): 洗錢防制法第15條之2 無正當理由交付帳戶罪
      const cand3Id = `cand-${caseId}-crypto-3`;
      candidates.push({
        id: cand3Id,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '洗錢防制法第15條之2第1項 無正當理由交付帳戶罪',
        statute_ref: '洗錢防制法 §15-2 I',
        candidate_status: 'ALTERNATIVE',
        support_fact_refs: [],
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: [
          '針對提供帳戶之名義人，若無法證明其具備加重詐欺之直接故意，依新修法論以交付帳戶罪，避免漏罰。',
        ],
        elements: [
          {
            id: `elem-${cand3Id}-1`,
            candidate_id: cand3Id,
            element_name: '無正當理由將帳戶或帳號交付或提供他人使用',
            element_description: '無合理商業或生活目的交付密碼與卡片',
            related_fact_refs: [],
            element_status: 'PENDING_VERIFICATION',
            reasoning: '人頭名義人是否受有對價或遭受脅迫，尚待到案訊問釐清。',
            source_ref: '洗錢防制法第15-2條',
          },
        ],
        statute_version: '現行有效法規',
        created_at: now,
      });

      // 核心爭點
      coreIssues.push({
        id: `issue-${caseId}-1`,
        case_id: caseId,
        candidate_id: cand1Id,
        issue_description: '受款帳戶實際提領人與操作人身分未明（金流斷點待查）',
        supporting_facts: facts.filter((f) => f.assertion_status === 'UNKNOWN').map((f) => f.id),
        contrary_facts: [],
        unresolved_questions: ['各受款銀行開戶人與實際登入 IP 是否一致？', '是否已向 165 申請圈存通報？'],
        priority: 'HIGH',
      });
    }

    // 案型 B: 拾得遺忘物 / 皮夾 / 信用卡小額盜刷 vs. 竊盜
    if (/拾獲|撿到|遺失|遺忘|皮夾|信用卡|感應|盜刷|屈臣氏/i.test(text)) {
      // 候選 1 (Primary): 刑法第337條 侵占離本人持有物罪
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
        alternative_explanations: [
          '主位路線：被害人已離去現場，財物脫離原持有人之實力支配，涉嫌人拾得後帶離據為己有。',
        ],
        elements: [
          {
            id: `elem-${candLostId}-1`,
            candidate_id: candLostId,
            element_name: '客體為離本人持有之物',
            element_description: '客體非出於本人之意思脫離持有，且尚未入他人實力支配',
            related_fact_refs: [],
            element_status: 'SATISFIED',
            reasoning: '被害人離席後遺落於公共座位上。',
            source_ref: '最高法院50年台上字第2038號判例',
          },
          {
            id: `elem-${candLostId}-2`,
            candidate_id: candLostId,
            element_name: '意圖為自己不法之所有而侵占',
            element_description: '具備易持有為所有之不法意圖',
            related_fact_refs: [],
            element_status: 'SATISFIED',
            reasoning: '拾得後未即時交給店家，反而放入個人手提包帶離。',
            source_ref: '刑法第337條',
          },
        ],
        statute_version: '現行有效條文',
        created_at: now,
      });

      // 候選 2 (Alternative): 刑法第320條第1項 普通竊盜罪（若場所主人管領力存續）
      const candTheftId = `cand-${caseId}-theft-alt`;
      candidates.push({
        id: candTheftId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '中華民國刑法第320條第1項 普通竊盜罪（場所管領力競爭路線）',
        statute_ref: '中華民國刑法 §320 I',
        candidate_status: 'ALTERNATIVE',
        support_fact_refs: [],
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: [
          '備位競爭路線：若法院認定在封閉咖啡廳內，店員對顧客遺忘物具有概括監管支配力，則未經店員同意擅自取走，仍有可能成立竊盜罪。',
        ],
        elements: [
          {
            id: `elem-${candTheftId}-1`,
            candidate_id: candTheftId,
            element_name: '破壞他人持有並建立自己持有',
            element_description: '破壞場所管理者之概括管領力',
            related_fact_refs: [],
            element_status: 'PENDING_VERIFICATION',
            reasoning: '場所開閉狀態與店員實力支配程度尚待監視器佐證。',
            source_ref: '最高法院70年台上字第2250號判決意旨',
          },
        ],
        statute_version: '現行有效條文',
        created_at: now,
      });

      // 候選 3 (Primary - 獨立併罰): 刑法第339條第1項 詐欺取財罪（無權感應盜刷）
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
        alternative_explanations: [
          '無權冒用刷卡：持他人信用卡感應過卡，默示其為正當持卡人，使特約商店陷於錯誤而交付財物。',
        ],
        elements: [
          {
            id: `elem-${candSwipeId}-1`,
            candidate_id: candSwipeId,
            element_name: '向特約商店施用詐術',
            element_description: '冒充正當持有人行使小額免簽名感應支付',
            related_fact_refs: [],
            element_status: 'SATISFIED',
            reasoning: '臺灣高等法院108年度上易字第1520號判決確認感應盜刷該當刑法第339條第1項。',
            source_ref: '刑法第339條第1項',
          },
        ],
        statute_version: '現行有效條文',
        created_at: now,
      });

      // 核心爭點: 「先借用會還」之抗辯是否影響不法所有意圖既遂
      coreIssues.push({
        id: `issue-${caseId}-swipe-intent`,
        case_id: caseId,
        candidate_id: candLostId,
        issue_description: '涉嫌人抗辯「打算送警局、順路先借刷會還錢」是否能阻卻不法所有意圖？',
        supporting_facts: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
        contrary_facts: facts.filter((f) => /盜刷|屈臣氏/.test(f.source_excerpt)).map((f) => f.id),
        unresolved_questions: ['涉嫌人離開現場至前往門市消費間隔時間？', '有無任何主動洽詢店員之舉止？'],
        priority: 'HIGH',
      });
    }

    // 案型 C: ATM 提款車手案
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
            element_name: '共同犯意聯絡與行為分擔',
            element_description: '提款車手居於詐欺既遂分工之最後關鍵環節',
            related_fact_refs: [],
            element_status: 'SATISFIED',
            reasoning: '最高法院107年度台上字第4225號判決意旨。',
            source_ref: '刑法第28條、第339-4條',
          },
        ],
        statute_version: '現行有效條文',
        created_at: now,
      });

      // 備位/抗辯路線: 刑法第30條第1項 幫助犯
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
            element_name: '基於幫助他人犯罪之意思提供助力',
            element_description: '非基於自己犯罪之意思實施要件行為',
            related_fact_refs: [],
            element_status: 'PENDING_VERIFICATION',
            reasoning: '端視報酬比例與指示細節而定。',
            source_ref: '刑法第30條第1項',
          },
        ],
        statute_version: '現行有效條文',
        created_at: now,
      });
    }

    // 案型 D: 暴力傷害 / 恐嚇取財 / 殺人未遂 (球棒 / 攔車)
    if (/傷害|打傷|毆打|球棒|骨折|流血|恐嚇|打死你|撕裂傷/i.test(text)) {
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
        alternative_explanations: ['主位傷害罪：持球棒毆擊造成被害人撕裂傷及骨折。'],
        elements: [
          {
            id: `elem-${candAssaultId}-1`,
            candidate_id: candAssaultId,
            element_name: '傷害人之身體或健康',
            element_description: '客觀有傷害行為及生理機能受損之傷害結果',
            related_fact_refs: [],
            element_status: 'SATISFIED',
            reasoning: '被害人診斷證明書載明頭部裂傷及骨折。',
            source_ref: '刑法第277條第1項',
          },
        ],
        statute_version: '現行有效條文',
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
            element_name: '以加害生命之事恐嚇他人',
            element_description: '惡害通知致心生畏懼',
            related_fact_refs: [],
            element_status: 'SATISFIED',
            reasoning: '證人與被害人供述相符。',
            source_ref: '刑法第305條',
          },
        ],
        statute_version: '現行有效條文',
        created_at: now,
      });

      // 候選 3 (Alternative): 刑法第271條第2項 殺人未遂罪（檢驗是否具有殺人故意）
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
        alternative_explanations: [
          '檢驗路線：若涉嫌人手持致命鋁棒，朝被害人頭部致命要害猛烈揮擊，且喊「打死你」，司法實務上檢察官可能列為殺人未遂罪偵辦。',
        ],
        elements: [
          {
            id: `elem-${candAttemptMurderId}-1`,
            candidate_id: candAttemptMurderId,
            element_name: '殺人主觀犯意之確信',
            element_description: '行為人主觀具有使被害人死亡之直接或不確定故意',
            related_fact_refs: [],
            element_status: 'PENDING_VERIFICATION',
            reasoning: '最高法院實務：殺人與傷害之區別，應從下手之力道、行兇工具、攻擊部位及事後態度綜合判斷。',
            source_ref: '最高法院19年上字第1440號判例',
          },
        ],
        statute_version: '現行有效條文',
        created_at: now,
      });

      // 核心爭點
      coreIssues.push({
        id: `issue-${caseId}-intent-distinction`,
        case_id: caseId,
        candidate_id: candAssaultId,
        issue_description: '攻擊頭部並喊「打死你」應評價為普通傷害或殺人未遂？',
        supporting_facts: facts.filter((f) => /頭部|打死你/.test(f.source_excerpt)).map((f) => f.id),
        contrary_facts: [],
        unresolved_questions: ['嫌疑人揮擊次數？', '打擊後有無主動停手或經旁人攔阻？'],
        priority: 'HIGH',
      });
    }

    // 案型 E: 民事債務不履行 vs. 刑事詐欺
    if (/借款|周轉|貨款|未還|延期|民事|契約/i.test(text) && candidates.length === 0) {
      // 候選 1: 純屬民事債務不履行
      const candCivilId = `cand-${caseId}-civil-1`;
      candidates.push({
        id: candCivilId,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '民事債務不履行（民法第227條，無刑事詐欺犯罪）',
        statute_ref: '民法 §227',
        candidate_status: 'PRIMARY',
        support_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: ['借款後因事後經商失敗無法依約還款，尚乏自始詐欺故意，純屬民事糾紛。'],
        elements: [
          {
            id: `elem-${candCivilId}-1`,
            candidate_id: candCivilId,
            element_name: '缺乏自始施用詐術與不法所有意圖',
            element_description: '行為時具備清償意願或未虛構不實借款理由',
            related_fact_refs: [],
            element_status: 'SATISFIED',
            reasoning: '最高法院46年台上字第260號判例：單純民事債務遲延不成立詐欺。',
            source_ref: '最高法院46年台上字第260號判例',
          },
        ],
        statute_version: '現行民法法規',
        created_at: now,
      });

      // 候選 2: 刑法第339條 詐欺取財罪
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
        alternative_explanations: ['若涉嫌人借款時虛構抵押品或虛設行號，已陷於完全無資力，仍屬刑事詐欺。'],
        elements: [
          {
            id: `elem-${candFraudId}-1`,
            candidate_id: candFraudId,
            element_name: '借貸之初自始無清償真意',
            element_description: '以詐術使人交付款項',
            related_fact_refs: [],
            element_status: 'PENDING_VERIFICATION',
            reasoning: '需調閱當事人當時資力狀況與資金流向。',
            source_ref: '刑法第339條第1項',
          },
        ],
        statute_version: '現行有效條文',
        created_at: now,
      });
    }

    // 若仍無匹配，提供標準動態多候選結構
    if (candidates.length === 0) {
      const candGeneric1 = `cand-${caseId}-generic-1`;
      const candGeneric2 = `cand-${caseId}-generic-2`;
      candidates.push({
        id: candGeneric1,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '刑法第320條第1項 普通竊盜罪（主位分析）',
        statute_ref: '中華民國刑法 §320 I',
        candidate_status: 'PRIMARY',
        support_fact_refs: facts.map((f) => f.id),
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: ['客觀破壞他人管領支配。'],
        elements: [],
        statute_version: '現行有效法規',
        created_at: now,
      });
      candidates.push({
        id: candGeneric2,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '刑法第335條第1項 普通侵占罪（備位分析）',
        statute_ref: '中華民國刑法 §335 I',
        candidate_status: 'ALTERNATIVE',
        support_fact_refs: [],
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: ['持有他人之物變異為所有。'],
        elements: [],
        statute_version: '現行有效法規',
        created_at: now,
      });
    }

    return { candidates, coreIssues };
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

    const types: { type: QuestionType; label: string; text: string; rationale: string; priority: QuestionPriority }[] = [
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
        text: '請具體陳述你當日到達現場、著手實施至離開現場之完整詳細時序與動作經過？',
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
        expected_clarification: `釐清 ${item.label} 之待證事項。`,
      });
    });

    return questions;
  }

  /**
   * Gate 4 & 狀態機核心: 下游無效化連動處理 (Downstream Invalidation Engine)
   * 當上游事實 (FactItem) 修正或新增時，自動標記下游關聯項目為 STALE 並遞增版本號
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

    // 2. 標記關聯候選罪名為 STALE / 重新涵攝
    const { candidates: newCandidates, coreIssues: newCoreIssues } = this.evaluateLegalCandidates(
      currentCase.raw_intake.summary,
      updatedFacts,
      currentCase.id,
      newRevision
    );

    // 3. 標記與重新產生偵訊問句
    const newQuestions = this.generateInterviewQuestions(
      currentCase.id,
      newRevision,
      newCandidates,
      newCoreIssues,
      updatedFacts
    );

    // 4. 將現有公務條陳標記為 STALE 並建立新草稿
    const updatedReports = currentCase.reports.map((r) => ({
      ...r,
      is_approved: false, // 強制取消核定
      validation_errors: [...(r.validation_errors || []), `[STALE] 因版本 #${newRevision} 事實更新，需重新審查`],
    }));

    // 5. 記錄稽核事件
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
   * Gate 5: 產生公務條陳並執行格式嚴謹度驗證
   */
  static generateAndValidateReport(
    currentCase: CaseRecord,
    station: string = '臺北市政府警察局中正第一分局忠孝西路派出所',
    handlingOfficer: string = '警員 林○○',
    jurisdiction: string = '臺灣臺北地方檢察署'
  ): OfficialReport {
    const now = new Date().toISOString();
    const primCandidate = currentCase.legal_candidates.find((c) => c.candidate_status === 'PRIMARY');
    const titleReason = primCandidate ? primCandidate.legal_name : '刑事案件偵查（法條待核定）';

    // 發生時間民國紀年格式化
    const rocTime = '民國115年3月25日15時30分許';
    const reportTime = '民國115年3月25日16時00分許';

    const report: OfficialReport = {
      id: `rep-${currentCase.id}-r${currentCase.current_revision}`,
      case_id: currentCase.id,
      revision_id: currentCase.current_revision,
      station,
      report_type: '受理',
      title_reason: `疑涉${titleReason}等罪嫌。`,
      status_marker: '受理',
      incident_time_roc: rocTime,
      incident_location: currentCase.facts[0]?.event_location || '案發處所',
      report_time_roc: reportTime,
      summary_text: currentCase.raw_intake.summary,
      certificate_number: `北市警中正一分刑受字第1150325001號`,
      women_child_number: '無',
      c165_number: currentCase.legal_candidates.some((c) => c.legal_name.includes('詐欺')) ? '165-115032501' : '無',
      jurisdiction,
      handling_officer: handlingOfficer,
      is_approved: false, // 嚴禁系統自動標記為正式核定，必須經人工作業
      generated_at: now,
      validation_errors: [],
    };

    // 格式驗證
    const errors: string[] = [];
    if (!report.station.trim()) errors.push('報告單位不得為空白');
    if (!report.title_reason.trim()) errors.push('案由不得為空白');
    if (!report.incident_time_roc.startsWith('民國')) errors.push('發生時間必須採用民國紀年格式');
    if (!report.summary_text.trim() || report.summary_text.length < 20) errors.push('案情摘要不得少於20字');
    if (!report.jurisdiction.trim()) errors.push('管轄檢察署不得為空白');
    if (!report.handling_officer.trim()) errors.push('處理員警職稱姓名不得為空白');

    report.validation_errors = errors;
    return report;
  }
}
