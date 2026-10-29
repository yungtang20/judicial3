export type AssertionStatus = 'ASSERTED' | 'ADMITTED' | 'DENIED' | 'INFERRED' | 'UNKNOWN';

export type SourceType = 'VICTIM' | 'SUSPECT' | 'WITNESS' | 'POLICE_RECORD' | 'PHYSICAL_EVIDENCE' | 'INFERRED';

export type GateStage = 'GATE0_INTAKE' | 'GATE1_FACTS' | 'GATE2_LEGAL' | 'GATE3_QUESTIONS' | 'GATE4_ANSWERS' | 'GATE5_DOCUMENTS';

export type ReviewStatus = 'DRAFT' | 'IN_REVIEW' | 'APPROVED' | 'REVISED' | 'STALE' | 'REJECTED';

export type CandidateStatus = 'PRIMARY' | 'ALTERNATIVE' | 'LOW_CONFIDENCE' | 'REJECTED' | 'UNRESOLVED';

export type ElementStatus =
  | 'SATISFIED'           // 構成要件已獲足夠事證支持
  | 'UNSUPPORTED'         // 經調查事證不支持或遭排除
  | 'CONTESTED'           // 存有重大正反矛盾或爭議抗辯
  | 'INSUFFICIENT_DATA'   // 資料不足，尚待進一步查證（不得直接視為不成立）
  | 'PENDING_VERIFICATION';// 待筆錄或客觀證據查核

export type QuestionPriority = 'P0_CRITICAL' | 'P1_IMPORTANT' | 'P2_SUPPLEMENTAL';

export type QuestionType =
  | '1_CORE_ELEMENT'             // 核心構成要件問句
  | '2_ACT_PROCESS'              // 行為經過問句
  | '3_SUBJECTIVE_INTENT'        // 主觀認知及意思問句
  | '4_TIME_LOCATION_PERSON'     // 時間、地點及人物關係問句
  | '5_FLOW_OF_PROPERTY'         // 財物、款項、工具或資料流向問句
  | '6_EVIDENCE_SOURCE'          // 證據及來源問句
  | '7_CONTRARY_ALTERNATIVE'     // 反向事實及替代解釋問句
  | '8_CONTRADICTION_SUPPLEMENT' // 矛盾與補充問句
  | '9_UNRESOLVED_INQUIRY';      // 尚待查明事項問句

export interface FactItem {
  id: string;
  case_id: string;
  revision_id: number;
  subject: string;
  predicate: string;
  object: string;
  time?: string;
  location?: string;
  event_time: string;
  event_location: string;
  source_type: SourceType;
  source_ref: string;
  source_excerpt: string;
  assertion_status: AssertionStatus;
  confidence: number;
  related_evidence: string[];
  created_at: string;
  updated_at: string;
}

export interface EvidenceItem {
  id: string;
  case_id: string;
  evidence_type: string;
  source_description: string;
  collection_status: 'OBTAINED' | 'REQUESTED' | 'PENDING_SEARCH' | 'UNAVAILABLE';
  related_fact_refs?: string[];
  limitations?: string; // 證據證明力界限（不得把當事人陳述當作客觀證據證實）
  created_at: string;
}

export interface BehaviorItem {
  id: string;
  case_id: string;
  revision_id: number;
  actor_ref: string;
  action_description: string;
  object_ref: string;
  time_ref: string;
  sequence_order?: number;
  means?: string;
  result?: string;
  fact_refs: string[];
  evidence_refs?: string[];
  uncertainty_status: string;
}

export interface LegalElement {
  id: string;
  candidate_id: string;
  legal_norm?: string;
  norm_version?: string;
  element_name: string;
  element_description: string;
  supporting_fact_refs?: string[];
  contrary_fact_refs?: string[];
  related_evidence_refs?: string[];
  missing_information?: string[];
  related_fact_refs: string[];
  element_status: ElementStatus;
  reasoning: string;
  source_ref: string;
  requires_human_review?: boolean;
}

export interface LegalCandidate {
  id: string;
  case_id: string;
  revision_id: number;
  legal_name: string;
  statute_ref: string;
  candidate_status: CandidateStatus;
  support_fact_refs: string[];
  contrary_fact_refs: string[];
  unknown_fact_refs: string[];
  exclusion_reason?: string;
  elements: LegalElement[];
  alternative_explanations: string[];
  statute_version: string;
  created_at: string;
}

export interface CoreIssue {
  id: string;
  case_id: string;
  candidate_id: string;
  issue_description: string;
  supporting_facts: string[];
  contrary_facts: string[];
  unresolved_questions: string[];
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface InterviewQuestion {
  id: string;
  case_id: string;
  candidate_id: string;
  element_id?: string;
  question_type: QuestionType;
  question_text: string;
  rationale: string;
  target_fact_refs: string[];
  priority: QuestionPriority;
  review_status: ReviewStatus;
  is_required: boolean;
  revision_number: number;
  expected_clarification: string;
}

export interface InterviewAnswer {
  id: string;
  question_id: string;
  answer_text: string;
  respondent_role: 'VICTIM' | 'SUSPECT' | 'WITNESS';
  created_at: string;
}

export interface ReviewRecord {
  id: string;
  case_id: string;
  gate_name: GateStage;
  target_revision_id: number;
  review_status: 'APPROVED' | 'CHANGES_REQUESTED' | 'STALE';
  reviewer_id: string;
  comments: string;
  reviewed_at: string;
}

export interface OfficialReport {
  id: string;
  case_id: string;
  revision_id: number;
  station: string;                   // 報告單位（例：臺北市政府警察局中正第一分局○○派出所）
  report_type: '受理' | '查獲';       // 受理或破獲/查獲
  title_reason: string;              // 案由（例：疑涉刑法第339條之4加重詐欺罪、洗錢防制法）
  status_marker: '受理' | '破獲';
  incident_time_roc: string;         // 民國紀年發生時間（例：民國113年5月10日15時30分許）
  incident_location: string;         // 發生地點
  report_time_roc: string;           // 報案時間
  clearance_time_roc?: string;       // 破獲時間
  summary_text: string;              // 案情摘要嚴謹公務條陳段落
  certificate_number: string;        // 證明單案號
  women_child_number: string;        // 婦幼案號（無則註明無）
  c165_number: string;               // 165反詐騙案號（無則註明無）
  jurisdiction: string;              // 本案管轄
  handling_officer: string;          // 處理員警
  is_approved: boolean;              // 是否經承辦人最終確認
  generated_at: string;
  validation_errors: string[];       // 格式驗證錯誤紀錄
}

export interface CaseRecord {
  id: string;
  title: string;
  status: 'ACTIVE' | 'ARCHIVED';
  stage: GateStage;
  current_revision: number;
  created_at: string;
  updated_at: string;
  owner_id: string;
  
  // Gate 0: 原始案情
  raw_intake: {
    summary: string;
    supplementary_notes?: string;
    analysis_remarks?: string;
    created_at: string;
  };
  
  // Gate 1: 結構化事實與證據
  facts: FactItem[];
  evidence_items: EvidenceItem[];
  behaviors: BehaviorItem[];
  
  // Gate 2: 候選法律方向與要件
  legal_candidates: LegalCandidate[];
  core_issues: CoreIssue[];
  
  // Gate 3: 筆錄問句
  questions: InterviewQuestion[];
  
  // Gate 4: 問答與更新比對
  answers: InterviewAnswer[];
  
  // Gate 5: 條陳與文件輸出
  reports: OfficialReport[];
  
  // 人工審核與歷史紀錄
  reviews: ReviewRecord[];
  audit_logs: AuditEvent[];
}

export interface AuditEvent {
  id: string;
  actor_id: string;
  case_id?: string;
  event_type: string;
  target_type: string;
  target_id: string;
  occurred_at: string;
  details: string;
}

export interface PredeployAuditCheck {
  id: string;
  title: string;
  category: 'CONFIG' | 'SECURITY' | 'CODE' | 'DOCUMENTATION' | 'TEST';
  status: 'PASS' | 'FAIL' | 'NOT_RUN' | 'BLOCKED';
  evidence: string;
  details: string;
}

export interface SystemSettings {
  allow_external_ai: boolean;
  external_ai_endpoint: string;
  encryption_enabled: boolean;
  encryption_key_hash: string;
  supabase_connected: boolean;
  single_owner_id: string;
  login_lockout_enabled: boolean;
}
