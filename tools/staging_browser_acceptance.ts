import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';

const base = (process.env.JUDICIAL3_STAGING_URL || '').replace(/\/$/, '');
const username = process.env.JUDICIAL3_STAGING_TEST_USERNAME || '';
const password = process.env.JUDICIAL3_STAGING_TEST_PASSWORD || '';
const evidenceDir = path.resolve(process.env.JUDICIAL3_EVIDENCE_DIR || 'artifacts/staging-browser');
if (!base.startsWith('https://') || !username || !password) {
  console.log('STAGING_BROWSER_BLOCKED reason=url_or_test_credentials_missing');
  process.exitCode = 2;
} else {
  fs.mkdirSync(evidenceDir, { recursive: true });
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  const consoleErrors: string[] = [];
  const networkErrors: string[] = [];
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text().slice(0, 300)); });
  page.on('requestfailed', (request) => networkErrors.push(`${request.method()} ${new URL(request.url()).pathname}`));
  let failed = 0;
  const check = (name: string, ok: boolean, detail = '') => {
    if (!ok) failed += 1;
    console.log(`[${ok ? 'PASS' : 'FAIL'}] ${name}${detail ? ` :: ${detail}` : ''}`);
  };
  try {
    const ready = await page.request.get(`${base}/api/health/ready`);
    check('LIVE-HEALTH-READY', ready.status() === 200, `status=${ready.status()}`);
    const anonymous = await page.request.get(`${base}/api/auth/me`);
    check('LIVE-ANONYMOUS-REJECTED', anonymous.status() === 401, `status=${anonymous.status()}`);
    const wrong = await page.request.post(`${base}/api/auth/login`, { data: { username, password: `${password}-wrong` } });
    check('LIVE-WRONG-PASSWORD-REJECTED', wrong.status() === 401, `status=${wrong.status()}`);
    await page.goto(base, { waitUntil: 'domcontentloaded' });
    await page.locator('#login-name').fill(username);
    await page.locator('#login-password').fill(password);
    await page.getByRole('button', { name: /登入/ }).click();
    await page.waitForLoadState('networkidle');
    const cookies = await context.cookies();
    const session = cookies.find((cookie) => cookie.name.includes('judicial3_session'));
    check('LIVE-SESSION-COOKIE', !!session && session.httpOnly && session.secure && session.sameSite !== 'None',
      session ? `httpOnly=${session.httpOnly} secure=${session.secure} sameSite=${session.sameSite} path=${session.path}` : 'missing');
    const axe = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
    const blocking = axe.violations.filter((item) => item.impact === 'critical' || item.impact === 'serious');
    check('LIVE-AXE', blocking.length === 0, `critical_or_serious=${blocking.length}`);
    await page.screenshot({ path: path.join(evidenceDir, 'authenticated.png'), fullPage: true });
    await page.reload({ waitUntil: 'domcontentloaded' });
    check('LIVE-SESSION-RELOAD', !(await page.locator('#login-name').isVisible().catch(() => false)));
    await page.getByRole('button', { name: '登出' }).click();
    await page.locator('#login-name').waitFor({ state: 'visible' });
    check('LIVE-LOGOUT', true);
    check('LIVE-CONSOLE-ERRORS', consoleErrors.length === 0, `count=${consoleErrors.length}`);
    check('LIVE-NETWORK-ERRORS', networkErrors.length === 0, `count=${networkErrors.length}`);
    fs.writeFileSync(path.join(evidenceDir, 'summary.json'), JSON.stringify({
      testedAt: new Date().toISOString(), commitSha: process.env.JUDICIAL3_RELEASE_COMMIT_SHA || process.env.GITHUB_SHA || 'UNKNOWN', checksFailed: failed,
      consoleErrorCount: consoleErrors.length, networkErrorCount: networkErrors.length,
    }, null, 2));
  } catch (error) {
    check('LIVE-BROWSER-HARNESS', false, error instanceof Error ? error.name : 'unknown');
  } finally {
    await context.close();
    await browser.close();
  }
  console.log(`STAGING_BROWSER_${failed ? 'FAIL' : 'PASS'} failed=${failed}`);
  process.exitCode = failed ? 1 : 0;
}
