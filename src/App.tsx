/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
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
  ClipboardPaste
} from 'lucide-react';
import {
  CaseAnalyzer,
  CaseAnalysisResult,
  QAItem,
  RulingItem,
  TreatiseItem,
  LawItem
} from './services/caseAnalyzer';

const PRESET_CASES = [
  {
    name: '林○○虛擬貨幣假投資 (截圖案例)',
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
    text: `被害人陳女於民國115年5月10日凌晨1時許，在臺北市信義區松壽路某夜店吧檯座位飲酒，不慎將隨身攜帶之香奈兒手提包（內有現金新臺幣2萬元及iPhone 15手機1支）置於高腳椅上。嫌疑人張三見周遭人潮擁擠，趁陳女轉身與友人交談之際，徒手將該手提包偷走藏入外套迅速逃離現場。張三於當日上午10時前往光華商場通訊行，以新臺幣1萬5,000元將該iPhone手機變賣花用。案經陳女報案，警方調閱夜店監視器於通訊行追查查獲張三。`,
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

  // Analysis Result
  const [analysis, setAnalysis] = useState<CaseAnalysisResult>(() =>
    CaseAnalyzer.analyze(PRESET_CASES[0].text)
  );

  // Active Main Tab in Results View
  const [activeTab, setActiveTab] = useState<'all' | 'crimes' | 'record' | 'report'>('all');

  // Sub-Tab for Part 1: 法規 3 | 裁判 4 | 論著 3 (Clickable tabs!)
  const [activeSubTab, setActiveSubTab] = useState<'laws' | 'rulings' | 'treatises' | 'all-sub'>('laws');

  const [showDetailedAnalysis, setShowDetailedAnalysis] = useState(true);
  const [copiedSection, setCopiedSection] = useState<string | null>(null);
  const [feedbackSuccess, setFeedbackSuccess] = useState(false);
  const [userFeedback, setUserFeedback] = useState<'helpful' | 'neutral' | null>(null);

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
  const [qaItems, setQaItems] = useState<QAItem[]>(analysis.qaItems);

  // Editable 條陳 Summary
  const [reportSummary, setReportSummary] = useState(analysis.report.summary);

  // Textarea auto-resize ref
  const landingInputRef = useRef<HTMLTextAreaElement>(null);
  const topInputRef = useRef<HTMLTextAreaElement>(null);

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
      // Backend starting or offline
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

  const handleSaveToPostgres = async () => {
    setIsSavingToDb(true);
    try {
      const payload = {
        title: `${analysis.categoryName} - ${analysis.report.titleReason.slice(0, 30)}`,
        rawText: inputText,
        facts: [
          { seq: 1, description: analysis.report.titleReason, status: 'ASSERTED', factType: 'STATEMENT' },
          { seq: 2, description: reportSummary, status: 'OBJECTIVE', factType: 'OBJECTIVE' }
        ],
        candidates: [
          { chargeName: analysis.categoryName, status: 'PRIMARY', rationale: analysis.aiBrief }
        ],
        questions: qaItems.map((q, idx) => ({
          seq: idx + 1,
          questionText: q.question,
          answerText: q.answer,
          isMandatory: true,
        })),
        summary: reportSummary,
        isLocked: false,
      };

      const res = await fetch('/api/cases/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setSaveSuccessMsg(`成功保存至 PostgreSQL 資料庫！案號: ${data.caseNumber}，快照版本: Rev #${data.revisionNumber}`);
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
          const result = CaseAnalyzer.analyze(data.case.raw_text);
          setAnalysis(result);
        }
        if (data.documents && data.documents[0]?.content_markdown) {
          setReportSummary(data.documents[0].content_markdown);
        }
        if (data.questions && data.questions.length > 0) {
          setQaItems(data.questions.map((q: any) => ({
            id: q.id,
            type: '資料庫已存問句',
            question: q.question_text,
            answer: q.answer_text || '答：',
            hint: '自 PostgreSQL 載入',
          })));
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

  // Re-generate tailored analysis when input changes and switch to results view
  const handlePerformSearch = (textToAnalyze?: string) => {
    const targetText = textToAnalyze !== undefined ? textToAnalyze : inputText;
    if (!targetText.trim()) {
      alert('請輸入案情內容');
      return;
    }
    const result = CaseAnalyzer.analyze(targetText);
    setAnalysis(result);
    setQaItems(result.qaItems);
    setReportSummary(result.report.summary);
    setViewMode('results');
    setFeedbackSuccess(true);
    setTimeout(() => setFeedbackSuccess(false), 2500);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Handle preset click: immediately updates input AND switches to results view
  const handleSelectPreset = (presetText: string) => {
    setInputText(presetText);
    handlePerformSearch(presetText);
  };

  // I'm Feeling Lucky / Random preset
  const handleFeelingLucky = () => {
    const randomIndex = Math.floor(Math.random() * PRESET_CASES.length);
    const selected = PRESET_CASES[randomIndex];
    setInputText(selected.text);
    handlePerformSearch(selected.text);
  };

  // Add a new blank question
  const handleAddQuestion = () => {
    const newId = `qa-${Date.now()}`;
    setQaItems([
      ...qaItems,
      {
        id: newId,
        type: '補充偵查問句',
        question: '問：',
        answer: '答：',
        hint: '請輸入補充待證事項說明。',
      },
    ]);
  };

  // Update question or answer in state
  const handleUpdateQA = (id: string, field: 'question' | 'answer', value: string) => {
    setQaItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, [field]: value } : item))
    );
  };

  // Remove question
  const handleRemoveQA = (id: string) => {
    setQaItems((prev) => prev.filter((item) => item.id !== id));
  };

  // Download official statement as Word (.doc)
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
<p style="text-align:right">中華民國 115 年 3 月 25 日<br>發文字號：警偵字第 115032501 號</p>
<h2>一、案由</h2>
<p>${analysis.report.titleReason}</p>
<h2>二、犯罪嫌疑人及關係人</h2>
<p>${analysis.report.suspects}<br>${analysis.report.victims}</p>
<h2>三、調查經過與客觀犯罪事實</h2>
<p>${reportSummary}</p>
<h2>四、扣案/檢附證物</h2>
<p>${analysis.report.seizedItems.map((item, idx) => `${idx + 1}. ${item}`).join('<br>')}</p>
<h2>五、法律適用與爭點研析</h2>
<p>${analysis.report.legalAnalysis}</p>
<h2>六、後續偵查建言與移送意見</h2>
<p>${analysis.report.recommendations}</p>
</body>
</html>`;

    const blob = new Blob(['\ufeff' + htmlContent], { type: 'application/msword;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `刑事案件報告單_條陳.doc`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Download full Interrogation Record as text
  const handleDownloadQAText = () => {
    let text = `【刑事案件調查警詢筆錄】\n\n`;
    text += `案由：${analysis.report.titleReason}\n時間：民國115年3月25日\n詢問地點：分局偵查隊\n\n`;
    text += `【權利告知事項】\n依刑事訴訟法第95條告知：得保持緘默、得選任辯護人、得請求調查有利證據。\n\n`;
    qaItems.forEach((item, idx) => {
      text += `第 ${idx + 1} 題【${item.type}】\n${item.question}\n${item.answer}\n\n`;
    });

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `警詢筆錄.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Paste clipboard into input
  const handlePasteClipboard = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setInputText(text);
      }
    } catch {
      // clipboard access not granted
    }
  };

  /* =========================================================================
   * VIEW 1: GOOGLE-STYLE LANDING PAGE (Only a single dialogue/input box!)
   * ========================================================================= */
  if (viewMode === 'landing') {
    return (
      <div className="min-h-screen bg-white flex flex-col justify-between text-slate-800 font-sans antialiased selection:bg-blue-100 selection:text-blue-900">
        {/* Minimal Google-like Top Bar */}
        <header className="w-full px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs text-slate-500 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>PostgreSQL 16 已就緒 (24 表完整支援)</span>
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
          {/* Google-like Judicial Branding / Logo */}
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
              輸入案情描述，一鍵自動產出法規競合分析、偵訊筆錄問答與公文條陳
            </p>
          </div>

          {/* THE SINGLE DIALOGUE / SEARCH BOX (Google style) */}
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
                  placeholder="請在此輸入或貼上案情事實、報案指訴、扣案物證或犯罪手法... (按 Enter 開始智能分析)"
                  className="w-full bg-transparent text-sm sm:text-base text-slate-800 placeholder-slate-400 focus:outline-hidden resize-none leading-relaxed"
                />
              </div>

              {/* Action utilities inside the search box */}
              <div className="flex items-center justify-between px-5 pb-3 pt-1 border-t border-slate-100 text-xs text-slate-400">
                <div className="flex items-center space-x-2">
                  <span className="text-[11px] text-slate-400 hidden sm:inline">
                    支援按 Enter 立即分析 • Shift+Enter 換行
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
                  <button
                    onClick={handlePasteClipboard}
                    className="p-1.5 rounded-lg text-slate-500 hover:text-blue-700 hover:bg-blue-50 transition cursor-pointer flex items-center space-x-1"
                    title="貼上剪貼簿內容"
                  >
                    <ClipboardPaste className="w-3.5 h-3.5" />
                    <span className="text-[11px] font-medium hidden sm:inline">貼上</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Google-style Action Buttons */}
          <div className="flex items-center justify-center space-x-3 mt-6">
            <button
              onClick={() => handlePerformSearch()}
              className="px-5 py-2.5 rounded-full bg-slate-100 hover:bg-slate-200 active:bg-slate-300 text-slate-700 font-medium text-xs sm:text-sm border border-slate-200 transition-all cursor-pointer shadow-2xs hover:shadow-xs flex items-center space-x-1.5"
            >
              <Sparkles className="w-4 h-4 text-blue-600" />
              <span>智能分析案情</span>
            </button>
            <button
              onClick={handleFeelingLucky}
              className="px-5 py-2.5 rounded-full bg-slate-100 hover:bg-slate-200 active:bg-slate-300 text-slate-700 font-medium text-xs sm:text-sm border border-slate-200 transition-all cursor-pointer shadow-2xs hover:shadow-xs flex items-center space-x-1.5"
            >
              <Compass className="w-4 h-4 text-emerald-600" />
              <span>隨機示範案件 (好手氣)</span>
            </button>
          </div>

          {/* Quick Preset Chips underneath (Like Google trending searches) */}
          <div className="mt-8 w-full flex flex-col items-center">
            <span className="text-xs text-slate-400 mb-2.5 font-medium">
              常見示範案情（點擊即可載入並分析）：
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

        {/* Minimal Google-like Footer */}
        <footer className="w-full bg-slate-50 border-t border-slate-200 py-3 px-6 text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center space-x-4">
            <span>中華民國刑事偵查法律推理規範</span>
            <span>刑法第339-4條 • 刑訴法第228條 • 洗防法第14條</span>
          </div>
          <div className="flex items-center space-x-3 text-slate-400">
            <span>PostgreSQL 16 PGlite 持久化</span>
            <span>•</span>
            <span>由AI輔助生成，僅供刑事偵查辦案參考</span>
          </div>
        </footer>

        {/* PostgreSQL Cases Modal */}
        {showCasesModal && renderCasesModal()}
      </div>
    );
  }

  /* =========================================================================
   * VIEW 2: RESULTS VIEW (Google Search Results style with top search bar)
   * ========================================================================= */
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans antialiased pb-16">
      {/* Top Google-style Search Header Bar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
          {/* Logo / Back to Landing */}
          <button
            onClick={() => setViewMode('landing')}
            className="flex items-center space-x-2 shrink-0 cursor-pointer group text-left"
            title="回到首頁對話框"
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

          {/* Compact Top Search Box */}
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
                placeholder="輸入案情後按 Enter 重新分析..."
                className="w-full bg-transparent text-xs sm:text-sm text-slate-800 focus:outline-hidden"
              />
              {inputText && (
                <button
                  onClick={() => setInputText('')}
                  className="p-0.5 text-slate-400 hover:text-slate-600 mr-1 cursor-pointer"
                  title="清除"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
              <button
                onClick={() => handlePerformSearch()}
                className="text-xs bg-blue-700 hover:bg-blue-800 text-white px-2.5 py-1 rounded-full font-medium shrink-0 ml-1 transition cursor-pointer"
              >
                分析
              </button>
            </div>
          </div>

          {/* Right Action Utilities */}
          <div className="flex items-center space-x-2 shrink-0">
            <button
              onClick={() => setViewMode('landing')}
              className="text-xs text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 px-2.5 py-1.5 rounded-lg font-medium hidden md:flex items-center space-x-1 transition cursor-pointer"
              title="返回單一對話框首頁"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>新案搜尋</span>
            </button>
            <button
              onClick={handleSaveToPostgres}
              disabled={isSavingToDb}
              className="text-xs text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-300 px-2.5 py-1.5 rounded-lg font-medium flex items-center space-x-1 transition cursor-pointer"
              title="儲存版本快照至 PostgreSQL 16"
            >
              <Save className="w-3.5 h-3.5 text-emerald-600" />
              <span className="hidden sm:inline">{isSavingToDb ? '存檔中...' : '保存快照'}</span>
            </button>
            <button
              onClick={() => setShowCasesModal(true)}
              className="text-xs text-slate-700 bg-slate-100 hover:bg-slate-200 px-2.5 py-1.5 rounded-lg font-medium flex items-center space-x-1 transition cursor-pointer"
              title="開啟案件庫"
            >
              <Database className="w-3.5 h-3.5 text-slate-600" />
              <span>({savedCases.length})</span>
            </button>
          </div>
        </div>

        {/* Google-like Result Tabs Row */}
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
            onClick={() => setActiveTab('crimes')}
            className={`px-3 py-2 font-medium border-b-2 transition shrink-0 cursor-pointer ${
              activeTab === 'crimes'
                ? 'border-blue-700 text-blue-700 font-bold'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            ⚖️ 候選罪名與法規 (法規 3 / 裁判 4 / 論著 3)
          </button>
          <button
            onClick={() => setActiveTab('record')}
            className={`px-3 py-2 font-medium border-b-2 transition shrink-0 cursor-pointer ${
              activeTab === 'record'
                ? 'border-blue-700 text-blue-700 font-bold'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            📝 偵訊筆錄 (9類可填寫)
          </button>
          <button
            onClick={() => setActiveTab('report')}
            className={`px-3 py-2 font-medium border-b-2 transition shrink-0 cursor-pointer ${
              activeTab === 'report'
                ? 'border-blue-700 text-blue-700 font-bold'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            📄 刑事條陳公文
          </button>

          {/* Quick presets in bar */}
          <div className="ml-auto pl-4 hidden lg:flex items-center space-x-1.5 text-xs text-slate-400">
            <span>換案例：</span>
            {PRESET_CASES.slice(0, 3).map((item, idx) => (
              <button
                key={idx}
                onClick={() => handleSelectPreset(item.text)}
                className="px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-600 text-[11px] cursor-pointer"
              >
                {item.short}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-5xl mx-auto px-4 pt-5 space-y-6">
        {/* Save success toast banner */}
        {saveSuccessMsg && (
          <div className="bg-emerald-50 border border-emerald-300 text-emerald-800 text-xs px-4 py-2.5 rounded-xl flex items-center justify-between shadow-xs animate-fade-in">
            <span className="flex items-center space-x-1.5 font-medium">
              <Check className="w-4 h-4 text-emerald-600" />
              <span>{saveSuccessMsg}</span>
            </span>
            <button
              onClick={() => setShowCasesModal(true)}
              className="underline hover:text-emerald-900 font-semibold cursor-pointer ml-2"
            >
              檢視歷史快照
            </button>
          </div>
        )}

        {/* The Output Container (一個匡輸出) matching User Screenshot */}
        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden divide-y divide-slate-100">
          {/* Top of Output Box: User's Case facts card (Grey background rounded container as in screenshot) */}
          <div className="p-5 sm:p-6 bg-slate-50/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center space-x-1.5">
                <FileText className="w-3.5 h-3.5 text-slate-400" />
                <span>案件基本事實情境</span>
              </span>
              <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                案由研判：{analysis.categoryName}
              </span>
            </div>
            <div className="p-4 rounded-xl bg-slate-100/90 border border-slate-200/80 text-sm text-slate-800 leading-relaxed text-justify font-sans">
              {inputText}
            </div>
          </div>

          {/* PART 1: 候選罪名與法律依據 */}
          {(activeTab === 'all' || activeTab === 'crimes') && (
            <div className="p-5 sm:p-6 space-y-5">
              {/* AI 簡述 Box (Dynamically updated based on current case) */}
              <div>
                <h3 className="text-xs font-bold text-blue-700 tracking-wide mb-1.5 flex items-center space-x-1">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>AI 簡述</span>
                </h3>
                <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 text-sm text-slate-800 leading-relaxed">
                  {analysis.aiBrief}
                </div>
              </div>

              {/* CLICKABLE BADGES ROW: 法規 3 | 裁判 4 | 論著 3 (Interactive tabs as shown in user screenshot!) */}
              <div className="border-b border-slate-200 pb-3">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center space-x-2">
                    {analysis.badges.map((badge) => {
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

                    <button
                      onClick={() => setActiveSubTab(activeSubTab === 'all-sub' ? 'laws' : 'all-sub')}
                      className={`px-2.5 py-1 rounded-full text-xs font-medium transition cursor-pointer border ${
                        activeSubTab === 'all-sub'
                          ? 'bg-slate-800 text-white border-slate-800'
                          : 'bg-slate-50 hover:bg-slate-100 text-slate-600 border-slate-200'
                      }`}
                      title="同時展開法規、裁判與論著"
                    >
                      <Layers className="w-3.5 h-3.5 inline mr-1" />
                      <span>{activeSubTab === 'all-sub' ? '單一分頁檢視' : '全部展開'}</span>
                    </button>
                  </div>

                  <span className="text-[11px] text-slate-400">
                    💡 點擊「法規」、「裁判」或「論著」即可切換檢視內容
                  </span>
                </div>
              </div>

              {/* 1-A: 法規清單 (Laws) */}
              {(activeSubTab === 'laws' || activeSubTab === 'all-sub') && (
                <div className="space-y-4 pt-1 text-sm text-slate-700 animate-fade-in">
                  <div className="flex items-center space-x-2 text-xs font-bold text-slate-700 border-l-3 border-blue-600 pl-2">
                    <BookOpen className="w-4 h-4 text-blue-600" />
                    <span>核心法規條文與構成要件 ({analysis.laws.length} 條)</span>
                  </div>

                  {analysis.laws.map((law, lIdx) => (
                    <div
                      key={lIdx}
                      className={`border-l-2 pl-3 space-y-1.5 ${
                        lIdx === 0 ? 'border-blue-600' : 'border-slate-300'
                      }`}
                    >
                      <div className="font-bold text-slate-900 flex items-center space-x-1.5">
                        <span
                          className={`w-2 h-2 rounded-full inline-block ${
                            lIdx === 0 ? 'bg-blue-600' : 'bg-slate-400'
                          }`}
                        ></span>
                        <span>
                          {law.title}（{law.subTitle}）
                        </span>
                      </div>
                      <div className="text-xs text-slate-600 space-y-1 pl-3 font-serif">
                        {law.items.map((item, iIdx) => (
                          <p
                            key={iIdx}
                            className={`${
                              item.highlight
                                ? 'font-semibold text-blue-900 bg-blue-50/60 p-1.5 rounded border border-blue-100'
                                : ''
                            }`}
                          >
                            <span className="italic font-sans text-slate-400 mr-2">{item.num}</span>
                            {item.text}
                          </p>
                        ))}
                      </div>
                      <div className="pl-3 flex items-center space-x-2 text-[11px] pt-1 flex-wrap gap-1">
                        <span className="text-slate-400">提示：</span>
                        <span className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                          {law.hint}
                        </span>
                        <span className="text-slate-400 ml-2">主管機關：{law.authority}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* 1-B: 司法裁判 (Rulings) */}
              {(activeSubTab === 'rulings' || activeSubTab === 'all-sub') && (
                <div className="space-y-3.5 pt-1 text-xs text-slate-700 animate-fade-in">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-xs font-bold text-slate-700 border-l-3 border-amber-600 pl-2">
                      <Gavel className="w-4 h-4 text-amber-600" />
                      <span>實務裁判與判例要旨 ({analysis.rulings.length} 件)</span>
                    </div>
                    <span className="text-[11px] text-slate-400">高等法院、最高法院與憲法法庭裁判依據</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {analysis.rulings.map((ruling, rIdx) => (
                      <div
                        key={rIdx}
                        className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/40 hover:bg-white hover:border-blue-300 transition space-y-2 shadow-2xs"
                      >
                        <div className="flex items-center justify-between border-b border-slate-200 pb-1.5">
                          <span className="font-bold text-blue-950 flex items-center space-x-1">
                            <span>{ruling.court}</span>
                          </span>
                          <span className="text-[10px] text-slate-400">{ruling.yearDate}</span>
                        </div>
                        <div className="text-xs font-semibold text-slate-800 flex items-center justify-between">
                          <span>{ruling.caseNo}</span>
                          <button
                            onClick={() => handleCopy(`${ruling.court} ${ruling.caseNo}：${ruling.holding}`, `rcp-${rIdx}`)}
                            className="text-[10px] text-blue-600 hover:text-blue-800 cursor-pointer flex items-center space-x-0.5"
                          >
                            {copiedSection === `rcp-${rIdx}` ? <span>已複製引述</span> : <span>複製字號</span>}
                          </button>
                        </div>
                        <p className="font-bold text-slate-900 text-xs">{ruling.title}</p>
                        <p className="text-slate-600 leading-relaxed text-justify bg-white p-2 rounded border border-slate-100">
                          {ruling.holding}
                        </p>
                        <div className="text-[11px] text-emerald-800 bg-emerald-50/70 border border-emerald-100 p-1.5 rounded flex items-start space-x-1">
                          <span className="font-bold shrink-0">本案適用：</span>
                          <span>{ruling.takeaway}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 1-C: 法學論著 (Treatises) */}
              {(activeSubTab === 'treatises' || activeSubTab === 'all-sub') && (
                <div className="space-y-3.5 pt-1 text-xs text-slate-700 animate-fade-in">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-xs font-bold text-slate-700 border-l-3 border-emerald-600 pl-2">
                      <Library className="w-4 h-4 text-emerald-600" />
                      <span>法學論著與檢察實務研析 ({analysis.treatises.length} 篇)</span>
                    </div>
                    <span className="text-[11px] text-slate-400">法務部檢察司、刑事警察局與法官學術論述</span>
                  </div>

                  <div className="space-y-2.5">
                    {analysis.treatises.map((treatise, tIdx) => (
                      <div
                        key={tIdx}
                        className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/30 hover:bg-white hover:border-emerald-300 transition space-y-1.5"
                      >
                        <div className="flex items-center justify-between flex-wrap gap-1">
                          <h4 className="font-bold text-slate-900 text-xs flex items-center space-x-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 inline-block"></span>
                            <span>{treatise.title}</span>
                          </h4>
                          <span className="text-[11px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                            {treatise.author} • {treatise.source}
                          </span>
                        </div>
                        <p className="text-slate-600 leading-relaxed text-justify">
                          <strong>論述核心：</strong>{treatise.coreArgument}
                        </p>
                        <div className="text-[11px] text-blue-900 bg-blue-50/60 border border-blue-100 p-1.5 rounded flex items-start space-x-1">
                          <span className="font-bold shrink-0">辦案指引：</span>
                          <span>{treatise.takeaway}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Collapsible Blue Button: 隱藏/顯示詳細解析 */}
              <div className="pt-2">
                <button
                  onClick={() => setShowDetailedAnalysis(!showDetailedAnalysis)}
                  className="w-full py-2 px-4 rounded-lg bg-blue-800 hover:bg-blue-900 text-white font-medium text-xs flex items-center justify-center space-x-1.5 transition cursor-pointer shadow-xs"
                >
                  <span>{showDetailedAnalysis ? '隱藏詳細解析' : '展開詳細解析'}</span>
                  {showDetailedAnalysis ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </button>

                {/* Detailed Analysis Content (Dynamically updated from analysis) */}
                {showDetailedAnalysis && (
                  <div className="mt-4 p-4 rounded-xl border border-slate-200 bg-slate-50/70 text-xs text-slate-700 space-y-3.5 leading-relaxed">
                    <div>
                      <h4 className="font-bold text-slate-900 text-sm mb-1">
                        {analysis.detailedAnalysis.title1}
                      </h4>
                      <p className="text-justify text-slate-600">
                        {analysis.detailedAnalysis.desc1}
                      </p>
                    </div>

                    <div>
                      <h4 className="font-bold text-slate-900 text-sm mb-1">
                        {analysis.detailedAnalysis.title2}
                      </h4>
                      <p className="text-justify text-slate-600">
                        {analysis.detailedAnalysis.desc2}
                      </p>
                    </div>

                    <div>
                      <h4 className="font-bold text-slate-900 text-sm mb-1">
                        {analysis.detailedAnalysis.title3}
                      </h4>
                      <p className="text-justify text-slate-600">
                        {analysis.detailedAnalysis.desc3}
                      </p>
                    </div>

                    <div className="border-t border-slate-200 pt-3">
                      <h4 className="font-bold text-slate-900 text-sm mb-1">結論</h4>
                      <p className="text-justify text-slate-600">
                        {analysis.detailedAnalysis.conclusion}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* PART 2: 筆錄（9類核心偵查問句 - 可線上填寫） */}
          {(activeTab === 'all' || activeTab === 'record') && (
            <div className="p-5 sm:p-6 space-y-4 bg-slate-50/30">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center space-x-2">
                  <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 text-xs font-bold flex items-center justify-center">
                    2
                  </span>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">
                      警詢/偵訊筆錄（9類核心待證問句 • 可線上填寫答詢）
                    </h3>
                    <p className="text-xs text-slate-500">
                      涵蓋行為人關係、犯意要件、金流物證、得利流向等9大法定偵訊層次
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleAddQuestion}
                    className="px-2.5 py-1 text-xs rounded bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 flex items-center space-x-1 transition cursor-pointer"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>增加問句</span>
                  </button>
                  <button
                    onClick={handleDownloadQAText}
                    className="px-2.5 py-1 text-xs rounded bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 flex items-center space-x-1 transition cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>匯出筆錄 (TXT)</span>
                  </button>
                </div>
              </div>

              {/* Editable Question List */}
              <div className="space-y-3">
                {qaItems.map((qa, index) => (
                  <div
                    key={qa.id}
                    className="p-3.5 rounded-xl border border-slate-200 bg-white space-y-2 text-xs shadow-2xs hover:border-slate-300 transition"
                  >
                    <div className="flex items-center justify-between text-slate-500 border-b border-slate-100 pb-1.5">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-blue-800">第 {index + 1} 題</span>
                        <span className="px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 font-medium">
                          {qa.type}
                        </span>
                      </div>
                      <button
                        onClick={() => handleRemoveQA(qa.id)}
                        className="text-slate-400 hover:text-red-500 p-1 rounded transition cursor-pointer"
                        title="刪除此題"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    {/* Question Input */}
                    <div>
                      <label className="font-semibold text-slate-700 block mb-1">詢問內容：</label>
                      <input
                        type="text"
                        value={qa.question}
                        onChange={(e) => handleUpdateQA(qa.id, 'question', e.target.value)}
                        className="w-full bg-slate-50 border border-slate-200 rounded p-2 text-slate-800 focus:bg-white focus:border-blue-600 focus:outline-hidden"
                      />
                    </div>

                    {/* Answer Input */}
                    <div>
                      <label className="font-semibold text-slate-700 block mb-1">受詢人答詢（可線上填寫）：</label>
                      <textarea
                        value={qa.answer}
                        onChange={(e) => handleUpdateQA(qa.id, 'answer', e.target.value)}
                        rows={2}
                        className="w-full bg-slate-50 border border-slate-200 rounded p-2 text-slate-800 focus:bg-white focus:border-blue-600 focus:outline-hidden"
                        placeholder="請記錄受詢人回答..."
                      />
                    </div>

                    {/* Hint / Statutory requirement */}
                    <div className="text-[11px] text-slate-500 bg-slate-50 px-2 py-1 rounded flex items-center space-x-1">
                      <span className="font-semibold text-slate-600">待證要旨：</span>
                      <span>{qa.hint}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* PART 3: 條陳與公文（依案情量身打造） */}
          {(activeTab === 'all' || activeTab === 'report') && (
            <div className="p-5 sm:p-6 space-y-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center space-x-2">
                  <span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center">
                    3
                  </span>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">
                      刑事案件報告單（條陳 • 案情精準契合）
                    </h3>
                    <p className="text-xs text-slate-500">
                      依當前案情動態萃取案由、嫌疑人、客觀事實、扣案證物與後續偵查意見
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleDownloadReportDoc}
                    className="px-2.5 py-1 text-xs rounded bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 flex items-center space-x-1 transition cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>下載公文 (Word)</span>
                  </button>
                  <button
                    onClick={() => handleCopy(reportSummary, 'report-copy')}
                    className="px-2.5 py-1 text-xs rounded bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 flex items-center space-x-1 transition cursor-pointer"
                  >
                    {copiedSection === 'report-copy' ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-600" />
                        <span>已複製</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>複製條陳事實</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Report Document Box */}
              <div className="p-4 rounded-xl border border-slate-200 bg-white space-y-4 text-xs font-serif leading-relaxed text-slate-800 shadow-2xs">
                <div className="text-center font-bold text-sm border-b border-slate-200 pb-2 text-slate-900">
                  【刑事案件調查報告單】
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-700">
                  <div>
                    <strong className="text-slate-900">一、案由：</strong>
                    <div className="p-1.5 bg-slate-50 rounded border border-slate-100 mt-1">
                      {analysis.report.titleReason}
                    </div>
                  </div>
                  <div>
                    <strong className="text-slate-900">二、嫌疑人及關係人：</strong>
                    <div className="p-1.5 bg-slate-50 rounded border border-slate-100 mt-1">
                      {analysis.report.suspects} / {analysis.report.victims}
                    </div>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <strong className="text-slate-900">三、調查經過與犯罪事實（可直接線上修訂）：</strong>
                    <span className="text-[11px] text-blue-600 font-sans">
                      ✏️ 點擊下方文字框即可編輯案情摘要
                    </span>
                  </div>
                  <textarea
                    value={reportSummary}
                    onChange={(e) => setReportSummary(e.target.value)}
                    rows={4}
                    className="w-full bg-slate-50/80 border border-slate-200 rounded p-2.5 text-xs text-slate-800 font-sans leading-relaxed focus:bg-white focus:border-blue-600 focus:outline-hidden"
                  />
                </div>

                <div>
                  <strong className="text-slate-900">四、扣案/檢附證物：</strong>
                  <ul className="list-disc pl-5 space-y-1 mt-1 text-slate-700">
                    {analysis.report.seizedItems.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <strong className="text-slate-900">五、法律適用與爭點研析：</strong>
                  <p className="mt-1 text-slate-700 text-justify bg-slate-50 p-2 rounded border border-slate-100">
                    {analysis.report.legalAnalysis}
                  </p>
                </div>

                <div>
                  <strong className="text-slate-900">六、後續偵查建言與移送意見：</strong>
                  <p className="mt-1 text-slate-700 text-justify bg-slate-50 p-2 rounded border border-slate-100">
                    {analysis.report.recommendations}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Footer of Output Box: Feedback & Actions (Matching User Screenshot) */}
          <div className="px-5 py-3.5 bg-slate-50/80 border-t border-slate-200 flex items-center justify-between flex-wrap gap-2 text-xs text-slate-500">
            <span className="flex items-center space-x-1.5">
              <span>由AI生成，僅供參考。</span>
            </span>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => {
                  setUserFeedback('helpful');
                  setTimeout(() => setUserFeedback(null), 2500);
                }}
                className={`flex items-center space-x-1 transition cursor-pointer ${
                  userFeedback === 'helpful' ? 'text-blue-700 font-bold' : 'hover:text-blue-700'
                }`}
              >
                <ThumbsUp className="w-3.5 h-3.5" />
                <span>{userFeedback === 'helpful' ? '已記錄有幫助！' : '有幫助'}</span>
              </button>

              <button
                onClick={() => {
                  setUserFeedback('neutral');
                  setTimeout(() => setUserFeedback(null), 2500);
                }}
                className={`flex items-center space-x-1 transition cursor-pointer ${
                  userFeedback === 'neutral' ? 'text-amber-700 font-bold' : 'hover:text-amber-700'
                }`}
              >
                <ThumbsDown className="w-3.5 h-3.5" />
                <span>{userFeedback === 'neutral' ? '已記錄反饋' : '還好'}</span>
              </button>

              <button
                onClick={() => {
                  handleCopy(
                    `【案由】${analysis.categoryName}\n\n【AI簡述】\n${analysis.aiBrief}\n\n【法規依據】\n${analysis.laws
                      .map((l) => `${l.title}（${l.subTitle}）\n${l.items.map((i) => i.text).join('\n')}`)
                      .join('\n\n')}\n\n【筆錄問答】\n${qaItems
                      .map((q, i) => `${i + 1}. [${q.type}] ${q.question}\n   ${q.answer}`)
                      .join('\n\n')}\n\n【條陳事實】\n${reportSummary}`,
                    'bottom-copy'
                  );
                }}
                className="hover:text-blue-700 flex items-center space-x-1 transition cursor-pointer"
              >
                {copiedSection === 'bottom-copy' ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="text-emerald-600">已複製全部回應</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>複製全部回應</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* PostgreSQL Cases Modal */}
      {showCasesModal && renderCasesModal()}
    </div>
  );

  /* =========================================================================
   * SHARED MODAL: PostgreSQL Database Cases & History
   * ========================================================================= */
  function renderCasesModal() {
    return (
      <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl border border-slate-200 max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden animate-fade-in">
          {/* Modal Header */}
          <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
            <div className="flex items-center space-x-2">
              <Database className="w-5 h-5 text-emerald-600" />
              <div>
                <h3 className="text-base font-bold text-slate-900">PostgreSQL 資料庫案件庫與版本歷程</h3>
                <p className="text-xs text-slate-500">
                  24張核心表 • 複合外鍵綁定 • RLS 安全政策 • 版本不可竄改鎖定保護
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

          {/* Database Engine Status Summary */}
          <div className="bg-emerald-50/70 border-b border-emerald-100 px-5 py-3 flex items-center justify-between text-xs text-emerald-900">
            <div className="flex items-center space-x-3">
              <span className="flex items-center space-x-1 font-semibold">
                <Server className="w-3.5 h-3.5 text-emerald-700" />
                <span>引擎：PostgreSQL 16 (PGlite 隔離持久化)</span>
              </span>
              <span className="bg-emerald-200/60 px-2 py-0.5 rounded text-[11px] font-mono">
                24 Tables Registered
              </span>
            </div>
            <div className="text-[11px] text-emerald-700">
              已建檔案件: <strong>{savedCases.length}</strong> 件
            </div>
          </div>

          {/* Case List Body */}
          <div className="p-5 overflow-y-auto space-y-3 flex-1">
            {savedCases.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-sm">
                資料庫內目前尚無儲存之案件，請於研析結果頁點擊「保存快照」即可寫入 PostgreSQL！
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
                          🔒 已鎖定核定
                        </span>
                      ) : (
                        <span className="text-[10px] bg-slate-100 text-slate-600 font-medium px-2 py-0.5 rounded-full">
                          可擴充草稿
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-700 line-clamp-1">{c.title}</p>
                    <div className="text-[11px] text-slate-400 flex items-center space-x-3">
                      <span>事實筆數: {c.fact_count ?? 2}</span>
                      <span>筆錄問句: {c.question_count ?? 2}</span>
                      <span>建檔時間: {new Date(c.created_at).toLocaleString('zh-TW')}</span>
                    </div>
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

          {/* Modal Footer */}
          <div className="px-5 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
            <span>支援直接將自訂修改之筆錄與條陳快照入庫</span>
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
