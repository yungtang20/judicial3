/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 * 
 * CaseAnalyzer - 相容轉接層 (Compatibility Layer)
 * 專案: yungtang20/judicial2 (JUDICIAL3)
 * 
 * 依據 JUDICIAL3 架構修復規範：
 * 舊版 CaseAnalyzer 作為明確的相容層，全面對接統一的 LegalReasoningEngine，
 * 嚴禁存在不易察覺的雙重分析路徑。所有分析均由 LegalReasoningEngine 提供。
 */

import { LegalReasoningEngine, FullCaseAnalysisOutput } from './legalReasoningEngine';

export interface LawItem {
  title: string;
  subTitle: string;
  items: { num: string; text: string; highlight?: boolean }[];
  hint: string;
  authority: string;
}

export interface RulingItem {
  court: string;
  caseNo: string;
  yearDate: string;
  title: string;
  holding: string;
  takeaway: string;
}

export interface TreatiseItem {
  title: string;
  author: string;
  source: string;
  coreArgument: string;
  takeaway: string;
}

export interface QAItem {
  id: string;
  type: string;
  question: string;
  answer: string;
  hint: string;
}

export interface CaseAnalysisResult {
  categoryName: string;
  aiBrief: string;
  badges: { label: string; count: number; key: 'laws' | 'rulings' | 'treatises' }[];
  laws: LawItem[];
  rulings: RulingItem[];
  treatises: TreatiseItem[];
  detailedAnalysis: {
    title1: string;
    desc1: string;
    title2: string;
    desc2: string;
    title3: string;
    desc3: string;
    conclusion: string;
  };
  qaItems: QAItem[];
  report: {
    titleReason: string;
    suspects: string;
    victims: string;
    summary: string;
    seizedItems: string[];
    legalAnalysis: string;
    recommendations: string;
  };
  // JUDICIAL3 結構化核心擴充屬性
  fullAnalysis?: FullCaseAnalysisOutput;
}

export class CaseAnalyzer {
  /**
   * 統一呼叫 LegalReasoningEngine，禁止獨立舊式正規化分支
   */
  static analyze(text: string): CaseAnalysisResult {
    const raw = (text || '').trim();
    // 呼叫統一權威引擎
    const full = LegalReasoningEngine.analyzeFullCase(raw);

    const prim = full.candidates.find((c) => c.candidate_status === 'PRIMARY') || full.candidates[0];
    const altCount = full.candidates.filter((c) => c.candidate_status !== 'PRIMARY').length;

    const suspects = full.facts.find((f) => f.source_type === 'SUSPECT')?.subject || '[涉嫌人待查]';
    const victims = full.facts.find((f) => f.source_type === 'VICTIM')?.subject || '[告訴人詳卷]';

    const qaItems: QAItem[] = full.questions.map((q) => ({
      id: q.id,
      type: q.question_type.replace(/^\d+_/, ''),
      question: `問：${q.question_text}`,
      answer: '答：',
      hint: q.rationale,
    }));

    return {
      categoryName: full.categoryName,
      aiBrief: full.aiBrief,
      badges: full.badges,
      laws: full.laws,
      rulings: full.rulings,
      treatises: full.treatises,
      detailedAnalysis: {
        title1: `1. 主位法律方向：${prim?.legal_name || '待查證'}`,
        desc1: `本案經構成要件逐項比對，主位指向「${prim?.legal_name || '待查'}」，其法定要件包含客觀行為著手與主觀犯意。已識別 ${
          prim?.elements.length || 0
        } 項構成要件分析。`,
        title2: `2. 競爭與替代法律方向（共 ${altCount} 項備位路線）`,
        desc2: full.candidates
          .filter((c) => c.candidate_status !== 'PRIMARY')
          .map((c) => `【${c.candidate_status}】${c.legal_name}：${c.alternative_explanations.join('；')}`)
          .join('\n') || '尚無其他顯著競爭罪名。',
        title3: '3. 核心待證爭點與事實狀態（落實三值邏輯）',
        desc3: `卷內共標記 ${full.facts.length} 項事實。其中否認爭點 ${
          full.facts.filter((f) => f.assertion_status === 'DENIED').length
        } 項、待查明未知事項 ${
          full.facts.filter((f) => f.assertion_status === 'UNKNOWN').length
        } 項。依規定不得將 UNKNOWN 當成 FALSE，亦不得將 DENIED 當成事實不存在。`,
        conclusion: `偵查建言：建請依照產製之 9 大分類偵訊問句逐題向涉嫌人與證人查證，並調取客觀監視器與金流明細補強保管鏈。`,
      },
      qaItems,
      report: {
        titleReason: full.report.title_reason,
        suspects: `涉嫌人：${suspects}`,
        victims: `告訴人：${victims}`,
        summary: full.report.summary_text,
        seizedItems: full.evidence.map((e) => `${e.evidence_type}（${e.source_description}）`),
        legalAnalysis: `涉案事實經比對該當${prim?.legal_name || '待查法條'}。備位方向並列${altCount}項。`,
        recommendations: '建請依法指揮司法警察調取通聯與金流，並落實人證供述與物證之客觀比對。',
      },
      fullAnalysis: full,
    };
  }
}
