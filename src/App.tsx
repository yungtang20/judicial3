/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 * 
 * 臺灣刑事偵查法律推理系統 (JUDICIAL3 核心架構)
 * 專案: yungtang20/judicial2
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Scale,
  FileText,
  FileCheck2,
  Copy,
  Check,
  Download,
  Sparkles,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Plus,
  Trash2,
  RefreshCw,
  BookOpen,
  Gavel,
  Library,
  Layers,
  ArrowRight,
  Database,
  Save,
  History,
  FolderOpen,
  X,
  Server,
  Search,
  RotateCcw,
  SlidersHorizontal,
  Compass,
  ArrowLeft,
  ThumbsUp,
  ThumbsDown,
  ClipboardPaste,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  Edit3
} from 'lucide-react';
import {
  LegalReasoningEngine,
  FullCaseAnalysisOutput,
  LawReferenceItem,
  RulingReferenceItem,
  TreatiseReferenceItem
} from './services/legalReasoningEngine';
import {
  AssertionStatus,
  CandidateStatus,
  ElementStatus,
  FactItem,
  LegalCandidate,
  InterviewQuestion,
  OfficialReport
} from './types';

const PRESET_CASES = [
  {
    name: '林○○虛擬貨幣假投資 (典型網路詐欺)',
    short: '虛擬貨幣假投資',
    text: `報案人林○○稱，其於網路社群平台認識一名自稱從事投資的男子，雙方聯繫約一個月後，該男子向其表示可透過特定投資平台操作虛擬貨幣獲利，並傳送平台網址及操作教學。林○○依指示註冊帳號，先後匯款新臺幣30萬元至對方提供之數個銀行帳戶，平台帳面顯示投資獲利，惟其申請提領時，對方要求再繳納保證金及稅金，林○○因而起疑，拒絕付款並要求返還款項，對方隨即停止聯繫，平台亦無法登入。林○○表示，匯款均由其本人操作，尚不清楚收款帳戶實際使用人身分，亦無法確認平台顯示之投資交易是否真實，現提供雙方對話紀錄、匯款明細及平台截圖供警方調查。`,
  },
  {
    name: '超商 ATM 連續提款車手案',
    short: '超商 ATM 車手案',
    text: `巡邏員警於民國115年3月15日22時30分許，在新北市板橋區文化路二段統一超商門市內之 ATM，查獲嫌疑人乙男手持非本人之金融卡3張，連續操作提領現鈔12次，累計提領新臺幣50萬元裝入隨身背包，形跡至為可疑。員警遂依法上前盤查，當場查扣該3張金融卡、現鈔50萬元及涉案手機1支。乙男坦承有提款行為，但辯稱是通訊軟體 Telegram 上一名自稱「飛哥」之人指示其代領跑腿，每領10萬元可抽2,000元，不知該筆款項係假冒健保局詐騙集團之贓款，否認參與詐欺。`,
  },
  {
    name: '夜店竊取皮包轉賣案',
    short: '夜店竊取皮包',
    text: `被害人陳女於民國115年5月10日凌晨1時許，在臺北市信義區松壽路某夜店吧檯座位飲酒，不慎將隨身攜帶之手提包（內有現金新臺幣2萬元及手機1支）置於高腳椅上。嫌疑人張三見周遭人潮擁擠，趁陳女轉身與友人交談之際，徒手將該手提包偷走藏入外套迅速逃離現場。張三於當日上午10時前往光華商場通訊行，以新臺幣1萬5,000元將該手機變賣花用。案經陳女報案，警方調閱夜店監視器於通訊行追查查獲張三。`,
  },
  {
    name: '路口行車糾紛持球棒傷害恐嚇案',
    short: '行車糾紛球棒案',
    text: `被害人張○○於民國115年5月2日18時許，駕駛自小客車行經臺中市西屯區臺灣大道時，與騎乘機車之嫌疑人陳○○發生超車糾紛。陳○○心生不滿，竟於停等紅燈時攔阻張○○去路，手持隨身攜帶之鋁製球棒擊破張○○自小客車前擋風玻璃，並將張○○拉下車徒手毆打及持球棒揮擊，致張○○受有頭部撕裂傷及左手臂骨折等傷害，陳○○更出言恫嚇稱：「再叭就打死你！」隨後騎車逃逸。案經被害人報案檢附醫院驗傷診斷證明書提出告訴。`,
  },
  {
    name: '咖啡廳皮夾遺忘與感應盜刷案',
    short: '咖啡廳感應盜刷',
    text: `被害人甲女於民國115年4月10日14時許，在臺北市大安區某咖啡廳2樓座位用餐，離去時不慎將皮夾（內有現金3,000元及感應式信用卡1張）遺忘在沙發座位上。鄰桌客人丁女見狀將該皮夾取走放入手提包離開現場，並於14時40分許前往鄰近屈臣氏持該信用卡以小額免簽名感應方式盜刷2,850元化妝品。甲女接獲發卡銀行消費簡訊後報案，警方調閱監視器當場查獲丁女。丁女辯稱本想送警局，順路先借用會還錢。`,
  },
  {
    name: '夜間超速闖紅燈撞倒機車肇事逃逸案',
    short: '闖紅燈肇事逃逸',
    text: `被害人李四於民國115年6月1日23時許，騎乘機車行經高雄市三民區九如一路與民族路口，依號誌綠燈正常行駛。嫌疑人王五駕駛白色自小客車超速且闖紅燈疾駛而來，直接攔腰撞擊李四機車，致李四人車倒地受有腦震盪及腿部粉碎性骨折。王五於撞擊後僅減速數秒，未下車施以救護或報警處理，隨即加速逃逸。現場熱心民眾記下車號報警，警員循線於2小時後在王五住處地下停車場查獲涉案車輛及車身擦痕。`,
  },
];

export default function App() {
  // View mode: 'landing' (Google single search box style) or 'results' (Google search results style)
  const [viewMode, setViewMode] = useState<'landing' | 'results'>('landing');

  // Input case text
  const [inputText, setInputText] = useState(PRESET_CASES[0].text);

  // Unified Legal Reasoning Engine output state
  const [analysisOutput, setAnalysisOutput] = useState<FullCaseAnalysisOutput>(() =>
    LegalReasoningEngine.analyzeFullCase(PRESET_CASES[0].text)
  );

  // Active Main Tab in Results View
  const [activeTab, setActiveTab] = useState<'all' | 'facts' | 'crimes' | 'record' | 'report'>('all');

  // Sub-Tab for Legal References: 法規 | 裁判 | 論著
  const [activeSubTab, setActiveSubTab] = useState<'laws' | 'rulings' | 'treatises' | 'all-sub'>('laws');

  const [showDetailedAnalysis, setShowDetailedAnalysis] = useState(true);
  const [copiedSection, setCopiedSection] = useState<string | null>(null);
  const [userFeedback, setUserFeedback] = useState<'helpful' | 'neutral' | null>(null);

  // Invalidation & Approval State (Phase 4 requirement)
  const [isApproved, setIsApproved] = useState<boolean>(false);
  const [isStale, setIsStale] = useState<boolean>(false);
  const [staleReason, setStaleReason] = useState<string | null>(null);

  // PostgreSQL Database State
  const [dbHealth, setDbHealth] = useState<{
    status: string;
    engine: string;
    tablesCount: number;
    caseCount: number;
    revisionCount: number;
  } | null>(null);
  const [savedCases, setSavedCases] = useState<any[]>([]);
  const [showCasesModal, setShowCasesModal] = useState(false);
  const [isSavingToDb, setIsSavingToDb] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);

  // Interactive Question & Answer items (Editable)
  const [qaList, setQaList] = useState<InterviewQuestion[]>(analysisOutput.questions);

  // Editable 條陳 Summary
  const [reportSummary, setReportSummary] = useState(analysisOutput.report.summary_text);

  // Textarea auto-resize ref
  const landingInputRef = useRef<HTMLTextAreaElement>(null);

  // Load Database Status & Cases on Mount
  useEffect(() => {
    fetchDbStatus();
    fetchCases();
  }, []);

  const fetchDbStatus = async () => {
    try {
      const res = await fetch('/api/database/status');
      if (res.ok) {
        const data = await res.json();
        setDbHealth(data);
      }
    } catch {
      // Backend offline or starting
    }
  };

  const fetchCases = async () => {
    try {
      const res = await fetch('/api/cases');
      if (res.ok) {
        const data = await res.json();
        setSavedCases(data.cases || []);
      }
    } catch {
      // ignore
    }
  };

  // Perform full legal reasoning analysis using LegalReasoningEngine
  const handlePerformSearch = (textToAnalyze?: string) => {
    const targetText = textToAnalyze !== undefined ? textToAnalyze : inputText;
    if (!targetText.trim()) {
      alert('請輸入案情內容');
      return;
    }
    const output = LegalReasoningEngine.analyzeFullCase(targetText);
    setAnalysisOutput(output);
    setQaList(output.questions);
    setReportSummary(output.report.summary_text);
    setIsApproved(false);
    setIsStale(false);
    setStaleReason(null);
    setViewMode('results');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectPreset = (presetText: string) => {
    setInputText(presetText);
    handlePerformSearch(presetText);
  };

  const handleFeelingLucky = () => {
    const randomIndex = Math.floor(Math.random() * PRESET_CASES.length);
    const selected = PRESET_CASES[randomIndex];
    setInputText(selected.text);
    handlePerformSearch(selected.text);
  };

  // Phase 4: Backfill answers & trigger downstream invalidation
  const handleBackfillAnswersAndReevaluate = () => {
    const updatedCase = { ...analysisOutput.caseRecord };
    const answeredCount = qaList.filter((q) => q.expected_clarification).length;

    // Advance revision and mark old approvals stale
    const targetFact = updatedCase.facts[0] || {
      id: `fact-temp`,
      predicate: reportSummary,
    };

    const { updatedCase: newCase, invalidationReport } = LegalReasoningEngine.invalidateDownstreamOnFactChange(
      updatedCase,
      targetFact.id,
      { predicate: reportSummary },
      `筆錄問答回填完畢（共填寫 ${qaList.length} 題），觸發下游重新涵攝`
    );

    const reEvaluatedOutput = LegalReasoningEngine.analyzeFullCase(reportSummary, newCase.id);
    reEvaluatedOutput.caseRecord.current_revision = newCase.current_revision;

    setAnalysisOutput(reEvaluatedOutput);
    setIsApproved(false);
    setIsStale(true);
    setStaleReason(`版本已推進至 Rev #${newCase.current_revision}。上游案件事實與答詢已更新，舊版公文核准失效，請重新審核！`);
    alert(`已完成問答回填！版本遞增至 Rev #${newCase.current_revision}，下游構成要件與公文已標記為 STALE，舊核定失效。`);
  };

  // Phase 4: Human-in-the-loop manual approval
  const handleApproveReport = () => {
    setIsApproved(true);
    setIsStale(false);
    setStaleReason(null);
    alert(`【人工審核確認】承辦員警已正式核定簽署本案公務條陳 (Rev #${analysisOutput.caseRecord.current_revision})！`);
  };

  // Phase 4: Manually edit fact assertion status (ASSERTED, ADMITTED, DENIED, INFERRED, UNKNOWN)
  const handleChangeFactStatus = (factId: string, newStatus: AssertionStatus) => {
    const updatedFacts = analysisOutput.facts.map((f) =>
      f.id === factId ? { ...f, assertion_status: newStatus } : f
    );
    const updatedCase = {
      ...analysisOutput.caseRecord,
      facts: updatedFacts,
    };
    const { candidates, coreIssues } = LegalReasoningEngine.evaluateLegalCandidates(
      inputText,
      updatedFacts,
      updatedCase.id,
      updatedCase.current_revision + 1,
      updatedCase.evidence_items
    );
    updatedCase.current_revision += 1;
    updatedCase.legal_candidates = candidates;
    updatedCase.core_issues = coreIssues;

    setAnalysisOutput({
      ...analysisOutput,
      caseRecord: updatedCase,
      facts: updatedFacts,
      candidates,
      coreIssues,
    });
    setIsApproved(false);
    setIsStale(true);
    setStaleReason(`事實項狀態變更為 ${newStatus}，觸發下游重新涵攝，版本遞增至 Rev #${updatedCase.current_revision}`);
  };

  // Save case analysis to PostgreSQL
  const handleSaveToPostgres = async () => {
    setIsSavingToDb(true);
    try {
      const payload = {
        title: `${analysisOutput.categoryName} - ${analysisOutput.report.title_reason.slice(0, 30)}`,
        rawText: inputText,
        facts: analysisOutput.facts.map((f, idx) => ({
          seq: idx + 1,
          description: f.predicate,
          status: f.assertion_status,
          factType: f.source_type,
          confidenceScore: f.confidence,
        })),
        candidates: analysisOutput.candidates.map((c) => ({
          chargeName: c.legal_name,
          status: c.candidate_status,
          rationale: c.alternative_explanations.join('；') || '法定構成要件比對',
        })),
        questions: qaList.map((q, idx) => ({
          seq: idx + 1,
          questionText: q.question_text,
          answerText: q.expected_clarification || '待填答',
          isMandatory: q.is_required,
        })),
        summary: reportSummary,
        isLocked: isApproved,
      };

      const res = await fetch('/api/cases/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setSaveSuccessMsg(`成功保存至 PostgreSQL 資料庫！案號: ${data.caseNumber}，版本: Rev #${data.revisionNumber}`);
        fetchDbStatus();
        fetchCases();
        setTimeout(() => setSaveSuccessMsg(null), 4000);
      } else {
        const err = await res.json();
        alert(`儲存失敗: ${err.error || '資料庫寫入異常'}`);
      }
    } catch (e: any) {
      alert(`連線資料庫異常: ${e.message}`);
    } finally {
      setIsSavingToDb(false);
    }
  };

  const handleLoadSavedCase = async (caseId: string) => {
    try {
      const res = await fetch(`/api/cases/${caseId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.case?.raw_text) {
          setInputText(data.case.raw_text);
          const output = LegalReasoningEngine.analyzeFullCase(data.case.raw_text);
          setAnalysisOutput(output);
          setQaList(output.questions);
          setReportSummary(output.report.summary_text);
        }
        setShowCasesModal(false);
        setViewMode('results');
        setSaveSuccessMsg(`已成功載入案件快照：${data.case.case_number} (${data.case.title})`);
        setTimeout(() => setSaveSuccessMsg(null), 3000);
      }
    } catch (e: any) {
      alert(`載入案件異常: ${e.message}`);
    }
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(id);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  // Download official statement as Word (.doc) without hardcoded assumptions
  const handleDownloadReportDoc = () => {
    const htmlContent = `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>刑事案件報告單（條陳）</title>
<style>
body { font-family: "標楷體", serif; line-height: 1.8; margin: 40px; }
h1 { text-align: center; font-size: 20pt; }
h2 { font-size: 15pt; border-bottom: 2px solid #000; padding-bottom: 4px; }
p { margin: 8px 0; text-align: justify; }
</style>
</head>
<body>
<h1>刑事案件報告單（條陳）</h1>
<p style="text-align:right">版本：Rev #${analysisOutput.caseRecord.current_revision}<br>審核狀態：${isApproved ? '已核定' : '草稿'}</p>
<h2>一、案由</h2>
<p>${analysisOutput.report.title_reason}</p>
<h2>二、犯罪嫌疑人及關係人</h2>
<p>涉嫌人：${analysisOutput.facts.find((f) => f.source_type === 'SUSPECT')?.subject || '[待查]'}<br>告訴人：${analysisOutput.facts.find((f) => f.source_type === 'VICTIM')?.subject || '[詳卷]'}</p>
<h2>三、調查經過與客觀犯罪事實</h2>
<p>${reportSummary}</p>
<h2>四、扣案/檢附證物</h2>
<p>${analysisOutput.evidence.map((item, idx) => `${idx + 1}. ${item.evidence_type} (${item.source_description})`).join('<br>')}</p>
<h2>五、法律適用與要件研析</h2>
<p>${analysisOutput.candidates.map((c) => `【${c.candidate_status}】${c.legal_name}`).join('<br>')}</p>
</body>
</html>`;

    const blob = new Blob(['\ufeff' + htmlContent], { type: 'application/msword;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `刑事案件報告單_Rev${analysisOutput.caseRecord.current_revision}.doc`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Download full Interrogation Record as text
  const handleDownloadQAText = () => {
    let text = `【刑事案件調查警詢筆錄】(版本: Rev #${analysisOutput.caseRecord.current_revision})\n\n`;
    text += `案由：${analysisOutput.report.title_reason}\n\n`;
    text += `【權利告知事項】\n依刑事訴訟法第95條告知：得保持緘默、得選任辯護人、得請求調查有利證據。\n\n`;
    qaList.forEach((item, idx) => {
      text += `第 ${idx + 1} 題【${item.question_type}】\n問：${item.question_text}\n答：${item.expected_clarification || '待填答'}\n\n`;
    });

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `警詢筆錄_Rev${analysisOutput.caseRecord.current_revision}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  /* =========================================================================
   * VIEW 1: GOOGLE-STYLE LANDING PAGE
   * ========================================================================= */
  if (viewMode === 'landing') {
    return (
      <div className="min-h-screen bg-white flex flex-col justify-between text-slate-800 font-sans antialiased selection:bg-blue-100 selection:text-blue-900">
        {/* Minimal Google-like Top Bar */}
        <header className="w-full px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs text-slate-500 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>PostgreSQL 16 已就緒 (PGlite WASM 24表支援)</span>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowCasesModal(true)}
              className="text-xs text-slate-600 hover:text-slate-900 hover:bg-slate-100 px-3 py-1.5 rounded-lg font-medium flex items-center space-x-1.5 transition cursor-pointer"
            >
              <Database className="w-3.5 h-3.5 text-emerald-600" />
              <span>案件庫 ({savedCases.length})</span>
            </button>
            <div className="w-8 h-8 rounded-full bg-blue-700 text-white flex items-center justify-center font-bold text-xs shadow-xs">
              司
            </div>
          </div>
        </header>

        {/* Central Google-style Search Section */}
        <main className="w-full max-w-3xl mx-auto px-4 flex flex-col items-center justify-center my-auto py-10">
          <div className="flex flex-col items-center mb-8 select-none">
            <div className="flex items-center space-x-3 mb-2">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-700 via-indigo-600 to-sky-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
                <Scale className="w-7 h-7" />
              </div>
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">
                刑事偵查<span className="text-blue-700">輔助系統</span>
              </h1>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 font-medium tracking-wide">
              JUDICIAL3 結構化法律推理：事實追溯 • 構成要件逐項涵攝 • 候選法律方向比較 • 9類偵訊問句
            </p>
          </div>

          {/* THE SINGLE DIALOGUE / SEARCH BOX */}
          <div className="w-full relative group">
            <div className="relative flex flex-col w-full bg-white rounded-3xl border border-slate-200 shadow-md hover:shadow-lg focus-within:shadow-xl focus-within:border-blue-500 transition-all duration-200 overflow-hidden">
              <div className="flex items-start px-5 pt-4 pb-2">
                <Search className="w-5 h-5 text-slate-400 mt-1 shrink-0 mr-3" />
                <textarea
                  ref={landingInputRef}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handlePerformSearch();
                    }
                  }}
                  rows={4}
                  placeholder="請在此輸入或貼上案情事實、報案指訴、扣案物證或犯罪手法... (按 Enter 開始法律推理涵攝)"
                  className="w-full bg-transparent text-sm sm:text-base text-slate-800 placeholder-slate-400 focus:outline-hidden resize-none leading-relaxed"
                />
              </div>

              <div className="flex items-center justify-between px-5 pb-3 pt-1 border-t border-slate-100 text-xs text-slate-400">
                <div className="flex items-center space-x-2">
                  <span className="text-[11px] text-slate-400 hidden sm:inline">
                    按 Enter 立即分析 • Shift+Enter 換行
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  {inputText && (
                    <button
                      onClick={() => setInputText('')}
                      className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition cursor-pointer"
                      title="清除內容"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-center space-x-3 mt-6">
            <button
              onClick={() => handlePerformSearch()}
              className="px-5 py-2.5 rounded-full bg-slate-100 hover:bg-slate-200 active:bg-slate-300 text-slate-700 font-medium text-xs sm:text-sm border border-slate-200 transition-all cursor-pointer shadow-2xs hover:shadow-xs flex items-center space-x-1.5"
            >
              <Sparkles className="w-4 h-4 text-blue-600" />
              <span>智能法律推理涵攝</span>
            </button>
            <button
              onClick={handleFeelingLucky}
              className="px-5 py-2.5 rounded-full bg-slate-100 hover:bg-slate-200 active:bg-slate-300 text-slate-700 font-medium text-xs sm:text-sm border border-slate-200 transition-all cursor-pointer shadow-2xs hover:shadow-xs flex items-center space-x-1.5"
            >
              <Compass className="w-4 h-4 text-emerald-600" />
              <span>隨機示範案件 (好手氣)</span>
            </button>
          </div>

          {/* Quick Preset Chips */}
          <div className="mt-8 w-full flex flex-col items-center">
            <span className="text-xs text-slate-400 mb-2.5 font-medium">
              常見示範案情（點擊載入並執行要件涵攝）：
            </span>
            <div className="flex flex-wrap items-center justify-center gap-2 max-w-xl">
              {PRESET_CASES.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelectPreset(item.text)}
                  className="px-3 py-1.5 rounded-full text-xs font-medium bg-slate-50 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-300 border border-slate-200 text-slate-600 transition-all cursor-pointer shadow-2xs"
                >
                  {item.short}
                </button>
              ))}
            </div>
          </div>
        </main>

        {/* Minimal Footer */}
        <footer className="w-full bg-slate-50 border-t border-slate-200 py-3 px-6 text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center space-x-4">
            <span>中華民國刑事偵查法律推理規範</span>
            <span>三階層犯罪論 • 構成要件涵攝 • 刑訴法第2條注意有利不利原則</span>
          </div>
          <div className="flex items-center space-x-3 text-slate-400">
            <span>JUDICIAL3 Core Engine</span>
            <span>•</span>
            <span>僅供司法警察機關辦案輔助參考</span>
          </div>
        </footer>

        {showCasesModal && renderCasesModal()}
      </div>
    );
  }

  /* =========================================================================
   * VIEW 2: RESULTS VIEW
   * ========================================================================= */
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans antialiased pb-16">
      {/* Top Search Bar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
          <button
            onClick={() => setViewMode('landing')}
            className="flex items-center space-x-2 shrink-0 cursor-pointer group text-left"
            title="回到首頁"
          >
            <div className="w-8 h-8 rounded-lg bg-blue-700 group-hover:bg-blue-800 flex items-center justify-center text-white shadow-xs transition">
              <Scale className="w-4 h-4" />
            </div>
            <div className="hidden sm:block">
              <span className="text-sm font-extrabold text-slate-900 group-hover:text-blue-700 transition">
                刑事偵查<span className="text-blue-700">輔助</span>
              </span>
            </div>
          </button>

          <div className="flex-1 max-w-2xl relative">
            <div className="flex items-center bg-slate-50 hover:bg-white focus-within:bg-white rounded-full border border-slate-300 focus-within:border-blue-600 focus-within:shadow-md transition px-4 py-1.5">
              <Search className="w-4 h-4 text-slate-400 mr-2 shrink-0" />
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handlePerformSearch();
                  }
                }}
                placeholder="輸入案情後按 Enter 重新涵攝..."
                className="w-full bg-transparent text-xs sm:text-sm text-slate-800 focus:outline-hidden"
              />
              <button
                onClick={() => handlePerformSearch()}
                className="text-xs bg-blue-700 hover:bg-blue-800 text-white px-2.5 py-1 rounded-full font-medium shrink-0 ml-1 transition cursor-pointer"
              >
                分析
              </button>
            </div>
          </div>

          <div className="flex items-center space-x-2 shrink-0">
            <button
              onClick={() => setViewMode('landing')}
              className="text-xs text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 px-2.5 py-1.5 rounded-lg font-medium hidden md:flex items-center space-x-1 transition cursor-pointer"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>新案</span>
            </button>
            <button
              onClick={handleSaveToPostgres}
              disabled={isSavingToDb}
              className="text-xs text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-300 px-2.5 py-1.5 rounded-lg font-medium flex items-center space-x-1 transition cursor-pointer"
            >
              <Save className="w-3.5 h-3.5 text-emerald-600" />
              <span className="hidden sm:inline">{isSavingToDb ? '存檔中...' : '保存快照'}</span>
            </button>
            <button
              onClick={() => setShowCasesModal(true)}
              className="text-xs text-slate-700 bg-slate-100 hover:bg-slate-200 px-2.5 py-1.5 rounded-lg font-medium flex items-center space-x-1 transition cursor-pointer"
            >
              <Database className="w-3.5 h-3.5 text-slate-600" />
              <span>({savedCases.length})</span>
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-5xl mx-auto px-4 flex items-center space-x-1 overflow-x-auto text-xs no-scrollbar border-t border-slate-100 pt-1">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-3 py-2 font-medium border-b-2 transition shrink-0 cursor-pointer ${
              activeTab === 'all'
                ? 'border-blue-700 text-blue-700 font-bold'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            全部一覽
          </button>
          <button
            onClick={() => setActiveTab('facts')}
            className={`px-3 py-2 font-medium border-b-2 transition shrink-0 cursor-pointer ${
              activeTab === 'facts'
                ? 'border-blue-700 text-blue-700 font-bold'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            🔍 結構化事實 ({analysisOutput.facts.length}項 • 5元狀態)
          </button>
          <button
            onClick={() => setActiveTab('crimes')}
            className={`px-3 py-2 font-medium border-b-2 transition shrink-0 cursor-pointer ${
              activeTab === 'crimes'
                ? 'border-blue-700 text-blue-700 font-bold'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            ⚖️ 候選法律與要件比對 ({analysisOutput.candidates.length}方向)
          </button>
          <button
            onClick={() => setActiveTab('record')}
            className={`px-3 py-2 font-medium border-b-2 transition shrink-0 cursor-pointer ${
              activeTab === 'record'
                ? 'border-blue-700 text-blue-700 font-bold'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            📝 偵訊筆錄 (9大類問句)
          </button>
          <button
            onClick={() => setActiveTab('report')}
            className={`px-3 py-2 font-medium border-b-2 transition shrink-0 cursor-pointer ${
              activeTab === 'report'
                ? 'border-blue-700 text-blue-700 font-bold'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            📄 刑事公務條陳 (Rev #{analysisOutput.caseRecord.current_revision})
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-5xl mx-auto px-4 pt-5 space-y-6">
        {/* Status Alerts */}
        {isStale && (
          <div className="bg-amber-50 border border-amber-300 text-amber-900 text-xs px-4 py-3 rounded-xl flex items-center justify-between shadow-xs">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
              <span className="font-medium">{staleReason || '案件事實已異動，下游要件與公文已標記為 STALE，舊版核准失效！'}</span>
            </div>
            <button
              onClick={handleApproveReport}
              className="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded font-medium cursor-pointer shrink-0 ml-2"
            >
              重新審核並核定
            </button>
          </div>
        )}

        {isApproved && (
          <div className="bg-emerald-50 border border-emerald-300 text-emerald-900 text-xs px-4 py-2.5 rounded-xl flex items-center space-x-2 shadow-xs">
            <CheckCircle className="w-4 h-4 text-emerald-600" />
            <span className="font-semibold">
              目前版本 (Rev #{analysisOutput.caseRecord.current_revision}) 已由承辦員警正式審查確認核定完畢。
            </span>
          </div>
        )}

        {/* Outer Container */}
        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden divide-y divide-slate-100">
          {/* Top: Raw Fact Box */}
          <div className="p-5 sm:p-6 bg-slate-50/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center space-x-1.5">
                <FileText className="w-3.5 h-3.5 text-slate-400" />
                <span>原始案情輸入 (快照版本: Rev #{analysisOutput.caseRecord.current_revision})</span>
              </span>
              <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                主位研判：{analysisOutput.categoryName}
              </span>
            </div>
            <div className="p-4 rounded-xl bg-slate-100/90 border border-slate-200/80 text-sm text-slate-800 leading-relaxed text-justify font-sans">
              {inputText}
            </div>
          </div>

          {/* SECTION: 結構化事實清單 (Facts & Evidence - 5元狀態) */}
          {(activeTab === 'all' || activeTab === 'facts') && (
            <div className="p-5 sm:p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-1.5">
                    <Search className="w-4 h-4 text-blue-600" />
                    <span>結構化事實與五元狀態 (三值邏輯 • 嚴禁 UNKNOWN 當作 FALSE)</span>
                  </h3>
                  <p className="text-xs text-slate-500">
                    區分陳述 (ASSERTED)、自白 (ADMITTED)、否認 (DENIED)、推論 (INFERRED)、未知 (UNKNOWN)
                  </p>
                </div>
                <span className="text-xs text-slate-400">點擊狀態標籤可手動調整事實認定</span>
              </div>

              <div className="grid grid-cols-1 gap-2.5">
                {analysisOutput.facts.map((fact, idx) => (
                  <div
                    key={fact.id}
                    className="p-3 rounded-xl border border-slate-200 bg-white hover:border-blue-300 transition flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-slate-500 font-mono">#{idx + 1}</span>
                        <span className="font-semibold text-slate-900">{fact.subject}</span>
                        <span className="text-slate-400">|</span>
                        <span className="text-slate-500">{fact.event_time}</span>
                        <span className="text-slate-400">|</span>
                        <span className="text-slate-500">{fact.event_location}</span>
                      </div>
                      <p className="text-slate-800 font-serif leading-relaxed text-justify">
                        {fact.predicate}
                      </p>
                    </div>

                    <div className="flex items-center space-x-1 shrink-0 self-end sm:self-center">
                      {(['ASSERTED', 'ADMITTED', 'DENIED', 'INFERRED', 'UNKNOWN'] as AssertionStatus[]).map((st) => (
                        <button
                          key={st}
                          onClick={() => handleChangeFactStatus(fact.id, st)}
                          className={`px-2 py-0.5 rounded text-[10px] font-bold cursor-pointer transition ${
                            fact.assertion_status === st
                              ? st === 'ADMITTED'
                                ? 'bg-emerald-600 text-white shadow-2xs'
                                : st === 'DENIED'
                                ? 'bg-red-600 text-white shadow-2xs'
                                : st === 'UNKNOWN'
                                ? 'bg-amber-600 text-white shadow-2xs'
                                : 'bg-blue-600 text-white shadow-2xs'
                              : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                          }`}
                        >
                          {st}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Evidences list */}
              <div className="border-t border-slate-100 pt-3">
                <span className="text-xs font-bold text-slate-700 block mb-2">客觀獨立證物與證明力界限：</span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {analysisOutput.evidence.map((evi) => (
                    <div key={evi.id} className="p-2.5 rounded-lg border border-slate-200 bg-slate-50/70 text-xs">
                      <div className="font-bold text-slate-800 flex items-center justify-between">
                        <span>{evi.evidence_type}</span>
                        <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">
                          {evi.collection_status}
                        </span>
                      </div>
                      <p className="text-slate-600 text-[11px] mt-0.5">{evi.source_description}</p>
                      {evi.limitations && (
                        <div className="text-[10px] text-amber-800 bg-amber-50 p-1 rounded mt-1">
                          <strong>證明力限制：</strong>{evi.limitations}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* SECTION: 候選法律方向與要件逐項涵攝 (Multi-Candidate Offenses & Subsumption) */}
          {(activeTab === 'all' || activeTab === 'crimes') && (
            <div className="p-5 sm:p-6 space-y-5">
              <div>
                <h3 className="text-xs font-bold text-blue-700 tracking-wide mb-1.5 flex items-center space-x-1">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>AI 法律推理涵攝簡述</span>
                </h3>
                <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 text-sm text-slate-800 leading-relaxed">
                  {analysisOutput.aiBrief}
                </div>
              </div>

              {/* Multi-Candidate Offense Cards */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-700 border-l-3 border-blue-600 pl-2">
                    平行候選法律方向 ({analysisOutput.candidates.length} 項 • 主位/備位/競爭)
                  </span>
                  <span className="text-[11px] text-slate-400">杜絕單一罪名分類偏誤</span>
                </div>

                <div className="grid grid-cols-1 gap-3.5">
                  {analysisOutput.candidates.map((cand, cIdx) => (
                    <div
                      key={cand.id}
                      className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-300 transition space-y-3 shadow-2xs"
                    >
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <div className="flex items-center space-x-2">
                          <span
                            className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                              cand.candidate_status === 'PRIMARY'
                                ? 'bg-blue-600 text-white'
                                : cand.candidate_status === 'ALTERNATIVE'
                                ? 'bg-indigo-100 text-indigo-800'
                                : cand.candidate_status === 'UNRESOLVED'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-slate-100 text-slate-700'
                            }`}
                          >
                            {cand.candidate_status}
                          </span>
                          <h4 className="font-bold text-sm text-slate-900">{cand.legal_name}</h4>
                        </div>
                        <span className="text-[11px] text-slate-500 font-mono">{cand.statute_ref}</span>
                      </div>

                      <div className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                        {cand.alternative_explanations.map((exp, eIdx) => (
                          <p key={eIdx}>{exp}</p>
                        ))}
                      </div>

                      {/* Element Assessment Subsumption Table */}
                      <div className="space-y-1.5 pt-1">
                        <span className="text-[11px] font-bold text-slate-600 block">
                          構成要件逐項比對 (Element Subsumption)：
                        </span>
                        <div className="grid grid-cols-1 gap-1.5">
                          {cand.elements.map((elem) => (
                            <div
                              key={elem.id}
                              className="p-2 rounded border border-slate-100 bg-slate-50/50 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-1 text-[11px]"
                            >
                              <div className="space-y-0.5">
                                <span className="font-bold text-slate-900 mr-2">{elem.element_name}</span>
                                <span className="text-slate-500">{elem.element_description}</span>
                                <p className="text-slate-600 text-[10px] mt-0.5">
                                  <strong>審查理由：</strong>{elem.reasoning}
                                </p>
                              </div>
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-bold shrink-0 ${
                                  elem.element_status === 'SATISFIED'
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : elem.element_status === 'CONTESTED'
                                    ? 'bg-red-100 text-red-800'
                                    : elem.element_status === 'INSUFFICIENT_DATA'
                                    ? 'bg-amber-100 text-amber-800'
                                    : 'bg-slate-100 text-slate-600'
                                }`}
                              >
                                {elem.element_status}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Clickable Legal Reference Badges */}
              <div className="border-t border-slate-200 pt-3">
                <div className="flex items-center space-x-2">
                  {analysisOutput.badges.map((badge) => {
                    const isSelected = activeSubTab === badge.key;
                    return (
                      <button
                        key={badge.key}
                        onClick={() => setActiveSubTab(badge.key)}
                        className={`px-3 py-1 rounded-full text-xs font-bold transition flex items-center space-x-1.5 cursor-pointer border ${
                          isSelected
                            ? 'bg-blue-700 text-white border-blue-700 shadow-xs'
                            : 'bg-sky-50 hover:bg-sky-100 text-sky-800 border-sky-200'
                        }`}
                      >
                        {badge.key === 'laws' && <BookOpen className="w-3.5 h-3.5" />}
                        {badge.key === 'rulings' && <Gavel className="w-3.5 h-3.5" />}
                        {badge.key === 'treatises' && <Library className="w-3.5 h-3.5" />}
                        <span>
                          {badge.label} {badge.count}
                        </span>
                      </button>
                    );
                  })}
                </div>

                {/* Sub Tab Content */}
                <div className="mt-3 text-xs text-slate-700">
                  {activeSubTab === 'laws' && (
                    <div className="space-y-2">
                      {analysisOutput.laws.map((l, i) => (
                        <div key={i} className="p-3 rounded-lg border border-slate-200 bg-white">
                          <strong className="text-slate-900">{l.title} ({l.subTitle})</strong>
                          <p className="text-slate-600 mt-1">{l.items.map((it) => it.text).join(' ')}</p>
                          <span className="text-[10px] text-slate-400 mt-1 block">提示: {l.hint} | 主管: {l.authority}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {activeSubTab === 'rulings' && (
                    <div className="space-y-2">
                      {analysisOutput.rulings.map((r, i) => (
                        <div key={i} className="p-3 rounded-lg border border-slate-200 bg-white">
                          <div className="flex justify-between font-bold text-slate-900">
                            <span>{r.court} {r.caseNo}</span>
                            <span className="text-slate-400 text-[10px]">{r.yearDate}</span>
                          </div>
                          <p className="text-slate-700 mt-1">{r.holding}</p>
                          <span className="text-[10px] text-emerald-700 mt-1 block font-medium">適用要旨: {r.takeaway}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {activeSubTab === 'treatises' && (
                    <div className="space-y-2">
                      {analysisOutput.treatises.map((t, i) => (
                        <div key={i} className="p-3 rounded-lg border border-slate-200 bg-white">
                          <strong className="text-slate-900">{t.title}</strong>
                          <span className="text-slate-400 text-[10px] ml-2">({t.author} • {t.source})</span>
                          <p className="text-slate-700 mt-1">{t.coreArgument}</p>
                          <span className="text-[10px] text-blue-700 mt-1 block font-medium">辦案指引: {t.takeaway}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* SECTION: 偵訊筆錄 (9大類問句 & 回填重新評估) */}
          {(activeTab === 'all' || activeTab === 'record') && (
            <div className="p-5 sm:p-6 space-y-4 bg-slate-50/30">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-1.5">
                    <Edit3 className="w-4 h-4 text-blue-600" />
                    <span>警詢/偵訊筆錄 (9大分類非誘導性問答 • 可線上填答並回填重新評估)</span>
                  </h3>
                  <p className="text-xs text-slate-500">
                    依刑訴法第2條注意有利不利原則，填答後可點擊回填觸發下游重新涵攝
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleBackfillAnswersAndReevaluate}
                    className="px-3 py-1.5 text-xs rounded-lg bg-blue-700 hover:bg-blue-800 text-white font-medium flex items-center space-x-1 shadow-xs transition cursor-pointer"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>回填答詢並重新評估</span>
                  </button>
                  <button
                    onClick={handleDownloadQAText}
                    className="px-2.5 py-1.5 text-xs rounded-lg bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 flex items-center space-x-1 transition cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>匯出筆錄 (TXT)</span>
                  </button>
                </div>
              </div>

              {/* Question list */}
              <div className="space-y-3">
                {qaList.map((q, idx) => (
                  <div key={q.id} className="p-3.5 rounded-xl border border-slate-200 bg-white space-y-2 text-xs shadow-2xs">
                    <div className="flex items-center justify-between text-slate-500 border-b border-slate-100 pb-1.5">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-blue-800">第 {idx + 1} 題</span>
                        <span className="px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 font-medium">
                          {q.question_type}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-400">待證目的: {q.rationale}</span>
                    </div>

                    <div>
                      <label className="font-semibold text-slate-700 block mb-1">訊問內容：</label>
                      <p className="font-serif text-slate-900 bg-slate-50 p-2 rounded border border-slate-100">
                        {q.question_text}
                      </p>
                    </div>

                    <div>
                      <label className="font-semibold text-slate-700 block mb-1">受詢人答詢紀錄（可線上編輯）：</label>
                      <textarea
                        value={q.expected_clarification || ''}
                        onChange={(e) => {
                          const val = e.target.value;
                          setQaList((prev) =>
                            prev.map((item) => (item.id === q.id ? { ...item, expected_clarification: val } : item))
                          );
                        }}
                        rows={2}
                        className="w-full bg-slate-50 border border-slate-200 rounded p-2 text-slate-800 focus:bg-white focus:border-blue-600 focus:outline-hidden font-serif"
                        placeholder="請記錄受詢人回答細節..."
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SECTION: 刑事公務條陳 (版本與人工審核確認) */}
          {(activeTab === 'all' || activeTab === 'report') && (
            <div className="p-5 sm:p-6 space-y-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-1.5">
                    <FileCheck2 className="w-4 h-4 text-indigo-600" />
                    <span>刑事案件報告單（條陳 • 嚴格公務體裁）</span>
                  </h3>
                  <div className="flex items-center space-x-2 text-xs mt-0.5">
                    <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-mono">
                      Rev #{analysisOutput.caseRecord.current_revision}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded font-semibold ${
                        isApproved
                          ? 'bg-emerald-100 text-emerald-800'
                          : isStale
                          ? 'bg-red-100 text-red-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {isApproved ? '🟢 已由承辦員警核定' : isStale ? '⚠️ [STALE] 舊核定失效需重審' : '🟡 [草稿待審核]'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {!isApproved ? (
                    <button
                      onClick={handleApproveReport}
                      className="px-3 py-1.5 text-xs rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-medium flex items-center space-x-1 shadow-xs transition cursor-pointer"
                    >
                      <Check className="w-3.5 h-3.5" />
                      <span>承辦員警審核確認</span>
                    </button>
                  ) : (
                    <span className="text-xs text-emerald-700 font-semibold flex items-center space-x-1">
                      <ShieldCheck className="w-4 h-4" />
                      <span>已完成正式核定</span>
                    </span>
                  )}

                  <button
                    onClick={handleDownloadReportDoc}
                    className="px-2.5 py-1.5 text-xs rounded-lg bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 flex items-center space-x-1 transition cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>下載條陳 (Word)</span>
                  </button>
                </div>
              </div>

              {/* Official Report Document */}
              <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-4 text-xs font-serif leading-relaxed text-slate-800 shadow-2xs">
                <div className="text-center font-bold text-sm border-b border-slate-200 pb-2 text-slate-900">
                  【刑事案件報告單（條陳）】
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-700">
                  <div>
                    <strong className="text-slate-900">一、案由：</strong>
                    <div className="p-1.5 bg-slate-50 rounded border border-slate-100 mt-1">
                      {analysisOutput.report.title_reason}
                    </div>
                  </div>
                  <div>
                    <strong className="text-slate-900">二、關係人：</strong>
                    <div className="p-1.5 bg-slate-50 rounded border border-slate-100 mt-1">
                      涉嫌人：{analysisOutput.facts.find((f) => f.source_type === 'SUSPECT')?.subject || '[待查]'} / 告訴人：{analysisOutput.facts.find((f) => f.source_type === 'VICTIM')?.subject || '[詳卷]'}
                    </div>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <strong className="text-slate-900">三、調查經過與犯罪事實（可即時修訂）：</strong>
                    <span className="text-[11px] text-blue-600 font-sans">
                      ✏️ 編輯案情摘要將自動使舊核定失效並標記 STALE
                    </span>
                  </div>
                  <textarea
                    value={reportSummary}
                    onChange={(e) => {
                      setReportSummary(e.target.value);
                      setIsApproved(false);
                      setIsStale(true);
                      setStaleReason('條陳內容已經過手動編輯，尚未核定，請重新確認！');
                    }}
                    rows={4}
                    className="w-full bg-slate-50/80 border border-slate-200 rounded p-2.5 text-xs text-slate-800 font-sans leading-relaxed focus:bg-white focus:border-blue-600 focus:outline-hidden"
                  />
                </div>

                <div>
                  <strong className="text-slate-900">四、扣案/檢附證物：</strong>
                  <ul className="list-disc pl-5 space-y-1 mt-1 text-slate-700">
                    {analysisOutput.evidence.map((item, idx) => (
                      <li key={idx}>
                        {item.evidence_type}（{item.source_description}）
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <strong className="text-slate-900">五、法律適用與要件研析：</strong>
                  <div className="mt-1 text-slate-700 bg-slate-50 p-2.5 rounded border border-slate-100 space-y-1">
                    {analysisOutput.candidates.map((c, i) => (
                      <p key={i}>
                        <strong>【{c.candidate_status}】{c.legal_name}：</strong>
                        {c.alternative_explanations.join('；')}
                      </p>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Bottom Footer */}
          <div className="px-5 py-3.5 bg-slate-50/80 border-t border-slate-200 flex items-center justify-between flex-wrap gap-2 text-xs text-slate-500">
            <span>由 LegalReasoningEngine 結構化生成，人工審核為正式核定之必要前提。</span>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => {
                  handleCopy(
                    `【案由】${analysisOutput.report.title_reason}\n\n【候選法律】\n${analysisOutput.candidates
                      .map((c) => `[${c.candidate_status}] ${c.legal_name}`)
                      .join('\n')}\n\n【事實摘要】\n${reportSummary}`,
                    'bottom-copy'
                  );
                }}
                className="hover:text-blue-700 flex items-center space-x-1 transition cursor-pointer"
              >
                {copiedSection === 'bottom-copy' ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="text-emerald-600">已複製</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>複製完整研析摘要</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* PostgreSQL Modal */}
      {showCasesModal && renderCasesModal()}
    </div>
  );

  function renderCasesModal() {
    return (
      <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl border border-slate-200 max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden animate-fade-in">
          <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
            <div className="flex items-center space-x-2">
              <Database className="w-5 h-5 text-emerald-600" />
              <div>
                <h3 className="text-base font-bold text-slate-900">PostgreSQL 資料庫案件庫與版本歷程</h3>
                <p className="text-xs text-slate-500">
                  24張核心表 • RLS 安全政策 • 版本不可竄改鎖定保護
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowCasesModal(false)}
              className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-200 transition cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-5 overflow-y-auto space-y-3 flex-1">
            {savedCases.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-sm">
                資料庫內目前尚無儲存之案件，請點擊「保存快照」即可寫入 PostgreSQL！
              </div>
            ) : (
              savedCases.map((c) => (
                <div
                  key={c.id}
                  className="border border-slate-200 rounded-xl p-4 hover:border-blue-400 hover:bg-blue-50/30 transition flex items-center justify-between space-x-4 bg-white"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-900 text-sm">{c.case_number}</span>
                      <span className="text-[10px] bg-blue-100 text-blue-800 font-semibold px-2 py-0.5 rounded-full">
                        快照 Rev #{c.revision_number || 1}
                      </span>
                      {c.is_locked ? (
                        <span className="text-[10px] bg-amber-100 text-amber-800 font-semibold px-2 py-0.5 rounded-full">
                          🔒 已核定
                        </span>
                      ) : (
                        <span className="text-[10px] bg-slate-100 text-slate-600 font-medium px-2 py-0.5 rounded-full">
                          可編輯草稿
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-700 line-clamp-1">{c.title}</p>
                  </div>

                  <button
                    onClick={() => handleLoadSavedCase(c.id)}
                    className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shrink-0 transition flex items-center space-x-1 cursor-pointer shadow-2xs"
                  >
                    <FolderOpen className="w-3.5 h-3.5" />
                    <span>載入案件</span>
                  </button>
                </div>
              ))
            )}
          </div>

          <div className="px-5 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
            <span>支援直接將修改之事實與筆錄快照入庫</span>
            <button
              onClick={() => setShowCasesModal(false)}
              className="px-4 py-1.5 rounded-lg bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-medium transition cursor-pointer"
            >
              關閉
            </button>
          </div>
        </div>
      </div>
    );
  }
}
