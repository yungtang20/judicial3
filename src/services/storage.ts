import {
  CaseRecord,
  SystemSettings,
  AuditEvent,
  GateStage,
  OfficialReport,
} from '../types';

const STORAGE_KEY_CASES = 'judicial_assistant_cases_v2';
const STORAGE_KEY_SETTINGS = 'judicial_assistant_settings_v2';
const STORAGE_KEY_AUDIT = 'judicial_assistant_audit_v2';
const STORAGE_KEY_AUTH = 'judicial_assistant_auth_v2';

const INITIAL_SETTINGS: SystemSettings = {
  allow_external_ai: false, // 規格第8.3條：第一階段預設關閉外部 AI 案件資料傳輸
  external_ai_endpoint: '已停用（維持沙盒本地安全規則引擎）',
  encryption_enabled: true,
  encryption_key_hash: 'SHA256:7a8f9c0e2b1d4a6f88c3e109d43521bbfa824901f4c78201',
  supabase_connected: false,
  single_owner_id: 'usr_tw_police_88014',
  login_lockout_enabled: true,
};

const SEED_CASES: CaseRecord[] = [
  {
    id: 'case-2026-c001-atm',
    title: '臺北中正第一分局—假冒公務員與車手提領款項案',
    status: 'ACTIVE',
    stage: 'GATE3_QUESTIONS',
    current_revision: 2,
    created_at: '2026-10-25T09:30:00+08:00',
    updated_at: '2026-10-27T08:15:00+08:00',
    owner_id: 'usr_tw_police_88014',
    raw_intake: {
      summary:
        '報案人甲女（民國65年生）指稱：於民國113年8月10日10時許接獲未顯示來電，對方自稱「健保局科長」指稱其健保卡在高雄遭冒用涉嫌洗錢，隨後轉接「特偵組林檢察官」，要求甲女將名下臺灣銀行提款卡2張及密碼置於臺北市中正區濟南路一段指定變電箱後方，以供監管清查。甲女依言照辦。同日14時30分許，涉嫌人乙男持該卡於臺北市中正區忠孝東路一段ATM自動櫃員機接續提領新臺幣20萬元。乙男遭巡邏員警當場盤查查獲，起獲提款卡2張及現金20萬元。乙男否認共同詐欺，辯稱係於Telegram受暱稱「飛哥」者指示代領款項，每次報酬新臺幣3,000元，不知為詐騙贓款。',
      supplementary_notes: '涉嫌人持有手機2支扣案，監視器錄影翻拍照片4張，贓款20萬元已依法發還被害人。',
      analysis_remarks: '應特別注意主觀詐欺故意與洗錢不確定故意之區辨，以及是否有侵占遺失物或單純民事代領之辯解空間。',
      created_at: '2026-10-25T09:30:00+08:00',
    },
    facts: [
      {
        id: 'fact-001',
        case_id: 'case-2026-c001-atm',
        revision_id: 1,
        subject: '自稱健保局與檢察官之不詳人士',
        predicate: '撥打電話施用詐術要求交付提款卡及密碼',
        object: '報案人甲女名下臺灣銀行提款卡2張與密碼',
        event_time: '民國113年8月10日10時許',
        event_location: '電話聯繫（被害人家中）',
        source_type: 'VICTIM',
        source_ref: '甲女指訴筆錄',
        source_excerpt: '對方自稱健保局科長與特偵組林檢察官，說我涉及洗錢要監管帳戶...',
        assertion_status: 'ASSERTED',
        confidence: 0.95,
        related_evidence: ['電話通聯紀錄', '被害人筆錄'],
        created_at: '2026-10-25T09:35:00+08:00',
        updated_at: '2026-10-25T09:35:00+08:00',
      },
      {
        id: 'fact-002',
        case_id: 'case-2026-c001-atm',
        revision_id: 1,
        subject: '報案人甲女',
        predicate: '將提款卡2張與密碼放置於變電箱後方',
        object: '變電箱後方置放點',
        event_time: '民國113年8月10日12時許',
        event_location: '臺北市中正區濟南路一段變電箱',
        source_type: 'VICTIM',
        source_ref: '甲女指訴筆錄及現場照片',
        source_excerpt: '我把裝有2張卡片和寫著密碼的便條紙放在變電箱後面...',
        assertion_status: 'ASSERTED',
        confidence: 0.98,
        related_evidence: ['置放點現場採證照片'],
        created_at: '2026-10-25T09:36:00+08:00',
        updated_at: '2026-10-25T09:36:00+08:00',
      },
      {
        id: 'fact-003',
        case_id: 'case-2026-c001-atm',
        revision_id: 1,
        subject: '涉嫌人乙男',
        predicate: '持被害人提款卡至ATM操作提領現金20萬元',
        object: '現金新臺幣20萬元',
        event_time: '民國113年8月10日14時30分許',
        event_location: '臺北市中正區忠孝東路一段超商ATM',
        source_type: 'PHYSICAL_EVIDENCE',
        source_ref: 'ATM交易明細表及監視器翻拍照片',
        source_excerpt: '監視器畫面顯示乙男於14時28分至32分多次插入卡片提款...',
        assertion_status: 'ADMITTED',
        confidence: 1.0,
        related_evidence: ['ATM交易紀錄', '監視器翻拍畫面', '扣案提款卡'],
        created_at: '2026-10-25T09:40:00+08:00',
        updated_at: '2026-10-25T09:40:00+08:00',
      },
      {
        id: 'fact-004',
        case_id: 'case-2026-c001-atm',
        revision_id: 1,
        subject: '涉嫌人乙男',
        predicate: '否認明知為詐騙集團贓款，抗辯為代領手續費打工',
        object: '主觀犯意認知',
        event_time: '民國113年8月10日14時45分查獲時',
        event_location: '臺北市中正區現場盤查處',
        source_type: 'SUSPECT',
        source_ref: '涉嫌人乙男供述筆錄',
        source_excerpt: '我是Telegram上有個叫飛哥的人叫我幫忙領，說一次給我3000元，我不知道卡片怎麼來的...',
        assertion_status: 'DENIED',
        confidence: 0.6,
        related_evidence: ['乙男扣案手機對話紀錄'],
        created_at: '2026-10-25T09:45:00+08:00',
        updated_at: '2026-10-25T09:45:00+08:00',
      },
      {
        id: 'fact-005',
        case_id: 'case-2026-c001-atm',
        revision_id: 1,
        subject: '指示者暱稱「飛哥」之後續金流與真實身分',
        predicate: '真實身分及款項最終交涉流向',
        object: '犯罪組織上游成員',
        event_time: '未知時段',
        event_location: '未知地點',
        source_type: 'INFERRED',
        source_ref: '通訊軟體Telegram數位鑑識初篩',
        source_excerpt: '對話帳號已銷號，僅餘文字指示及取款報酬之約定...',
        assertion_status: 'UNKNOWN',
        confidence: 0.2,
        related_evidence: ['扣案手機鑑識分析報告待送'],
        created_at: '2026-10-25T09:50:00+08:00',
        updated_at: '2026-10-25T09:50:00+08:00',
      },
    ],
    evidence_items: [
      {
        id: 'ev-01',
        case_id: 'case-2026-c001-atm',
        evidence_type: '證物（物證）',
        source_description: '甲女名下臺灣銀行提款卡2張（已發還）及現場查扣現金新臺幣20萬元（已發還）',
        collection_status: 'OBTAINED',
        created_at: '2026-10-25T09:32:00+08:00',
      },
      {
        id: 'ev-02',
        case_id: 'case-2026-c001-atm',
        evidence_type: '數位證據',
        source_description: '涉嫌人乙男持有iPhone手機2支（含Telegram對話電磁紀錄）',
        collection_status: 'OBTAINED',
        created_at: '2026-10-25T09:32:00+08:00',
      },
      {
        id: 'ev-03',
        case_id: 'case-2026-c001-atm',
        evidence_type: '影像紀錄',
        source_description: '超商ATM路口及機台監視錄影翻拍光碟1份（照片4張）',
        collection_status: 'OBTAINED',
        created_at: '2026-10-25T09:33:00+08:00',
      },
    ],
    behaviors: [
      {
        id: 'beh-01',
        case_id: 'case-2026-c001-atm',
        revision_id: 1,
        actor_ref: '電信詐欺集團成員（自稱健保局/林檢察官）',
        action_description: '冒用政府機關及公務員名義施用詐術',
        object_ref: '甲女個人財產支配權',
        time_ref: '113年8月10日10時至12時',
        fact_refs: ['fact-001', 'fact-002'],
        uncertainty_status: '上游主謀身分未明',
      },
      {
        id: 'beh-02',
        case_id: 'case-2026-c001-atm',
        revision_id: 1,
        actor_ref: '涉嫌人乙男',
        action_description: '持他人提款卡至金融機構ATM自動付款設備提領現金',
        object_ref: '現金20萬元',
        time_ref: '113年8月10日14時30分',
        fact_refs: ['fact-003', 'fact-004'],
        uncertainty_status: '客觀事實明確，爭點在於主觀不確定故意程度',
      },
    ],
    legal_candidates: [
      {
        id: 'cand-001',
        case_id: 'case-2026-c001-atm',
        revision_id: 1,
        legal_name: '刑法第339條之4 第1項第1款、第2款 加重詐欺取財罪',
        statute_ref: '中華民國刑法 §339-4 I(1)(2)',
        candidate_status: 'PRIMARY',
        statute_version: '現行有效條文（113年施行版本）',
        support_fact_refs: ['fact-001', 'fact-002', 'fact-003'],
        contrary_fact_refs: ['fact-004'],
        unknown_fact_refs: ['fact-005'],
        alternative_explanations: [
          '可能成立詐欺取財罪之共同正犯，抑或僅成立幫助犯。',
          '若涉嫌人全然無詐欺認識，可能爭執主觀無故意（但依常理非親友指示代領鉅款並收取高額報酬，具不確定故意之高度可能性）。',
        ],
        elements: [
          {
            id: 'elem-01',
            candidate_id: 'cand-001',
            element_name: '冒用政府機關或公務員名義',
            element_description: '行為人冒充公權力身分詐騙',
            related_fact_refs: ['fact-001'],
            element_status: 'SATISFIED',
            reasoning: '電話通聯與被害人陳述均明確提及健保局科長及特偵組檢察官。',
            source_ref: '刑法第339-4條第1項第1款',
          },
          {
            id: 'elem-02',
            candidate_id: 'cand-001',
            element_name: '三人以上共同犯之',
            element_description: '犯罪組織或共同正犯達三人以上',
            related_fact_refs: ['fact-001', 'fact-003', 'fact-005'],
            element_status: 'SATISFIED',
            reasoning: '包含電話前端話務員、自稱檢察官者、Telegram指示者「飛哥」及車手乙男，已逾三人分工架構。',
            source_ref: '刑法第339-4條第1項第2款',
          },
          {
            id: 'elem-03',
            candidate_id: 'cand-001',
            element_name: '主觀犯意聯絡與行為分擔',
            element_description: '涉嫌人具有共同詐欺取財之犯意認知',
            related_fact_refs: ['fact-004'],
            element_status: 'PENDING_VERIFICATION',
            reasoning: '乙男否認主觀知情，須透過對話紀錄、報酬對價、取款頻率及查獲反應進一步釐清是不確定故意或共同正犯。',
            source_ref: '最高法院107年度台上字第4225號判決意旨',
          },
        ],
        created_at: '2026-10-25T10:00:00+08:00',
      },
      {
        id: 'cand-002',
        case_id: 'case-2026-c001-atm',
        revision_id: 1,
        legal_name: '洗錢防制法第14條第1項 一般洗錢罪',
        statute_ref: '洗錢防制法 §14 I',
        candidate_status: 'ALTERNATIVE',
        statute_version: '現行有效法規',
        support_fact_refs: ['fact-003'],
        contrary_fact_refs: ['fact-004'],
        unknown_fact_refs: ['fact-005'],
        alternative_explanations: [
          '車手提領贓款並移轉占有之行為，實務上常評價為掩飾隱匿特定犯罪所得來源與去向之洗錢行為。',
        ],
        elements: [
          {
            id: 'elem-11',
            candidate_id: 'cand-002',
            element_name: '特定犯罪所得',
            element_description: '款項源於最輕本刑六月以上有期徒刑之重大犯罪（含加重詐欺）',
            related_fact_refs: ['fact-001', 'fact-002'],
            element_status: 'SATISFIED',
            reasoning: '款項係甲女遭冒名詐欺所交付，屬加重詐欺之特定犯罪所得。',
            source_ref: '洗錢防制法第3條',
          },
          {
            id: 'elem-12',
            candidate_id: 'cand-002',
            element_name: '掩飾或隱匿特定犯罪所得來源或去向',
            element_description: '提領現鈔阻斷金融金流追蹤',
            related_fact_refs: ['fact-003'],
            element_status: 'SATISFIED',
            reasoning: '將帳戶內存款轉為實體現鈔，使被害人款項脫離銀行追蹤體系。',
            source_ref: '最高法院108年度台上字第3101號判決意旨',
          },
        ],
        created_at: '2026-10-25T10:05:00+08:00',
      },
      {
        id: 'cand-003',
        case_id: 'case-2026-c001-atm',
        revision_id: 1,
        legal_name: '刑法第339條之2 由自動付款設備取得他人之物罪',
        statute_ref: '中華民國刑法 §339-2 I',
        candidate_status: 'ALTERNATIVE',
        statute_version: '現行有效法規',
        support_fact_refs: ['fact-003'],
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: [
          '若認涉嫌人非詐欺集團組織成員且未參與前階段詐術，僅持取得之卡片無權提款，可能構成§339-2。但實務通常與加重詐欺想像競合從一重處斷。',
        ],
        elements: [
          {
            id: 'elem-21',
            candidate_id: 'cand-003',
            element_name: '不正方法由自動付款設備取得他人之物',
            element_description: '輸入非合法授權密碼提領金錢',
            related_fact_refs: ['fact-003'],
            element_status: 'SATISFIED',
            reasoning: '非卡片合法授權人，持被害人受詐交付之密碼至機台提款。',
            source_ref: '刑法第339-2條',
          },
        ],
        created_at: '2026-10-25T10:10:00+08:00',
      },
      {
        id: 'cand-004',
        case_id: 'case-2026-c001-atm',
        revision_id: 1,
        legal_name: '刑法第337條 侵占離本人持有物罪（替代排除論述）',
        statute_ref: '中華民國刑法 §337',
        candidate_status: 'REJECTED',
        exclusion_reason: '涉嫌人持有提款卡係由他人指示自變電箱特定隱蔽點起獲，非偶然路過拾得無主遺失物，且持有密碼連續提領，不符單純侵占遺失物要件。',
        statute_version: '現行有效法規',
        support_fact_refs: [],
        contrary_fact_refs: ['fact-002', 'fact-003'],
        unknown_fact_refs: [],
        alternative_explanations: ['涉嫌人若抗辯「路上撿到錢包有卡片嘗試提款」，已被現場採證與通訊軟體指示事實排除。'],
        elements: [],
        created_at: '2026-10-25T10:15:00+08:00',
      },
    ],
    core_issues: [
      {
        id: 'issue-01',
        case_id: 'case-2026-c001-atm',
        candidate_id: 'cand-001',
        issue_description: '涉嫌人乙男對「款項係詐欺贓款」是否具有未必故意（不確定故意）？',
        supporting_facts: ['不合理之3,000元代領單筆高額酬金', '使用匿名軟體Telegram聯繫', '提款卡取自變電箱後方非正常交付管道'],
        contrary_facts: ['涉嫌人辯稱僅為打工代領不知情'],
        unresolved_questions: ['是否曾有其他帳戶代領紀錄？', '與「飛哥」之歷史對話是否提及封鎖或警察盤查？'],
        priority: 'HIGH',
      },
      {
        id: 'issue-02',
        case_id: 'case-2026-c001-atm',
        candidate_id: 'cand-002',
        issue_description: '提領後之現金去向是否意圖移轉、交付他人或製造金流斷點？',
        supporting_facts: ['隨身持有20萬元現金準備轉交', '手機內有下一個交款地點指示'],
        contrary_facts: [],
        unresolved_questions: ['是否有接應手（收水）之具體特徵？'],
        priority: 'HIGH',
      },
    ],
    questions: [
      {
        id: 'q-001',
        case_id: 'case-2026-c001-atm',
        candidate_id: 'cand-001',
        element_id: 'elem-03',
        question_type: '1_CORE_ELEMENT',
        question_text: '你於何時、何地，透過何種管道認識指示你提款之人？雙方約定之代價或報酬為何？',
        rationale: '釐清是否具備共同正犯之犯意聯絡或對於詐欺贓款具有不確定故意。',
        target_fact_refs: ['fact-004'],
        priority: 'P0_CRITICAL',
        review_status: 'APPROVED',
        is_required: true,
        revision_number: 1,
        expected_clarification: '取得通訊軟體聯繫方式、約定金額、工作內容細節。',
      },
      {
        id: 'q-002',
        case_id: 'case-2026-c001-atm',
        candidate_id: 'cand-001',
        element_id: 'elem-03',
        question_type: '2_ACT_PROCESS',
        question_text: '你前往變電箱取得提款卡之確切時間？卡片取得時之外包裝為何？密碼係由何人以何種方式告知？',
        rationale: '確認取得卡片之異常交付方式，排除正常商業借貸或正當授權。',
        target_fact_refs: ['fact-002', 'fact-003'],
        priority: 'P0_CRITICAL',
        review_status: 'APPROVED',
        is_required: true,
        revision_number: 1,
        expected_clarification: '確認隱蔽置放點取物之異常性。',
      },
      {
        id: 'q-003',
        case_id: 'case-2026-c001-atm',
        candidate_id: 'cand-001',
        element_id: 'elem-03',
        question_type: '3_SUBJECTIVE_INTENT',
        question_text: '對方要求你使用他人名義之提款卡提領高額現金，且約定於變電箱隱密處取卡，你主觀上是否曾懷疑該款項涉及違法或犯罪不法所得？',
        rationale: '針對主觀不確定故意建立直接筆錄問答，遵守中性詢問避免誘導。',
        target_fact_refs: ['fact-004'],
        priority: 'P0_CRITICAL',
        review_status: 'APPROVED',
        is_required: true,
        revision_number: 1,
        expected_clarification: '記錄涉嫌人對異常情境之主觀認知與警覺程度。',
      },
      {
        id: 'q-004',
        case_id: 'case-2026-c001-atm',
        candidate_id: 'cand-001',
        question_type: '4_TIME_LOCATION_PERSON',
        question_text: '除本次遭查獲之20萬元外，今日是否尚有前往其他超商、郵局或金融機構ATM提領款項？如有，地點及次數為何？',
        rationale: '查證是否有其他潛在被害人或同一連續提領行為。',
        target_fact_refs: ['fact-003'],
        priority: 'P1_IMPORTANT',
        review_status: 'APPROVED',
        is_required: true,
        revision_number: 1,
        expected_clarification: '清查有無擴大清查必要之關聯案件。',
      },
      {
        id: 'q-005',
        case_id: 'case-2026-c001-atm',
        candidate_id: 'cand-002',
        question_type: '5_FLOW_OF_PROPERTY',
        question_text: '提領出之現金新臺幣20萬元，對方指示你後續如何交涉？交款對象是何人？約定交款之地點、時間及識別暗號為何？',
        rationale: '釐清洗錢防制法之去向切斷要件，並利於線上即時查緝收水共犯。',
        target_fact_refs: ['fact-005'],
        priority: 'P0_CRITICAL',
        review_status: 'APPROVED',
        is_required: true,
        revision_number: 1,
        expected_clarification: '掌握收水人員特徵、聯繫方式及交款約定。',
      },
      {
        id: 'q-006',
        case_id: 'case-2026-c001-atm',
        candidate_id: 'cand-001',
        question_type: '6_EVIDENCE_SOURCE',
        question_text: '警方現場所扣押之相關證物是否均為你本人所有及持有？有無其他相關紀錄可供查證？',
        rationale: '確立證據保管鏈與證物關聯性。',
        target_fact_refs: ['fact-004'],
        priority: 'P1_IMPORTANT',
        review_status: 'APPROVED',
        is_required: true,
        revision_number: 1,
        expected_clarification: '確認數位證據扣押合法性與密碼提供。',
      },
      {
        id: 'q-007',
        case_id: 'case-2026-c001-atm',
        candidate_id: 'cand-004',
        question_type: '7_CONTRARY_ALTERNATIVE',
        question_text: '你是否曾向警方抗辯該提款卡係路上拾得？若非拾得，你與卡片名義人甲女之間是否存在任何金錢借貸、買賣或親友委託關係？',
        rationale: '正式於筆錄中檢驗並排除侵占遺失物或民事糾紛等替代抗辯事由。',
        target_fact_refs: ['fact-002', 'fact-004'],
        priority: 'P1_IMPORTANT',
        review_status: 'APPROVED',
        is_required: true,
        revision_number: 1,
        expected_clarification: '明確排除民事借貸抗辯或無因管理說詞。',
      },
      {
        id: 'q-008',
        case_id: 'case-2026-c001-atm',
        candidate_id: 'cand-001',
        question_type: '8_CONTRADICTION_SUPPLEMENT',
        question_text: '你陳稱不清楚款項為詐騙所得，惟依手機對話顯示，對方曾指示「若遇警察盤查就說幫朋友領錢」，對此作何解釋？',
        rationale: '對客觀證據與涉嫌人口供矛盾處進行補充追問，維護偵查真實。',
        target_fact_refs: ['fact-004'],
        priority: 'P1_IMPORTANT',
        review_status: 'APPROVED',
        is_required: true,
        revision_number: 1,
        expected_clarification: '直面反證釐清教戰守則之認知。',
      },
      {
        id: 'q-009',
        case_id: 'case-2026-c001-atm',
        candidate_id: 'cand-001',
        question_type: '9_UNRESOLVED_INQUIRY',
        question_text: '除上述陳述外，有無其他有利證據提出或尚待查明之證人？',
        rationale: '落實刑事訴訟法第2條注意對被告有利及不利情形規定。',
        target_fact_refs: ['fact-005'],
        priority: 'P2_SUPPLEMENTAL',
        review_status: 'APPROVED',
        is_required: true,
        revision_number: 1,
        expected_clarification: '保障被告防禦權與調查有利證據。',
      },
    ],
    answers: [
      {
        id: 'ans-001',
        question_id: 'q-001',
        answer_text:
          '我是上個禮拜在Telegram打工群組看到兼職跑腿廣告，私訊一個叫「飛哥」的人。他說是做虛擬貨幣代購，只要幫客戶去指定地方拿卡提款，一筆給我3000元，提完款去台北車站地下街交給另一個人。',
        respondent_role: 'SUSPECT',
        created_at: '2026-10-25T11:00:00+08:00',
      },
      {
        id: 'ans-002',
        question_id: 'q-003',
        answer_text:
          '我當時有問他為什麼不自己領，他說他在國外，卡片放在變電箱是因為客戶放在那裡。我雖然覺得有點怪怪的，但因為缺錢急著用，就沒有多想...',
        respondent_role: 'SUSPECT',
        created_at: '2026-10-25T11:15:00+08:00',
      },
    ],
    reports: [
      {
        id: 'rep-001',
        case_id: 'case-2026-c001-atm',
        revision_id: 1,
        station: '臺北市政府警察局中正第一分局忠孝西路派出所',
        report_type: '查獲',
        title_reason: '疑涉刑法第339條之4加重詐欺取財罪及洗錢防制法案',
        status_marker: '破獲',
        incident_time_roc: '民國113年8月10日10時00分許',
        incident_location: '臺北市中正區忠孝東路一段○○號超商ATM',
        report_time_roc: '民國113年8月10日14時10分許',
        clearance_time_roc: '民國113年8月10日14時30分許',
        summary_text:
          '緣報案人甲女於民國113年8月10日10時許接獲自稱健保局及檢察官人員來電，佯稱健保卡遭冒用涉案，誘使甲女將名下臺灣銀行提款卡2張置於本轄濟南路一段變電箱後方。同日14時30分許，涉嫌人乙男持該卡於超商ATM接續提領新臺幣20萬元時，為本所巡邏員警當場查獲，當場起獲提款卡2張、贓款20萬元（已發還被害人）及犯案手機2支。全案移送臺灣臺北地方檢察署偵辦。',
        certificate_number: '北市警中正一分刑受字第113081001號',
        women_child_number: '無',
        c165_number: 'C1130810-0982號',
        jurisdiction: '臺灣臺北地方檢察署',
        handling_officer: '警員 林○○',
        is_approved: true,
        generated_at: '2026-10-25T16:00:00+08:00',
        validation_errors: [],
      },
    ],
    reviews: [
      {
        id: 'rev-001',
        case_id: 'case-2026-c001-atm',
        gate_name: 'GATE1_FACTS',
        target_revision_id: 1,
        review_status: 'APPROVED',
        reviewer_id: 'usr_tw_police_88014',
        comments: '事實拆解已完整區分客觀提款行為與主觀否認狀態，符合規範。',
        reviewed_at: '2026-10-25T09:55:00+08:00',
      },
      {
        id: 'rev-002',
        case_id: 'case-2026-c001-atm',
        gate_name: 'GATE2_LEGAL',
        target_revision_id: 1,
        review_status: 'APPROVED',
        reviewer_id: 'usr_tw_police_88014',
        comments: '保留加重詐欺、一般洗錢與自動付款設備取財罪等替代方向，符合多重法律評估要求。',
        reviewed_at: '2026-10-25T10:20:00+08:00',
      },
    ],
    audit_logs: [
      {
        id: 'aud-001',
        actor_id: 'usr_tw_police_88014',
        case_id: 'case-2026-c001-atm',
        event_type: 'CASE_CREATED',
        target_type: 'CASE',
        target_id: 'case-2026-c001-atm',
        occurred_at: '2026-10-25T09:30:00+08:00',
        details: '初始建立案件檔案，寫入原始報案摘要（Gate 0）',
      },
      {
        id: 'aud-002',
        actor_id: 'usr_tw_police_88014',
        case_id: 'case-2026-c001-atm',
        event_type: 'GATE1_APPROVED',
        target_type: 'FACTS',
        target_id: 'rev-1',
        occurred_at: '2026-10-25T09:55:00+08:00',
        details: '承辦人完成事實拆解審核，核准進入 Gate 2',
      },
    ],
  },
  {
    id: 'case-2026-c002-wallet',
    title: '臺北市中山分局—咖啡廳皮夾遺忘拾得與感應盜刷案',
    status: 'ACTIVE',
    stage: 'GATE2_LEGAL',
    current_revision: 1,
    created_at: '2026-10-26T14:20:00+08:00',
    updated_at: '2026-10-26T16:40:00+08:00',
    owner_id: 'usr_tw_police_88014',
    raw_intake: {
      summary:
        '報案人丙男稱於民國113年7月5日16時許在臺北市中山區南京西路某咖啡廳如廁，將皮夾置於洗手台上遺忘。涉嫌人丁女隨後進入取走該皮夾，並持內附玉山銀行信用卡於隔壁藥妝店感應消費新臺幣3,500元。丁女辯稱以為是無人要的皮夾撿去用，不知道要送派出所。案經調閱監視器循線通知丁女到案。',
      supplementary_notes: '發票明細1張、簽帳電磁紀錄、監視錄影翻拍照片4張。皮夾及信用卡已發還。',
      analysis_remarks: '核心爭點在於侵占遺失物（§337）與竊盜罪（§320）之界線，以及詐欺罪之牽連關係。',
      created_at: '2026-10-26T14:20:00+08:00',
    },
    facts: [
      {
        id: 'fact-w-001',
        case_id: 'case-2026-c002-wallet',
        revision_id: 1,
        subject: '報案人丙男',
        predicate: '將皮夾置於咖啡廳洗手台遺忘離去',
        object: '內含現金2,000元及信用卡之皮夾',
        event_time: '民國113年7月5日16時許',
        event_location: '臺北市中山區南京西路咖啡廳化妝室',
        source_type: 'VICTIM',
        source_ref: '丙男報案筆錄',
        source_excerpt: '我上廁所洗手把皮夾放在洗手台，走回座位約5分鐘想起回去找就不見了...',
        assertion_status: 'ASSERTED',
        confidence: 0.95,
        related_evidence: ['咖啡廳走道監視器畫面'],
        created_at: '2026-10-26T14:25:00+08:00',
        updated_at: '2026-10-26T14:25:00+08:00',
      },
      {
        id: 'fact-w-002',
        case_id: 'case-2026-c002-wallet',
        revision_id: 1,
        subject: '涉嫌人丁女',
        predicate: '自洗手台取走他人皮夾入己持有',
        object: '丙男所有之皮夾',
        event_time: '民國113年7月5日16時05分許',
        event_location: '咖啡廳洗手台',
        source_type: 'SUSPECT',
        source_ref: '丁女偵訊筆錄',
        source_excerpt: '我看到洗手台上有個皮夾，旁邊沒人，我就拿走了...',
        assertion_status: 'ADMITTED',
        confidence: 1.0,
        related_evidence: ['監視器錄影光碟'],
        created_at: '2026-10-26T14:30:00+08:00',
        updated_at: '2026-10-26T14:30:00+08:00',
      },
      {
        id: 'fact-w-003',
        case_id: 'case-2026-c002-wallet',
        revision_id: 1,
        subject: '涉嫌人丁女',
        predicate: '持皮夾內信用卡感應刷卡消費購買化妝品',
        object: '玉山銀行信用卡與新臺幣3,500元商品',
        event_time: '民國113年7月5日16時20分許',
        event_location: '隔壁藥妝門市',
        source_type: 'PHYSICAL_EVIDENCE',
        source_ref: '特約商店簽帳紀錄及發票',
        source_excerpt: '丁女持該卡免簽名感應過卡成功消費3,500元...',
        assertion_status: 'ADMITTED',
        confidence: 1.0,
        related_evidence: ['發票收執聯', '簽帳電磁紀錄'],
        created_at: '2026-10-26T14:35:00+08:00',
        updated_at: '2026-10-26T14:35:00+08:00',
      },
      {
        id: 'fact-w-004',
        case_id: 'case-2026-c002-wallet',
        revision_id: 1,
        subject: '涉嫌人丁女',
        predicate: '辯稱以為是無主棄物，不知道應送交警察局',
        object: '主觀認知',
        event_time: '查獲到案時',
        event_location: '中山分局偵訊室',
        source_type: 'SUSPECT',
        source_ref: '丁女調查筆錄',
        source_excerpt: '我以為是人家不要的，不知道那是犯罪...',
        assertion_status: 'DENIED',
        confidence: 0.5,
        related_evidence: [],
        created_at: '2026-10-26T14:40:00+08:00',
        updated_at: '2026-10-26T14:40:00+08:00',
      },
    ],
    evidence_items: [
      {
        id: 'ev-w01',
        case_id: 'case-2026-c002-wallet',
        evidence_type: '物證',
        source_description: '黑色真皮皮夾1只、玉山銀行信用卡1張（均發還被害人）',
        collection_status: 'OBTAINED',
        created_at: '2026-10-26T14:22:00+08:00',
      },
      {
        id: 'ev-w02',
        case_id: 'case-2026-c002-wallet',
        evidence_type: '書證',
        source_description: '藥妝店發票影本、玉山銀行信用卡刷卡通知紀錄',
        collection_status: 'OBTAINED',
        created_at: '2026-10-26T14:23:00+08:00',
      },
    ],
    behaviors: [
      {
        id: 'beh-w01',
        case_id: 'case-2026-c002-wallet',
        revision_id: 1,
        actor_ref: '涉嫌人丁女',
        action_description: '在特定場域（咖啡廳洗手間）取走他人暫時脫離持有之動產',
        object_ref: '丙男皮夾',
        time_ref: '113年7月5日16時05分',
        fact_refs: ['fact-w-001', 'fact-w-002'],
        uncertainty_status: '皮夾是否仍在丙男或咖啡廳店長監督持有下之法律評價爭議',
      },
      {
        id: 'beh-w02',
        case_id: 'case-2026-c002-wallet',
        revision_id: 1,
        actor_ref: '涉嫌人丁女',
        action_description: '持他人信用卡冒名感應消費獲取財物',
        object_ref: '價值3,500元之商品',
        time_ref: '113年7月5日16時20分',
        fact_refs: ['fact-w-003'],
        uncertainty_status: '客觀事實明確，構成刑法第339條第1項詐欺取財罪無疑',
      },
    ],
    legal_candidates: [
      {
        id: 'cand-w01',
        case_id: 'case-2026-c002-wallet',
        revision_id: 1,
        legal_name: '刑法第337條 侵占離本人持有物罪',
        statute_ref: '中華民國刑法 §337',
        candidate_status: 'PRIMARY',
        statute_version: '現行有效法規',
        support_fact_refs: ['fact-w-001', 'fact-w-002'],
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: [
          '若認丙男走出洗手間回到座位，皮夾已脫離其直接支配範圍，且咖啡廳主管未及建立支配，丁女行為該當侵占遺失物。',
        ],
        elements: [
          {
            id: 'elem-w11',
            candidate_id: 'cand-w01',
            element_name: '遺失物或離本人持有之物',
            element_description: '非基於本人意思而偶然脫離其實力管領範圍之物',
            related_fact_refs: ['fact-w-001'],
            element_status: 'SATISFIED',
            reasoning: '被害人如廁遺忘洗手台，客觀上已暫時脫離持有。',
            source_ref: '最高法院50年台上字第2031號判例',
          },
        ],
        created_at: '2026-10-26T14:45:00+08:00',
      },
      {
        id: 'cand-w02',
        case_id: 'case-2026-c002-wallet',
        revision_id: 1,
        legal_name: '刑法第320條第1項 普通竊盜罪（替代法律方向）',
        statute_ref: '中華民國刑法 §320 I',
        candidate_status: 'ALTERNATIVE',
        statute_version: '現行有效法規',
        support_fact_refs: ['fact-w-001'],
        contrary_fact_refs: ['fact-w-004'],
        unknown_fact_refs: [],
        alternative_explanations: [
          '實務部分見解認為：在封閉之營業場所（如咖啡廳、餐廳），顧客暫時遺忘之物品，場所主人具有概括監督支配權，非離本人持有物；未得同意取走仍構成竊盜。',
        ],
        elements: [
          {
            id: 'elem-w21',
            candidate_id: 'cand-w02',
            element_name: '他人管領力下之動產',
            element_description: '物仍在被害人或場所管理者之支配範圍內',
            related_fact_refs: ['fact-w-001'],
            element_status: 'PENDING_VERIFICATION',
            reasoning: '場所支配力程度與被害人察覺間隔時間（僅5分鐘）需綜合判斷。',
            source_ref: '刑法第320條',
          },
        ],
        created_at: '2026-10-26T14:50:00+08:00',
      },
      {
        id: 'cand-w03',
        case_id: 'case-2026-c002-wallet',
        revision_id: 1,
        legal_name: '刑法第339條第1項 詐欺取財罪（盜刷部分）',
        statute_ref: '中華民國刑法 §339 I',
        candidate_status: 'PRIMARY',
        statute_version: '現行有效法規',
        support_fact_refs: ['fact-w-003'],
        contrary_fact_refs: [],
        unknown_fact_refs: [],
        alternative_explanations: [
          '無權使用他人信用卡感應過卡，使特約商店店員陷於錯誤而交付財物。',
        ],
        elements: [
          {
            id: 'elem-w31',
            candidate_id: 'cand-w03',
            element_name: '施用詐術使人交付財物',
            element_description: '冒充合法持卡人身分行使權利',
            related_fact_refs: ['fact-w-003'],
            element_status: 'SATISFIED',
            reasoning: '感應他人信用卡獲取價值3,500元化妝品。',
            source_ref: '刑法第339條',
          },
        ],
        created_at: '2026-10-26T14:55:00+08:00',
      },
    ],
    core_issues: [
      {
        id: 'issue-w01',
        case_id: 'case-2026-c002-wallet',
        candidate_id: 'cand-w01',
        issue_description: '取走皮夾當時，該物究屬「離本人持有物」抑或仍在「被害人/店長管領下」？',
        supporting_facts: ['被害人忘記拿皮夾離開5分鐘', '咖啡廳洗手間屬半公開營業空間'],
        contrary_facts: [],
        unresolved_questions: ['店員是否知悉洗手間有遺落皮夾？'],
        priority: 'HIGH',
      },
    ],
    questions: [],
    answers: [],
    reports: [
      {
        id: 'rep-w01',
        case_id: 'case-2026-c002-wallet',
        revision_id: 1,
        station: '臺北市政府警察局中山分局長春路派出所',
        report_type: '受理',
        title_reason: '疑涉刑法侵占離本人持有物罪及詐欺取財罪案',
        status_marker: '受理',
        incident_time_roc: '民國113年7月5日16時00分許',
        incident_location: '臺北市中山區南京西路○○號咖啡廳及隔壁藥妝店',
        report_time_roc: '民國113年7月5日17時10分許',
        summary_text:
          '緣報案人丙男於民國113年7月5日16時許在咖啡廳洗手間將皮夾置於洗手台遺忘，涉嫌人丁女取走該皮夾後，持內附信用卡於隔壁藥妝店盜刷消費新臺幣3,500元。案經調閱監視器確認丁女身分循線通知到案，全案依侵占離本人持有物及詐欺取財罪嫌陳報臺灣臺北地方檢察署。',
        certificate_number: '北市警中山分刑受字第113070501號',
        women_child_number: '無',
        c165_number: '無',
        jurisdiction: '臺灣臺北地方檢察署',
        handling_officer: '警員 陳○○',
        is_approved: false,
        generated_at: '2026-10-26T17:00:00+08:00',
        validation_errors: [],
      },
    ],
    reviews: [
      {
        id: 'rev-w01',
        case_id: 'case-2026-c002-wallet',
        gate_name: 'GATE1_FACTS',
        target_revision_id: 1,
        review_status: 'APPROVED',
        reviewer_id: 'usr_tw_police_88014',
        comments: '事實拆解完整，明確區分皮夾取得與後續刷卡兩個行為階段。',
        reviewed_at: '2026-10-26T15:00:00+08:00',
      },
    ],
    audit_logs: [
      {
        id: 'aud-w01',
        actor_id: 'usr_tw_police_88014',
        case_id: 'case-2026-c002-wallet',
        event_type: 'CASE_CREATED',
        target_type: 'CASE',
        target_id: 'case-2026-c002-wallet',
        occurred_at: '2026-10-26T14:20:00+08:00',
        details: '建立案件及初始案情摘要（Gate 0）',
      },
    ],
  },
];

export class StorageService {
  private static getStoredCases(): CaseRecord[] {
    const raw = localStorage.getItem(STORAGE_KEY_CASES);
    if (!raw) {
      localStorage.setItem(STORAGE_KEY_CASES, JSON.stringify(SEED_CASES));
      return SEED_CASES;
    }
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      return SEED_CASES;
    } catch {
      return SEED_CASES;
    }
  }

  static getCases(): CaseRecord[] {
    return this.getStoredCases();
  }

  static getCase(id: string): CaseRecord | undefined {
    return this.getStoredCases().find((c) => c.id === id);
  }

  static saveCase(updatedCase: CaseRecord): void {
    const cases = this.getStoredCases();
    const index = cases.findIndex((c) => c.id === updatedCase.id);
    updatedCase.updated_at = new Date().toISOString();
    if (index >= 0) {
      cases[index] = updatedCase;
    } else {
      cases.unshift(updatedCase);
    }
    localStorage.setItem(STORAGE_KEY_CASES, JSON.stringify(cases));
  }

  static resetToSeedData(): void {
    localStorage.setItem(STORAGE_KEY_CASES, JSON.stringify(SEED_CASES));
    localStorage.setItem(STORAGE_KEY_SETTINGS, JSON.stringify(INITIAL_SETTINGS));
    this.addAuditLog({
      id: `aud-${Date.now()}`,
      actor_id: 'usr_tw_police_88014',
      event_type: 'DATABASE_RESET',
      target_type: 'SYSTEM',
      target_id: 'seed_restore',
      occurred_at: new Date().toISOString(),
      details: '重設沙盒展示資料庫至初始乾淨狀態',
    });
  }

  static createCase(intake: {
    title?: string;
    summary: string;
    supplementary_notes?: string;
    analysis_remarks?: string;
  }): CaseRecord {
    const now = new Date().toISOString();
    const id = `case-${Date.now().toString().slice(-6)}-${Math.random().toString(36).substring(2, 6)}`;
    const newCase: CaseRecord = {
      id,
      title: intake.title?.trim() || `新案件 ${new Date().toLocaleDateString('zh-TW')}`,
      status: 'ACTIVE',
      stage: 'GATE1_FACTS',
      current_revision: 1,
      created_at: now,
      updated_at: now,
      owner_id: 'usr_tw_police_88014',
      raw_intake: {
        summary: intake.summary,
        supplementary_notes: intake.supplementary_notes,
        analysis_remarks: intake.analysis_remarks,
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
      audit_logs: [
        {
          id: `aud-${Date.now()}`,
          actor_id: 'usr_tw_police_88014',
          case_id: id,
          event_type: 'CASE_CREATED',
          target_type: 'CASE',
          target_id: id,
          occurred_at: now,
          details: '建立案件及初始案情摘要（Gate 0 完成）',
        },
      ],
    };

    const cases = this.getStoredCases();
    cases.unshift(newCase);
    localStorage.setItem(STORAGE_KEY_CASES, JSON.stringify(cases));
    return newCase;
  }

  /**
   * 規格第4.3條核心要求：
   * 「Gate 1 修改後，所有依賴舊事實版本的後續審核均應標記為過期 (STALE)，並要求重新分析或確認。」
   */
  static invalidateLaterGates(caseRecord: CaseRecord, modifiedGate: GateStage): CaseRecord {
    const updated = { ...caseRecord };
    updated.current_revision += 1;
    const gateOrder: GateStage[] = [
      'GATE0_INTAKE',
      'GATE1_FACTS',
      'GATE2_LEGAL',
      'GATE3_QUESTIONS',
      'GATE4_ANSWERS',
      'GATE5_DOCUMENTS',
    ];
    const modIndex = gateOrder.indexOf(modifiedGate);

    // 把修改點之後的所有 review 標記為 STALE
    updated.reviews = updated.reviews.map((r) => {
      const rIndex = gateOrder.indexOf(r.gate_name);
      if (rIndex > modIndex && r.review_status === 'APPROVED') {
        return {
          ...r,
          review_status: 'STALE',
          comments: `${r.comments}（因前置 ${modifiedGate} 事實異動，歷史審核已過期失效）`,
        };
      }
      return r;
    });

    this.saveCase(updated);
    this.addAuditLog({
      id: `aud-${Date.now()}`,
      actor_id: updated.owner_id,
      case_id: updated.id,
      event_type: 'STAGE_INVALIDATED',
      target_type: 'GATE_CASCADE',
      target_id: modifiedGate,
      occurred_at: new Date().toISOString(),
      details: `因修改 ${modifiedGate}，版本提升至 Rev ${updated.current_revision}，後續審核標記為 STALE`,
    });

    return updated;
  }

  static getSettings(): SystemSettings {
    const raw = localStorage.getItem(STORAGE_KEY_SETTINGS);
    if (!raw) {
      localStorage.setItem(STORAGE_KEY_SETTINGS, JSON.stringify(INITIAL_SETTINGS));
      return INITIAL_SETTINGS;
    }
    try {
      return JSON.parse(raw);
    } catch {
      return INITIAL_SETTINGS;
    }
  }

  static saveSettings(settings: SystemSettings): void {
    localStorage.setItem(STORAGE_KEY_SETTINGS, JSON.stringify(settings));
    this.addAuditLog({
      id: `aud-${Date.now()}`,
      actor_id: settings.single_owner_id,
      event_type: 'SETTINGS_UPDATED',
      target_type: 'SYSTEM',
      target_id: 'global',
      occurred_at: new Date().toISOString(),
      details: `更新系統設定（外部 AI 傳輸: ${settings.allow_external_ai ? '開啟' : '關閉'}）`,
    });
  }

  static getAuditLogs(): AuditEvent[] {
    const raw = localStorage.getItem(STORAGE_KEY_AUDIT);
    if (!raw) return [];
    try {
      return JSON.parse(raw);
    } catch {
      return [];
    }
  }

  static addAuditLog(event: AuditEvent): void {
    const logs = this.getAuditLogs();
    logs.unshift(event);
    if (logs.length > 500) logs.pop();
    localStorage.setItem(STORAGE_KEY_AUDIT, JSON.stringify(logs));
  }

  // 登入狀態管理
  static getAuthSession(): { authenticated: boolean; user: string; lockoutUntil?: number } {
    const raw = localStorage.getItem(STORAGE_KEY_AUTH);
    if (!raw) return { authenticated: true, user: '警員 林○○ (核准公務帳號)' };
    try {
      return JSON.parse(raw);
    } catch {
      return { authenticated: true, user: '警員 林○○ (核准公務帳號)' };
    }
  }

  static setAuthSession(session: { authenticated: boolean; user: string; lockoutUntil?: number }): void {
    localStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(session));
  }

  // 匯出工具
  static exportMarkdown(caseRecord: CaseRecord): string {
    return `# 刑事案件偵查輔助分析報告：${caseRecord.title}

- 案件識別碼：\`${caseRecord.id}\`
- 目前階段：${caseRecord.stage}
- 案件版本：Revision ${caseRecord.current_revision}
- 建立時間：${caseRecord.created_at}
- 最近更新：${caseRecord.updated_at}
- 承辦人員：${caseRecord.owner_id}

---

## 1. 原始案情（Gate 0）
${caseRecord.raw_intake.summary}

${caseRecord.raw_intake.supplementary_notes ? `> 補充資訊：${caseRecord.raw_intake.supplementary_notes}\n` : ''}

---

## 2. 結構化事實清單（Gate 1）
${caseRecord.facts
  .map(
    (f, idx) => `### 事實 ${idx + 1}（${f.assertion_status}）
- 主體：${f.subject}
- 行為：${f.predicate}
- 客體：${f.object}
- 時間：${f.event_time}
- 地點：${f.event_location}
- 來源類型：${f.source_type}（來源依據：${f.source_ref}）
- 摘錄片段：「${f.source_excerpt}」
`
  )
  .join('\n')}

---

## 3. 候選法律方向與構成要件（Gate 2）
${caseRecord.legal_candidates
  .map(
    (c, idx) => `### 方向 ${idx + 1}：${c.legal_name}（狀態：${c.candidate_status}）
- 依據法條：${c.statute_ref}（版本：${c.statute_version}）
${c.exclusion_reason ? `- 排除理由：${c.exclusion_reason}\n` : ''}
${c.elements
  .map(
    (e) => `  - 要件【${e.element_name}】：${e.element_status}
    - 說明：${e.element_description}
    - 理由：${e.reasoning}`
  )
  .join('\n')}
`
  )
  .join('\n')}

---

## 4. 筆錄問句規劃（Gate 3）
${caseRecord.questions
  .map(
    (q, idx) => `${idx + 1}. 【${q.priority} · ${q.question_type}】
問：${q.question_text}
（待證目的：${q.rationale}｜審核狀態：${q.review_status}）`
  )
  .join('\n\n')}

---

## 5. 警政公務條陳（Gate 5）
${
  caseRecord.reports[0]
    ? `${caseRecord.reports[0].station} 報告
一、案由：${caseRecord.reports[0].title_reason}（${caseRecord.reports[0].status_marker}）
二、發生時間：${caseRecord.reports[0].incident_time_roc}
三、發生地點：${caseRecord.reports[0].incident_location}
四、報案時間：${caseRecord.reports[0].report_time_roc}
五、案情摘要：${caseRecord.reports[0].summary_text}
六、後續處置：
（一）依規定陳報（證明單案號：${caseRecord.reports[0].certificate_number}、婦幼案號：${caseRecord.reports[0].women_child_number}、165案號：${caseRecord.reports[0].c165_number}）
（二）本案管轄：${caseRecord.reports[0].jurisdiction}
（三）處理員警：${caseRecord.reports[0].handling_officer}
`
    : '（條陳尚未產製）'
}

---
*聲明：本文件為系統輔助整理之分析紀錄，僅供司法警察人員參考，不得直接作為司法機關正式裁判或處分依據。*
`;
  }
}
