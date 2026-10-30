/**
 * Phase 3 browser acceptance test.
 *
 * Runs the real server (Vite middleware + PGlite with the seeded test data) and
 * drives the real UI with Chromium. It is intentionally a standalone script so
 * that it can be rerun from a terminal or CI without a browser plugin:
 *
 *   npx tsx tests/browser_acceptance.test.ts
 *
 * Evidence produced: login/session cookie behaviour, keyboard focus order,
 * axe accessibility scan, blob downloads, network-failure handling, duplicate
 * submit protection, reload persistence and logout revocation.
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { chromium, type Browser, type BrowserContext, type Page } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import { startTestServer, login, type TestServer } from './helpers/httpServer';

const USERNAME = 'lead_investigator_01';
const PASSWORD = 'Judicial3!TestPass2026';
const CASE_TEXT =
  '虛構驗收案情：甲於民國115年1月5日以通訊軟體向乙佯稱可代為投資，乙因而匯款新臺幣十萬元至甲指定之帳戶，甲隨即提領花用。';

interface CheckResult {
  id: string;
  ok: boolean;
  detail: string;
}

const checks: CheckResult[] = [];
function check(id: string, ok: boolean, detail = ''): void {
  checks.push({ id, ok, detail });
  console.log(`[${ok ? 'PASS' : 'FAIL'}] ${id}${detail ? ` :: ${detail}` : ''}`);
}

async function axe(page: Page, id: string): Promise<void> {
  const result = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();
  const blocking = result.violations.filter(
    (violation) => violation.impact === 'critical' || violation.impact === 'serious',
  );
  const summary = blocking
    .map((violation) => `${violation.id}(${violation.impact}):${violation.nodes.length}`)
    .join(',');
  check(id, blocking.length === 0, summary || 'no critical/serious violations');
  if (blocking.length > 0) {
    for (const violation of blocking) {
      for (const node of violation.nodes.slice(0, 8)) {
        console.log(`       ${violation.id} -> ${node.target.join(' ')} :: ${node.failureSummary?.replace(/\s+/g, ' ').slice(0, 220)}`);
      }
    }
  }
}

async function apiJson(base: string, cookie: string, route: string): Promise<any> {
  const response = await fetch(`${base}${route}`, { headers: { cookie } });
  return response.json();
}

let server: TestServer | undefined;
let browser: Browser | undefined;
let context: BrowserContext | undefined;

try {
  server = await startTestServer();
  browser = await chromium.launch();
  context = await browser.newContext({ acceptDownloads: true });
  const page = await context.newPage();

  // ---------------------------------------------------------------- login view
  await page.goto(server.base, { waitUntil: 'domcontentloaded' });
  await page.locator('#login-name').waitFor({ state: 'visible', timeout: 30_000 });
  await axe(page, 'AXE-LOGIN');

  // Keyboard order on the unauthenticated screen: username -> password -> submit.
  await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur());
  await page.keyboard.press('Tab');
  const firstFocus = await page.evaluate(() => document.activeElement?.id);
  await page.keyboard.press('Tab');
  const secondFocus = await page.evaluate(() => document.activeElement?.id);
  await page.keyboard.press('Tab');
  const thirdFocus = await page.evaluate(() => {
    const element = document.activeElement as HTMLElement | null;
    return element ? `${element.tagName}:${element.getAttribute('type') || ''}` : '';
  });
  check(
    'KEYBOARD-LOGIN-ORDER',
    firstFocus === 'login-name' && secondFocus === 'login-password' && thirdFocus === 'BUTTON:submit',
    `${firstFocus} -> ${secondFocus} -> ${thirdFocus}`,
  );

  await page.fill('#login-name', USERNAME);
  await page.fill('#login-password', PASSWORD);
  await page.click('form[aria-labelledby="login-title"] button[type="submit"]');
  await page.locator('textarea[aria-label="案情摘要"]').waitFor({ state: 'visible', timeout: 20_000 });
  check('LOGIN-SUCCESS', true, 'landing view rendered after cookie login');

  const cookies = await context.cookies();
  const sessionCookie = cookies.find((cookie) => cookie.name.includes('judicial3_session'));
  check(
    'COOKIE-FLAGS',
    !!sessionCookie && sessionCookie.httpOnly && sessionCookie.sameSite === 'Strict',
    sessionCookie ? `httpOnly=${sessionCookie.httpOnly} sameSite=${sessionCookie.sameSite} secure=${sessionCookie.secure}` : 'session cookie missing',
  );

  const storage = await page.evaluate(() => ({
    local: Object.keys(localStorage),
    session: Object.keys(sessionStorage),
  }));
  check(
    'NO-CREDENTIAL-IN-LOCALSTORAGE',
    storage.local.every((key) => !/token|auth|jwt|session/i.test(key)),
    `localStorage keys=[${storage.local.join(',')}]`,
  );

  await axe(page, 'AXE-LANDING');

  // -------------------------------------------------------------- analysis view
  await page.fill('textarea[aria-label="案情摘要"]', CASE_TEXT);
  await page.getByRole('button', { name: '智能法律推理涵攝' }).click();
  await page.getByRole('button', { name: '保存快照' }).waitFor({ state: 'visible', timeout: 20_000 });
  check('ANALYZE-RENDER', await page.getByText(CASE_TEXT.slice(0, 12)).first().isVisible(), 'result view contains the submitted case text');

  await axe(page, 'AXE-RESULTS');

  // Keyboard traversal on the results screen. Every stop must be a real
  // interactive element, and focus must keep moving forward.
  await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur());
  const focusTrace: string[] = [];
  for (let index = 0; index < 14; index += 1) {
    await page.keyboard.press('Tab');
    const stop = await page.evaluate(() => {
      const element = document.activeElement as HTMLElement | null;
      if (!element || element === document.body) return 'BODY';
      const name = element.getAttribute('aria-label') || (element.textContent || '').trim().slice(0, 24);
      return `${element.tagName}:${name}`;
    });
    focusTrace.push(stop);
  }
  const interactive = focusTrace.filter((stop) => /^(BUTTON|INPUT|TEXTAREA|A|SELECT):/.test(stop));
  const distinct = new Set(focusTrace).size;
  check(
    'KEYBOARD-RESULTS-TRAVERSAL',
    interactive.length >= 10 && distinct >= 10 && !focusTrace.includes('BODY'),
    `interactive=${interactive.length} distinct=${distinct} trace=${focusTrace.slice(0, 6).join(' | ')}`,
  );
  await page.keyboard.press('Shift+Tab');
  const shiftBack = await page.evaluate(() => {
    const element = document.activeElement as HTMLElement | null;
    return element ? `${element.tagName}:${(element.getAttribute('aria-label') || (element.textContent || '').trim()).slice(0, 24)}` : 'BODY';
  });
  check('KEYBOARD-SHIFT-TAB', shiftBack !== focusTrace[focusTrace.length - 1], `shift+tab -> ${shiftBack}`);

  // --------------------------------------------------------------- downloads
  const txtPath = path.join(os.tmpdir(), `judicial3-browser-${Date.now()}.txt`);
  const [txtDownload] = await Promise.all([
    page.waitForEvent('download', { timeout: 15_000 }),
    page.getByRole('button', { name: /匯出筆錄/ }).click(),
  ]);
  await txtDownload.saveAs(txtPath);
  const txtContent = fs.readFileSync(txtPath, 'utf8');
  check(
    'DOWNLOAD-INTERROGATION-TXT',
    fs.statSync(txtPath).size > 200 && txtContent.includes('權利告知') && txtContent.includes('問：'),
    `bytes=${fs.statSync(txtPath).size} suggested=${txtDownload.suggestedFilename()}`,
  );

  const docPath = path.join(os.tmpdir(), `judicial3-browser-${Date.now()}.doc`);
  const [docDownload] = await Promise.all([
    page.waitForEvent('download', { timeout: 15_000 }),
    page.getByRole('button', { name: /下載條陳 \(Word\)/ }).click(),
  ]);
  await docDownload.saveAs(docPath);
  const docContent = fs.readFileSync(docPath, 'utf8');
  check(
    'DOWNLOAD-REPORT-DOC',
    fs.statSync(docPath).size > 400 && docContent.includes('刑事案件報告單'),
    `bytes=${fs.statSync(docPath).size} suggested=${docDownload.suggestedFilename()}`,
  );
  fs.rmSync(txtPath, { force: true });
  fs.rmSync(docPath, { force: true });

  // --------------------------------------------------- session for API checks
  const apiSession = await login(server.base, USERNAME, PASSWORD);
  check('API-LOGIN', apiSession.status === 200 && !!apiSession.cookie && !!apiSession.csrf, `status=${apiSession.status}`);
  const casesBefore = await apiJson(server.base, apiSession.cookie, '/api/cases');

  const csrfMissing = await page.request.post(`${server.base}/api/auth/logout`, { data: {} });
  check('CSRF-REQUIRED', csrfMissing.status() === 403, `POST /api/auth/logout without X-CSRF-Token -> ${csrfMissing.status()}`);

  const spoof = await fetch(`${server.base}/api/cases`, {
    headers: { 'x-user-id': '22222222-2222-2222-2222-222222222201' },
  });
  check('SPOOFED-USER-HEADER-REJECTED', spoof.status === 401, `x-user-id header without session -> ${spoof.status}`);

  // ------------------------------------------------- network failure on save
  let networkDialog = '';
  page.once('dialog', async (dialog) => {
    networkDialog = dialog.message();
    await dialog.accept();
  });
  await page.route('**/api/cases/save', (route) => route.abort('failed'));
  await page.getByRole('button', { name: '保存快照' }).click();
  await page.waitForTimeout(1_200);
  await page.unroute('**/api/cases/save');
  const casesAfterAbort = await apiJson(server.base, apiSession.cookie, '/api/cases');
  check(
    'NETWORK-ABORT-NO-FALSE-SUCCESS',
    networkDialog.length > 0 && casesAfterAbort.cases.length === casesBefore.cases.length,
    `dialog=${networkDialog.slice(0, 40)} cases=${casesBefore.cases.length}->${casesAfterAbort.cases.length}`,
  );

  // --------------------------------------- duplicate submit creates one case
  await page.evaluate(() => {
    const button = Array.from(document.querySelectorAll('button')).find((candidate) =>
      (candidate.textContent || '').includes('保存快照'),
    ) as HTMLButtonElement | undefined;
    button?.click();
    button?.click();
  });
  await page.getByText(/成功保存至 PostgreSQL 資料庫/).waitFor({ state: 'visible', timeout: 20_000 });
  const successText = await page.getByText(/成功保存至 PostgreSQL 資料庫/).first().textContent();
  const caseNumber = (successText || '').match(/draft-[0-9a-f-]{36}/i)?.[0] || '';
  await page.waitForTimeout(800);
  const casesAfterSave = await apiJson(server.base, apiSession.cookie, '/api/cases');
  const created = casesAfterSave.cases.find((item: any) => item.case_number === caseNumber);
  const details = created ? await apiJson(server.base, apiSession.cookie, `/api/cases/${created.id}`) : null;
  check(
    'DUPLICATE-SUBMIT-ONE-REVISION',
    !!created && details?.revisionHistory?.length === 1 && casesAfterSave.cases.length === casesBefore.cases.length + 1,
    `caseNumber=${caseNumber} revisions=${details?.revisionHistory?.length} cases=${casesBefore.cases.length}->${casesAfterSave.cases.length}`,
  );

  // ------------------------------------------------------ reload persistence
  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.locator('textarea[aria-label="案情摘要"]').waitFor({ state: 'visible', timeout: 20_000 });
  const loginVisibleAfterReload = await page.locator('#login-name').isVisible().catch(() => false);
  check('SESSION-SURVIVES-RELOAD', !loginVisibleAfterReload, 'cookie session kept the user signed in after reload');

  await page.getByRole('button', { name: /案件庫/ }).first().click();
  await page.getByText('PostgreSQL 資料庫案件庫與版本歷程').waitFor({ state: 'visible' });
  const modalHasCase = await page.getByText(caseNumber, { exact: true }).first().isVisible().catch(() => false);
  check('PERSISTED-CASE-VISIBLE-AFTER-RELOAD', modalHasCase, `modal contains ${caseNumber}`);
  await page.getByRole('button', { name: '關閉' }).click();

  // ------------------------------------------------------- logout revocation
  const browserSession = (await context.cookies()).find((cookie) => cookie.name.includes('judicial3_session'));
  const cookieBeforeLogout = browserSession ? `${browserSession.name}=${browserSession.value}` : '';
  await page.getByRole('button', { name: '登出' }).click();
  await page.locator('#login-name').waitFor({ state: 'visible', timeout: 15_000 });
  const meAfterLogout = await fetch(`${server.base}/api/auth/me`, { headers: { cookie: cookieBeforeLogout } });
  check('LOGOUT-REVOKES-SESSION', meAfterLogout.status === 401, `old session cookie /api/auth/me -> ${meAfterLogout.status}`);

  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.locator('#login-name').waitFor({ state: 'visible', timeout: 15_000 });
  check('LOGOUT-SURVIVES-RELOAD', true, 'login form shown after reload');
  await axe(page, 'AXE-LOGIN-AFTER-LOGOUT');
} catch (error) {
  check('BROWSER-HARNESS', false, error instanceof Error ? `${error.message}` : String(error));
} finally {
  await context?.close().catch(() => undefined);
  await browser?.close().catch(() => undefined);
  await server?.close().catch(() => undefined);
}

const failed = checks.filter((entry) => !entry.ok);
console.log(`\nBROWSER_ACCEPTANCE ${failed.length === 0 ? 'PASS' : 'FAIL'} checks=${checks.length} failed=${failed.length}`);
if (failed.length > 0) {
  for (const entry of failed) console.log(`FAILED ${entry.id} :: ${entry.detail}`);
  process.exit(1);
}


