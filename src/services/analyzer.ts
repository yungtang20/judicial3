import {
  FactItem,
  LegalCandidate,
  InterviewQuestion,
  OfficialReport,
  AssertionStatus,
  CandidateStatus,
} from '../types';

export class AnalyzerService {
  /**
   * Gate 1: 事實語意拆解
   * 遵守規格 1.2、4.3：不預設犯罪、區分陳述 (ASSERTED)、承認 (ADMITTED)、否認 (DENIED)、推論 (INFERRED)、未知 (UNKNOWN)
   */
  static extractFacts(summary: string, caseId: string, revisionId: number): FactItem[] {
    const facts: FactItem[] = [];
    const now = new Date().toISOString();

    // 透過標點符號與換行分割獨立語句
    const rawSentences = summary
      .split(/[。！？\n]/)
      .map((s) => s.trim())
      .filter((s) => s.length >= 6);

    const sentences = rawSentences.length > 0 ? rawSentences : [summary.trim()];

    sentences.forEach((sentence, idx) => {
      let status: AssertionStatus = 'ASSERTED';
      if (/承認|自首|坦承|有說是他|有拿|有領/i.test(sentence)) {
        status = 'ADMITTED';
      } else if (/否認|辯稱|不知情|沒有|反對|抗辯|不知為/i.test(sentence)) {
        status = 'DENIED';
      } else if (/研判|推論|疑似|可能|初步研判/i.test(sentence)) {
        status = 'INFERRED';
      } else if (/尚待|未明|不詳|未知|待確認|不知/i.test(sentence)) {
        status = 'UNKNOWN';
      }

      // 提取時間
      const timeMatch = sentence.match(/(民國\s*\d{2,3}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日|\d{1,2}\s*時\s*\d{1,2}\s*分|\d{1,2}\s*月\s*\d{1,2}\s*日|某日|某時|當日|日前)/);
      const eventTime = timeMatch ? timeMatch[0] : '民國113年案發時段（待筆錄查證）';

      // 提取地點
      const locMatch = sentence.match(/(在|於)([\u4e00-\u9fa5]{2,15}(?:市|縣|區|路|街|號|超商|ATM|門市|店|住處|所|局|變電箱))/);
      const eventLocation = locMatch ? locMatch[2] : '案發處所（待筆錄精確化）';

      // 提取主體
      let subject = '相關當事人';
      if (/報案人|被害人|甲女|丙男|告訴人/.test(sentence)) subject = '報案人/被害人';
      else if (/涉嫌人|犯嫌|乙男|丁女|被告|嫌犯/.test(sentence)) subject = '涉嫌人/行為人';
      else if (/對方|自稱|不詳人士|某男|某女|飛哥/.test(sentence)) subject = '不詳第三方/指使者';

      facts.push({
        id: `fact-${Date.now()}-${idx + 1}`,
        case_id: caseId,
        revision_id: revisionId,
        subject,
        predicate: sentence.slice(0, 50),
        object: '案件事實構成要素',
        event_time: eventTime,
        event_location: eventLocation,
        source_type: /被害人|報案人|甲女|丙男/.test(sentence)
          ? 'VICTIM'
          : /涉嫌人|犯嫌|被告|乙男|丁女/.test(sentence)
          ? 'SUSPECT'
          : 'POLICE_RECORD',
        source_ref: '報案人指訴或現場查獲紀錄',
        source_excerpt: sentence,
        assertion_status: status,
        confidence: status === 'UNKNOWN' ? 0.35 : 0.9,
        related_evidence: [],
        created_at: now,
        updated_at: now,
      });
    });

    return facts;
  }

  /**
   * Gate 2: 候選法律方向與構成要件分析
   * 遵守規格 1.2、4.4、5.4：不只分析最明顯的一個罪名，辨識合理的替代法律方向
   */
  static generateLegalCandidates(
    summary: string,
    facts: FactItem[],
    caseId: string,
    revisionId: number
  ): LegalCandidate[] {
    const candidates: LegalCandidate[] = [];
    const text = (summary + ' ' + facts.map((f) => f.source_excerpt).join(' ')).toLowerCase();
    const now = new Date().toISOString();

    // 1. 詐欺 / 車手 / 假冒公務員 / 洗錢
    if (/詐|騙|提款|車手|提領|健保|檢察官|帳戶|人頭/i.test(text)) {
      candidates.push({
        id: `cand-${Date.now()}-1`,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '刑法第339條之4 第1項第1、2款 加重詐欺取財罪',
        statute_ref: '中華民國刑法 §339-4 I(1)(2)',
        candidate_status: 'PRIMARY' as CandidateStatus,
        statute_version: '現行有效條文（113年施行版本）',
        support_fact_refs: facts.filter((f) => f.assertion_status !== 'DENIED').map((f) => f.id),
        contrary_fact_refs: facts.filter((f) => f.assertion_status === 'DENIED').map((f) => f.id),
        unknown_fact_refs: facts.filter((f) => f.assertion_status === 'UNKNOWN').map((f) => f.id),
        alternative_explanations: [
          '共同正犯：分工合作具共同犯意聯絡與行為分擔。',
          '幫助犯：僅單純代為跑腿提供助力無核心利益分贓（不確定故意程度爭議）。',
        ],
        elements: [
          {
            id: `elem-${Date.now()}-11`,
            candidate_id: `cand-${Date.now()}-1`,
            element_name: '冒用政府機關或公務員名義',
            element_description: '行為人冒充公權力身分詐騙被害人',
            related_fact_refs: facts.map((f) => f.id),
            element_status: /公務員|檢察官|健保|警察/.test(text) ? 'SATISFIED' : 'PENDING_VERIFICATION',
            reasoning: '電話通聯與被害人指訴均提及公務員或機關名義。',
            source_ref: '刑法第339-4條第1項第1款',
          },
          {
            id: `elem-${Date.now()}-12`,
            candidate_id: `cand-${Date.now()}-1`,
            element_name: '三人以上共同犯之',
            element_description: '集團分工達三人以上',
            related_fact_refs: [],
            element_status: 'SATISFIED',
            reasoning: '話務手、通訊軟體指示者及現場車手三人以上分工架構。',
            source_ref: '刑法第339-4條第1項第2款',
          },
          {
            id: `elem-${Date.now()}-13`,
            candidate_id: `cand-${Date.now()}-1`,
            element_name: '主觀犯意聯絡與行為分擔',
            element_description: '涉嫌人具有共同詐欺取財之犯意認知',
            related_fact_refs: [],
            element_status: 'PENDING_VERIFICATION',
            reasoning: '涉嫌人否認主觀知情，須透過報酬對價、通訊紀錄與取卡方式檢驗。',
            source_ref: '最高法院107年度台上字第4225號判決意旨',
          },
        ],
        created_at: now,
      });

      candidates.push({
        id: `cand-${Date.now()}-2`,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '洗錢防制法第14條第1項 一般洗錢罪',
        statute_ref: '洗錢防制法 §14 I',
        candidate_status: 'ALTERNATIVE' as CandidateStatus,
        statute_version: '現行有效法規',
        support_fact_refs: [],
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: ['將詐欺贓款實體提領轉化為現金，隱匿金流來源與去向。'],
        elements: [
          {
            id: `elem-${Date.now()}-21`,
            candidate_id: `cand-${Date.now()}-2`,
            element_name: '掩飾或隱匿特定犯罪所得',
            element_description: '阻斷司法機關追查金流管道',
            related_fact_refs: [],
            element_status: 'SATISFIED',
            reasoning: '提款現鈔移轉占有之實質評價。',
            source_ref: '洗錢防制法第3條、第14條',
          },
        ],
        created_at: now,
      });
    }

    // 2. 竊盜 vs 侵占遺失物 vs 盜刷
    if (/拿走|取走|偷|拾得|撿到|遺失|皮夾|刷卡|消費|化妝品/i.test(text) || candidates.length === 0) {
      candidates.push({
        id: `cand-${Date.now()}-3`,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '刑法第337條 侵占離本人持有物罪',
        statute_ref: '中華民國刑法 §337',
        candidate_status: 'PRIMARY' as CandidateStatus,
        statute_version: '現行有效法規',
        support_fact_refs: [],
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: [
          '若物原本已脫離被害人直接持有範圍，偶然拾得入己，評價為侵占離本人持有物。',
        ],
        elements: [
          {
            id: `elem-${Date.now()}-31`,
            candidate_id: `cand-${Date.now()}-3`,
            element_name: '遺失物、漂流物或離本人持有物',
            element_description: '客體已脫離原管領人之直接實力支配範圍',
            related_fact_refs: [],
            element_status: 'SATISFIED',
            reasoning: '被害人離開現場數分鐘遺忘財物。',
            source_ref: '刑法第337條',
          },
        ],
        created_at: now,
      });

      candidates.push({
        id: `cand-${Date.now()}-4`,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '刑法第320條第1項 普通竊盜罪（替代路線）',
        statute_ref: '中華民國刑法 §320 I',
        candidate_status: 'ALTERNATIVE' as CandidateStatus,
        statute_version: '現行有效法規',
        support_fact_refs: [],
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: [
          '封閉營業場所內遺落之動產，若認場所主人具有概括支配力，未得同意取走仍有成立竊盜之可能。',
        ],
        elements: [
          {
            id: `elem-${Date.now()}-41`,
            candidate_id: `cand-${Date.now()}-4`,
            element_name: '他人實力管領下之動產',
            element_description: '被害人或場所管理者之管領力尚未完全中斷',
            related_fact_refs: [],
            element_status: 'PENDING_VERIFICATION',
            reasoning: '需調閱場所動線與遺失至發現時間距。',
            source_ref: '刑法第320條',
          },
        ],
        created_at: now,
      });

      if (/刷卡|信用卡|感應|簽帳/i.test(text)) {
        candidates.push({
          id: `cand-${Date.now()}-5`,
          case_id: caseId,
          revision_id: revisionId,
          legal_name: '刑法第339條第1項 詐欺取財罪（無權冒用刷卡）',
          statute_ref: '中華民國刑法 §339 I',
          candidate_status: 'PRIMARY' as CandidateStatus,
          statute_version: '現行有效法規',
          support_fact_refs: [],
          contrary_fact_refs: [],
          unknown_fact_refs: [],
          alternative_explanations: ['持他人信用卡免簽名感應過卡，使店家陷於錯誤交付商品。'],
          elements: [
            {
              id: `elem-${Date.now()}-51`,
              candidate_id: `cand-${Date.now()}-5`,
              element_name: '施用詐術與交付財物',
              element_description: '冒充合法授權持卡人行使權利',
              related_fact_refs: [],
              element_status: 'SATISFIED',
              reasoning: '未經授權感應消費獲得對價商品。',
              source_ref: '刑法第339條',
            },
          ],
          created_at: now,
        });
      }
    }

    // 3. 妨害秘密 / 性隱私
    if (/偷拍|影片|性|隱私|照像|錄影|如廁/i.test(text)) {
      candidates.push({
        id: `cand-${Date.now()}-6`,
        case_id: caseId,
        revision_id: revisionId,
        legal_name: '刑法第319條之1第1項 未經同意攝錄性影像罪',
        statute_ref: '中華民國刑法 §319-1 I',
        candidate_status: 'PRIMARY',
        statute_version: '現行有效法規（112年增訂施行）',
        support_fact_refs: [],
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: ['若攝錄內容非屬性影像或隱私部位，則退回評估刑法第315條之1妨害秘密罪。'],
        elements: [
          {
            id: `elem-${Date.now()}-61`,
            candidate_id: `cand-${Date.now()}-6`,
            element_name: '未經同意攝錄性影像',
            element_description: '無正當理由以照相、錄影攝錄他人性影像',
            related_fact_refs: [],
            element_status: 'PENDING_VERIFICATION',
            reasoning: '需確認查扣設備內影像之私密程度與當事人是否知情同意。',
            source_ref: '刑法第319-1條',
          },
        ],
        created_at: now,
      });
    }

    return candidates;
  }

  /**
   * Gate 3: 依 Chapter 5.1 產生 9 大分類的筆錄問句
   */
  static generateInterviewQuestions(
    caseId: string,
    candidates: LegalCandidate[]
  ): InterviewQuestion[] {
    const questions: InterviewQuestion[] = [];
    const prim = candidates[0] || { id: 'cand-gen' };

    // 1. 核心構成要件問句
    questions.push({
      id: `q-${Date.now()}-1`,
      case_id: caseId,
      candidate_id: prim.id,
      question_type: '1_CORE_ELEMENT',
      question_text: '你於行為時主觀上是否知悉或可預見該財物/行為可能涉及他人所有權或違法性？',
      rationale: '確認犯罪主觀故意或未必故意，建立構成要件必備事實。',
      target_fact_refs: [],
      priority: 'P0_CRITICAL',
      review_status: 'DRAFT',
      is_required: true,
      revision_number: 1,
      expected_clarification: '釐清行為人認知深度與知情程度。',
    });

    // 2. 行為經過問句
    questions.push({
      id: `q-${Date.now()}-2`,
      case_id: caseId,
      candidate_id: prim.id,
      question_type: '2_ACT_PROCESS',
      question_text: '請具體陳述你當日自到達現場、著手實施至離開現場之完整詳細經過？',
      rationale: '還原連續行為時序，檢驗客觀構成要件著手與既遂時點。',
      target_fact_refs: [],
      priority: 'P0_CRITICAL',
      review_status: 'DRAFT',
      is_required: true,
      revision_number: 1,
      expected_clarification: '獲取完整時序性動作紀錄。',
    });

    // 3. 主觀認知及意思問句
    questions.push({
      id: `q-${Date.now()}-3`,
      case_id: caseId,
      candidate_id: prim.id,
      question_type: '3_SUBJECTIVE_INTENT',
      question_text: '你為上述行為時，意圖獲取何種利益或達到何種目的？有無受他人教唆或指揮？',
      rationale: '探求不法所有意圖、損害他人意圖或共同分工意思聯絡。',
      target_fact_refs: [],
      priority: 'P0_CRITICAL',
      review_status: 'DRAFT',
      is_required: true,
      revision_number: 1,
      expected_clarification: '確認犯意動機與共犯指示來源。',
    });

    // 4. 時間、地點及人物關係問句
    questions.push({
      id: `q-${Date.now()}-4`,
      case_id: caseId,
      candidate_id: prim.id,
      question_type: '4_TIME_LOCATION_PERSON',
      question_text: '你與在場其他關係人（或被害人）平時是否有任何親誼、借貸、僱傭或糾紛關係？',
      rationale: '排除民事債務抗辯或特定身分免除刑罰關係。',
      target_fact_refs: [],
      priority: 'P1_IMPORTANT',
      review_status: 'DRAFT',
      is_required: true,
      revision_number: 1,
      expected_clarification: '排除雙方既有民事糾紛借款辯解。',
    });

    // 5. 財物、款項、工具或資料流向問句
    questions.push({
      id: `q-${Date.now()}-5`,
      case_id: caseId,
      candidate_id: prim.id,
      question_type: '5_FLOW_OF_PROPERTY',
      question_text: '涉案之款項、卡片或物品，目前下落何在？有無藏匿、移轉、變賣或交付第三人？',
      rationale: '查證贓物流向，完備沒收及追徵要件，並尋找其他共犯。',
      target_fact_refs: [],
      priority: 'P0_CRITICAL',
      review_status: 'DRAFT',
      is_required: true,
      revision_number: 1,
      expected_clarification: '贓物保全與共犯查緝線索。',
    });

    // 6. 證據及來源問句
    questions.push({
      id: `q-${Date.now()}-6`,
      case_id: caseId,
      candidate_id: prim.id,
      question_type: '6_EVIDENCE_SOURCE',
      question_text: '警方現場所扣押之相關證物是否均為你本人所有及持有？有無其他相關紀錄可供查證？',
      rationale: '確立證據保管鏈與證物關聯性。',
      target_fact_refs: [],
      priority: 'P1_IMPORTANT',
      review_status: 'DRAFT',
      is_required: true,
      revision_number: 1,
      expected_clarification: '證物管領權確定。',
    });

    // 7. 反向事實及替代解釋問句
    questions.push({
      id: `q-${Date.now()}-7`,
      case_id: caseId,
      candidate_id: prim.id,
      question_type: '7_CONTRARY_ALTERNATIVE',
      question_text: '你是否主張該行為係獲得被害人同意，或純屬正當合法受委託代辦業務？有何依據？',
      rationale: '主動檢驗阻卻違法事由或有利抗辯，避免預設立場。',
      target_fact_refs: [],
      priority: 'P1_IMPORTANT',
      review_status: 'DRAFT',
      is_required: true,
      revision_number: 1,
      expected_clarification: '驗證正當防衛、業務正當或得被害人承諾等可能。',
    });

    // 8. 矛盾與補充問句
    questions.push({
      id: `q-${Date.now()}-8`,
      case_id: caseId,
      candidate_id: prim.id,
      question_type: '8_CONTRADICTION_SUPPLEMENT',
      question_text: '現場客觀監視器翻拍紀錄與你上述陳述有所出入，你對該不一致之處如何說明？',
      rationale: '針對陳述矛盾點進行中性追問，確保自白任意性與客觀性。',
      target_fact_refs: [],
      priority: 'P1_IMPORTANT',
      review_status: 'DRAFT',
      is_required: true,
      revision_number: 1,
      expected_clarification: '消除供述與物證之重大歧異。',
    });

    // 9. 尚待查明事項問句
    questions.push({
      id: `q-${Date.now()}-9`,
      case_id: caseId,
      candidate_id: prim.id,
      question_type: '9_UNRESOLVED_INQUIRY',
      question_text: '就本案事實，除上述各節外，有無其他有利事項或待傳喚之證人請求調查？',
      rationale: '依刑事訴訟法第2條注意有利不利原則，保障權益。',
      target_fact_refs: [],
      priority: 'P2_SUPPLEMENTAL',
      review_status: 'DRAFT',
      is_required: true,
      revision_number: 1,
      expected_clarification: '確保當事人陳述意見防禦權充分行使。',
    });

    return questions;
  }

  /**
   * Gate 5: 條陳編製與格式驗證（符合警政機關公務條陳體裁）
   */
  static validateOfficialReport(report: OfficialReport): string[] {
    const errors: string[] = [];

    if (!report.station.trim()) {
      errors.push('報告單位不得為空白。');
    }
    if (!report.title_reason.trim()) {
      errors.push('案由不得為空白。');
    }
    if (!report.incident_time_roc.startsWith('民國') || !report.incident_time_roc.includes('年')) {
      errors.push('發生時間必須符合公務民國紀年格式（例：民國113年5月10日15時許）。');
    }
    if (!report.incident_location.trim()) {
      errors.push('發生地點不得為空白。');
    }
    if (!report.summary_text.trim() || report.summary_text.length < 20) {
      errors.push('案情摘要不得少於20字，且須完整包含人、事、時、地、物要件。');
    }
    if (report.summary_text.length > 500) {
      errors.push('案情摘要不得超過500個Unicode字元，請重新整理後再輸出。');
    }
    if (!report.jurisdiction.trim()) {
      errors.push('本案管轄檢察署或法院不得為空白。');
    }
    if (!report.handling_officer.trim()) {
      errors.push('處理員警職稱及姓名不得為空白。');
    }

    return errors;
  }

  /**
   * 只補上可辨識的格式標記；不捏造日期、機關、人員或案號。
   */
  static autoFixReport(report: OfficialReport): OfficialReport {
    let incidentTime = report.incident_time_roc.trim();
    if (!incidentTime.startsWith('民國')) {
      incidentTime = '[發生時間待查證填報]';
    }

    let station = report.station.trim();
    if (!station) {
      station = '[報告單位待填報]';
    }

    let jurisdiction = report.jurisdiction.trim();
    if (!jurisdiction) {
      jurisdiction = '[管轄地方檢察署待填報]';
    }

    let officer = report.handling_officer.trim();
    if (!officer) {
      officer = '[承辦員警待填報]';
    }

    let certNo = report.certificate_number.trim();
    if (!certNo || certNo.includes('待填報')) {
      certNo = '[受處理案件證明單案號待填報]';
    }

    return {
      ...report,
      station,
      incident_time_roc: incidentTime,
      jurisdiction,
      handling_officer: officer,
      certificate_number: certNo,
    };
  }
}
