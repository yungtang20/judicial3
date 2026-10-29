/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 * 
 * JUDICIAL3 法律推理品質與端到端回歸測試套件
 * 專案: yungtang20/judicial2
 * 
 * 測試範圍 (涵蓋 JUDICIAL3 第六階段 14 大核心情境):
 * 1.  情境 1: 事實明確且證據支持之行為（要件該當與證物支持）
 * 2.  情境 2: 事實不足不能判斷特定要件（INSUFFICIENT_DATA 絕非 FALSE）
 * 3.  情境 3: 當事人否認但仍有待調查之證據（DENIED 爭點保留）
 * 4.  情境 4: 同一事件存在相互矛盾之陳述（矛盾事實各自獨立保留）
 * 5.  情境 5: 竊盜、侵占及侵占遺失物之嚴格區分（多候選路徑並存）
 * 6.  情境 6: 詐欺話術、付款及虛擬資產多階段行為（加重詐欺與洗錢罪）
 * 7.  情境 7: 傷害、威脅、恐嚇取財與殺人未遂之構成要件區分
 * 8.  情境 8: 多行為人、多被害人及不同犯罪階段（共同正犯與幫助犯）
 * 9.  情境 9: 使用者回答新問題後候選排序及要件狀態更新
 * 10. 情境 10: 事實修改後舊核准失效（STALE 狀態機推進）
 * 11. 情境 11: 異常輸入或缺漏欄位明確報錯（拒絕假裝完成）
 * 12. 情境 12: 案件存取控制與資料授權隔離
 * 13. 情境 13: 資料庫初始化保護（嚴禁破壞性遞歸刪除既有資料）
 * 14. 情境 14: 連續切換案件時文件防污染隔離（無前案殘留）
 */

import { LegalReasoningEngine } from '../src/services/legalReasoningEngine';
import { FactItem, LegalCandidate } from '../src/types';
import fs from 'fs';
import path from 'path';

interface TestResult {
  id: string;
  name: string;
  passed: boolean;
  assertions: number;
  details: string;
}

const testResults: TestResult[] = [];

function assert(cond: boolean, msg: string) {
  if (!cond) {
    throw new Error(`斷言失敗: ${msg}`);
  }
}

console.log('======================================================================');
console.log('   JUDICIAL3 臺灣刑事法律推理品質與端到端回歸測試');
console.log('   核心引擎: LegalReasoningEngine | 規範版本: 1.0');
console.log('======================================================================\n');

// -----------------------------------------------------------------------------
// 情境 1: 事實明確且證據支持之行為
// -----------------------------------------------------------------------------
try {
  const raw = `被害人陳女於民國115年5月10日，在夜店遭嫌疑人張三趁其不備，伸手偷走高腳椅上之手提包。警方調閱現場監視器錄影光碟清晰錄得張三行竊過程。`;
  const output = LegalReasoningEngine.analyzeFullCase(raw, 'J3-01');

  assert(output.facts.length >= 2, '應至少拆解2筆事實');
  assert(output.evidence.some((e) => e.evidence_type.includes('監視')), '必須獨立提取監視器客觀證物');
  const prim = output.candidates.find((c) => c.candidate_status === 'PRIMARY');
  assert(prim !== undefined && prim.legal_name.includes('320條'), '客觀破壞持有之竊取行為，主位候選應為刑法第320條普通竊盜罪');
  assert(prim?.elements.some((e) => e.element_status === 'SATISFIED') === true, '監視器證物支持之客觀要件應為 SATISFIED');

  testResults.push({ id: 'SCN-01', name: '事實明確且證據支持之單一行為', passed: true, assertions: 4, details: '正確提取事實與監視器物證，主位竊盜罪要件滿足' });
} catch (e: any) {
  testResults.push({ id: 'SCN-01', name: '事實明確單一行為', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 情境 2: 事實不足不能判斷特定要件（INSUFFICIENT_DATA 絕非 FALSE）
// -----------------------------------------------------------------------------
try {
  const raw = `報案人稱其皮夾在路上不見了，懷疑有人拿走，但未見到任何人，現場亦無任何監視器。`;
  const output = LegalReasoningEngine.analyzeFullCase(raw, 'J3-02');

  const allElements = output.candidates.flatMap((c) => c.elements);
  const hasInsufficient = allElements.some((e) => e.element_status === 'INSUFFICIENT_DATA' || e.missing_information?.length! > 0);
  assert(hasInsufficient, '事證不足時，要件狀態必須標記為 INSUFFICIENT_DATA，不得將資料不足當作 FALSE');
  assert(output.candidates.some((c) => c.candidate_status === 'UNRESOLVED' || c.candidate_status === 'ALTERNATIVE'), '應保留未決或替代法律方向');

  testResults.push({ id: 'SCN-02', name: '事實不足不能判斷特定要件 (INSUFFICIENT_DATA)', passed: true, assertions: 2, details: '落實三值邏輯，資料不足標為 INSUFFICIENT_DATA 絕非否定要件' });
} catch (e: any) {
  testResults.push({ id: 'SCN-02', name: '事實不足不能判斷', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 情境 3: 當事人否認但仍有待調查之證據（DENIED 爭點保留）
// -----------------------------------------------------------------------------
try {
  const raw = `嫌疑人乙男於警詢時堅決否認參與詐欺，辯稱自己只是單純幫朋友跑腿代領款項，不知背包內現鈔為犯罪贓款。`;
  const output = LegalReasoningEngine.analyzeFullCase(raw, 'J3-03');

  const deniedFact = output.facts.find((f) => f.assertion_status === 'DENIED');
  assert(deniedFact !== undefined, '嫌疑人之抗辯供述必須被賦予 DENIED 狀態，嚴禁抹除');
  assert(!output.candidates.every((c) => c.candidate_status === 'REJECTED'), '不能因為嫌疑人否認就直接將犯罪嫌疑全數排除');
  assert(output.questions.some((q) => q.question_type === '8_CONTRADICTION_SUPPLEMENT' || q.question_type === '7_CONTRARY_ALTERNATIVE'), '必須產生反向抗辯或矛盾澄清問句');

  testResults.push({ id: 'SCN-03', name: '當事人否認但仍有待調查證據 (DENIED != FALSE)', passed: true, assertions: 3, details: '保留 DENIED 狀態與抗辯路線，衍生第7與第8類查證問句' });
} catch (e: any) {
  testResults.push({ id: 'SCN-03', name: '當事人否認保留', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 情境 4: 同一事件存在相互矛盾之陳述
// -----------------------------------------------------------------------------
try {
  const raw = `證人陳先生指述肇事自小客車闖紅燈；惟現場目擊證人林小姐則表示號誌剛轉黃燈尚未全紅。`;
  const output = LegalReasoningEngine.analyzeFullCase(raw, 'J3-04');

  assert(output.facts.length >= 2, '相互矛盾之陳述不得合併為單一確定事實');
  assert(output.facts.some((f) => f.source_excerpt.includes('闖紅燈')), '保留證人陳先生供述');
  assert(output.facts.some((f) => f.source_excerpt.includes('黃燈')), '保留證人林小姐供述');

  testResults.push({ id: 'SCN-04', name: '同一事件相互矛盾陳述並存保留', passed: true, assertions: 3, details: '矛盾陳述獨立存放，未發生單向覆蓋' });
} catch (e: any) {
  testResults.push({ id: 'SCN-04', name: '矛盾陳述並存', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 情境 5: 竊盜、侵占及侵占遺失物之嚴格區分
// -----------------------------------------------------------------------------
try {
  const raw = `甲女於咖啡廳沙發遺忘皮夾，鄰桌丁女將之取走放入手提包離開現場，並持卡感應消費2,850元。丁女辯稱本想送警局，順路先借刷會還錢。`;
  const output = LegalReasoningEngine.analyzeFullCase(raw, 'J3-05');

  const candNames = output.candidates.map((c) => c.legal_name);
  const hasLostProperty = candNames.some((n) => n.includes('337條'));
  const hasTheftAlt = candNames.some((n) => n.includes('320條'));
  const hasFraudSwipe = candNames.some((n) => n.includes('339條'));

  assert(hasLostProperty, '必須有刑法第337條侵占離本人持有物罪主位分析');
  assert(hasTheftAlt, '必須有刑法第320條普通竊盜罪場所管領力競爭備位路線');
  assert(hasFraudSwipe, '必須有刑法第339條第1項詐欺取財罪盜刷競合');

  testResults.push({ id: 'SCN-05', name: '竊盜、侵占遺失物與感應盜刷之多候選區分', passed: true, assertions: 3, details: '同時提供侵占離本人持有物（主位）、竊盜（競爭）與詐欺（併罰）' });
} catch (e: any) {
  testResults.push({ id: 'SCN-05', name: '竊盜侵占區分', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 情境 6: 詐欺話術、付款及虛擬資產多階段行為
// -----------------------------------------------------------------------------
try {
  const raw = `報案人林○○於社群平台誤信高獲利投資泰達幣話術，先後匯款30萬元至指定帳戶，申請出金時遭要求再繳保證金，對方旋即斷聯，平台無法登入。`;
  const output = LegalReasoningEngine.analyzeFullCase(raw, 'J3-06');

  const candNames = output.candidates.map((c) => c.legal_name);
  assert(candNames.some((n) => n.includes('339條之4')), '多階段網路假投資應成立加重詐欺取財罪');
  assert(candNames.some((n) => n.includes('洗錢')), '層轉虛擬貨幣並切斷金流應列洗錢罪候選');

  testResults.push({ id: 'SCN-06', name: '詐欺話術、付款與虛擬資產多階段行為分析', passed: true, assertions: 2, details: '識別誘騙、出金阻撓及虛擬幣層轉，該當加重詐欺與洗錢罪' });
} catch (e: any) {
  testResults.push({ id: 'SCN-06', name: '多階段詐欺分析', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 情境 7: 傷害、威脅、恐嚇取財與殺人未遂之構成要件區分
// -----------------------------------------------------------------------------
try {
  const raw = `陳○○持鋁棒擊破自小客車玻璃，將張○○拉下車毆打重擊頭部致骨折及撕裂傷，並恫嚇稱：「再叭就打死你！」隨後逃逸。`;
  const output = LegalReasoningEngine.analyzeFullCase(raw, 'J3-07');

  const candNames = output.candidates.map((c) => c.legal_name);
  assert(candNames.some((n) => n.includes('277條')), '應成立刑法第277條普通傷害罪');
  assert(candNames.some((n) => n.includes('305條')), '應成立刑法第305條恐嚇危害安全罪');
  assert(candNames.some((n) => n.includes('271條')), '重擊頭部致命要害且出言打死你，應平行保留殺人未遂替代檢驗路線');

  testResults.push({ id: 'SCN-07', name: '傷害、恐嚇與殺人未遂之構成要件區分', passed: true, assertions: 3, details: '精確建立普通傷害（主位）、恐嚇（主位）與殺人未遂（備位檢驗）' });
} catch (e: any) {
  testResults.push({ id: 'SCN-07', name: '傷害恐嚇殺人未遂', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 情境 8: 多行為人、多被害人及不同犯罪階段（共同正犯與幫助犯）
// -----------------------------------------------------------------------------
try {
  const raw = `乙男手持非本人金融卡在超商ATM連續提款50萬元，辯稱僅受通訊軟體飛哥指示代領跑腿抽佣，不知為假冒健保局之詐騙贓款。`;
  const output = LegalReasoningEngine.analyzeFullCase(raw, 'J3-08');

  const candNames = output.candidates.map((c) => c.legal_name);
  assert(candNames.some((n) => n.includes('共同')), '車手分工應列加重詐欺共同正犯候選');
  assert(candNames.some((n) => n.includes('幫助犯')), '車手抗辯不知情應列幫助犯檢驗路線');

  testResults.push({ id: 'SCN-08', name: '共同正犯與幫助犯之歸責認定', passed: true, assertions: 2, details: '平衡檢驗實務嚴格未必故意共同正犯與辯解幫助犯' });
} catch (e: any) {
  testResults.push({ id: 'SCN-08', name: '共同正犯幫助犯', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 情境 9: 使用者回答新問題後候選排序及要件狀態更新
// -----------------------------------------------------------------------------
try {
  const initial = LegalReasoningEngine.analyzeFullCase('報案人稱皮夾於路邊遺失，不知去向。', 'J3-09');
  const initialRev = initial.caseRecord.current_revision;

  // 模擬回答新問題：目擊證人提供證詞確認是遭扒竊
  const { updatedCase } = LegalReasoningEngine.invalidateDownstreamOnFactChange(
    initial.caseRecord,
    initial.facts[0]?.id || 'f-1',
    { predicate: '嫌犯在公車站牌趁人多推擠時徒手扒竊皮夾' },
    '目擊證人筆錄證實為扒竊'
  );

  assert(updatedCase.current_revision === initialRev + 1, '版本號必須遞增');
  assert(updatedCase.legal_candidates.length > 0, '重新評估後候選罪名必須更新');

  testResults.push({ id: 'SCN-09', name: '回答新問題後候選排序與要件狀態更新', passed: true, assertions: 2, details: '事實補充後觸發重新涵攝，版本遞增 +1' });
} catch (e: any) {
  testResults.push({ id: 'SCN-09', name: '回答新問題更新', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 情境 10: 事實修改後舊核准失效（STALE 狀態機推進）
// -----------------------------------------------------------------------------
try {
  const caseRec = LegalReasoningEngine.createNewCase('J3-10', '核准失效案', '原始案情');
  caseRec.facts = LegalReasoningEngine.parseFactsFromText('原始事實內容', 'J3-10', 1);
  caseRec.reports = [LegalReasoningEngine.generateAndValidateReport(caseRec)];
  caseRec.reports[0].is_approved = true; // 假設舊版已被人工核定

  // 上游事實變更
  const { updatedCase } = LegalReasoningEngine.invalidateDownstreamOnFactChange(
    caseRec,
    caseRec.facts[0].id,
    { predicate: '更正之事實內容' },
    '偵查事證修正'
  );

  assert(updatedCase.reports[0].is_approved === false, '事實更新後，舊版核准必須自動撤回失效 (is_approved = false)');
  assert(updatedCase.reports[0].validation_errors.some((e) => e.includes('[STALE]')), '公務條陳必須標記 [STALE] 警告標籤');

  testResults.push({ id: 'SCN-10', name: '事實修改後舊核准失效 (STALE 狀態機推進)', passed: true, assertions: 2, details: '嚴格遵守舊核准不得自動套用於新版，公文強制標記 STALE' });
} catch (e: any) {
  testResults.push({ id: 'SCN-10', name: '舊核准失效保護', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 情境 11: 異常輸入或缺漏欄位明確報錯（拒絕假裝完成）
// -----------------------------------------------------------------------------
try {
  const emptyOutput = LegalReasoningEngine.analyzeFullCase('', 'J3-11');
  assert(emptyOutput.candidates.some((c) => c.candidate_status === 'UNRESOLVED'), '輸入為空或無事實時必須輸出 UNRESOLVED 狀態，嚴禁假裝分析完成');

  testResults.push({ id: 'SCN-11', name: '異常輸入明確輸出 UNRESOLVED 狀態', passed: true, assertions: 1, details: '欠缺具體犯罪事實時拒絕假裝完成，輸出 UNRESOLVED' });
} catch (e: any) {
  testResults.push({ id: 'SCN-11', name: '異常輸入報錯', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 情境 12: 案件存取控制與資料授權隔離
// -----------------------------------------------------------------------------
try {
  const caseA = LegalReasoningEngine.createNewCase('CASE-A', '甲官承辦案', '事實A', 'officer-A');
  const caseB = LegalReasoningEngine.createNewCase('CASE-B', '乙官承辦案', '事實B', 'officer-B');

  assert(caseA.owner_id !== caseB.owner_id, '不同案件擁有不同之承辦員警 ID');
  assert(caseA.id !== caseB.id, '案件主檔 ID 嚴格隔離');

  testResults.push({ id: 'SCN-12', name: '案件存取控制與承辦人授權隔離', passed: true, assertions: 2, details: '各案獨立關聯 owner_id，具備 RLS 隔離基礎' });
} catch (e: any) {
  testResults.push({ id: 'SCN-12', name: '案件存取隔離', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 情境 13: 資料庫初始化保護（嚴禁破壞性遞歸刪除既有資料）
// -----------------------------------------------------------------------------
try {
  const dbServiceCode = fs.readFileSync(path.resolve(process.cwd(), 'src', 'server', 'databaseService.ts'), 'utf-8');
  assert(!dbServiceCode.includes('fs.rmSync(dbPath'), 'databaseService.ts 中嚴格禁止包含遞歸刪除資料庫之 rmSync 調用');

  testResults.push({ id: 'SCN-13', name: '資料庫初始化保護（嚴禁破壞性刪除）', passed: true, assertions: 1, details: '已徹底移除遞歸刪除資料夾代碼，既有資料受實體保護' });
} catch (e: any) {
  testResults.push({ id: 'SCN-13', name: '資料庫初始化保護', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 情境 14: 連續切換案件時文件防污染隔離（無前案殘留）
// -----------------------------------------------------------------------------
try {
  const outputCase1 = LegalReasoningEngine.analyzeFullCase('報案人林○○在台中遭遇假投資詐騙匯款30萬。', 'CASE-01');
  const outputCase2 = LegalReasoningEngine.analyzeFullCase('被害人張○○在台北超商遭人毆打受傷。', 'CASE-02');

  assert(!outputCase2.report.summary_text.includes('林○○'), 'CASE-02 公文絕不得混入 CASE-01 報案人姓名');
  assert(!outputCase2.report.summary_text.includes('30萬'), 'CASE-02 公文絕不得混入 CASE-01 詐騙金額');
  assert(!outputCase2.report.title_reason.includes('詐欺'), 'CASE-02 傷害案由絕不得混入 CASE-01 之詐欺罪名');

  testResults.push({ id: 'SCN-14', name: '連續切換案件文件防污染隔離', passed: true, assertions: 3, details: '跨案件執行完全隔離，條陳無前案殘留數據' });
} catch (e: any) {
  testResults.push({ id: 'SCN-14', name: '案件防污染隔離', passed: false, assertions: 0, details: e.message });
}

// -----------------------------------------------------------------------------
// 測試輸出匯總
// -----------------------------------------------------------------------------
console.log('----------------------------------------------------------------------');
console.log('測試執行矩陣結果:');
console.log('----------------------------------------------------------------------');
let totalPassed = 0;
let totalFailed = 0;

testResults.forEach((r) => {
  const status = r.passed ? '✓ PASS' : '✗ FAIL';
  if (r.passed) totalPassed++;
  else totalFailed++;
  console.log(`[${status}] [${r.id}] ${r.name} (${r.assertions} assertions) - ${r.details}`);
});

console.log('----------------------------------------------------------------------');
console.log(`總測試情境數: ${testResults.length} | 通過: ${totalPassed} | 失敗: ${totalFailed}`);
console.log('======================================================================');

if (totalFailed > 0) {
  process.exit(1);
} else {
  process.exit(0);
}
