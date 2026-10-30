# Phase 2 / Phase 3 修改鑑識矩陣

基準：`6505a2c776187706f6b987b4d2d1afc87170d230`。原始混合工作目錄 `D:\工作用\judicial3` 僅供讀取；重建於隔離 worktree 完成。

## 證據與時間分界

- `STRONG`：Codex session `rollout-2026-10-26T21-34-56-01a1786b-d79b-7970-ade5-9c85ed372ff7.jsonl` 保存每一筆 `apply_patch`。Phase 2 計畫於 2026-10-29 17:08:33 +08:00 結束；Phase 3 任務於 17:21:43 讀入，17:25 後才開始 Phase 3 patch。
- `STRONG`：Git SHA `6505a2c` 已包含同一 session 12:29 前的 MVP 成果；因此重建只重播 16:39:38–17:07:08 的 Phase 2 驗收 patch。
- `STRONG`：`git reflog --all`、`git stash list`、`git fsck --no-reflogs --unreachable --full` 均未提供另一個 Phase 2 commit/blob。
- `MEDIUM`：`docs/PHASE2_*.md`、`docs/MVP_*.md` 與重跑測試互相印證。
- 修改時間僅作定位，不作歸屬證據。

## Tracked 差異逐檔／逐區塊分類

| 路徑 | 相對 main 的區塊 | 分類 | 判定與依賴 | 獨立套用／人工確認 |
|---|---|---|---|---|
| `.env.example` | Phase 2：dev-session、external AI、model；Phase 3：DB、cookie、origin、bootstrap | `MIXED_SEPARABLE` | session 時序可逐 hunk 分界 | 僅 Phase 2；否 |
| `bun.lock` | Phase 2：`tsx` 移至 runtime dependency；Phase 3：pg/bcrypt/cookie 等 | `MIXED_SEPARABLE` | lock hunk 與 package patch 相符 | 僅 Phase 2；否 |
| `database/migrations/0010_mvp_traceability.sql` | `interview_questions.answer_text` | `PHASE2_ONLY` | 16:41 patch 與 flow test | 是；否 |
| `database/tests/test_data.sql` | role/user seed schema 調整 | `PHASE3_ONLY` | Phase 3 production auth migration 相依 | 否；否 |
| `index.html` | CSP/production HTML 調整 | `PHASE3_ONLY` | 17:21 後 security hardening | 否；否 |
| `package.json` | Phase 2：start/tsx；Phase 3：DB/auth scripts 與 dependencies | `MIXED_SEPARABLE` | Phase 2 production-start test只需 tsx | 僅 Phase 2；否 |
| `scripts/audit_predeploy.py` | Phase 2 external-AI gate；Phase 3 production config checks | `MIXED_SEPARABLE` | session patch 時序 | 僅 Phase 2；否 |
| `server.ts` | Phase 2：HMAC/dev session、503、owner/API 驗證、static start；Phase 3：cookie/CSRF/readiness/error middleware | `MIXED_SEPARABLE` | Phase 2 route tests在無 Phase 3 runtime下通過 | 僅 Phase 2；否 |
| `src/App.tsx` | Phase 2：snapshot restore、問句 CRUD/answer、ARIA、token header；Phase 3：正式登入/session UI | `MIXED_SEPARABLE` | 明確 patch 分界 | 僅 Phase 2；否 |
| `src/server/auth.ts` | Phase 2 HMAC bearer；Phase 3 PostgreSQL cookie session | `MIXED_SEPARABLE` | Phase 2 middleware tests獨立通過 | 保留 HMAC 版；否 |
| `src/server/databaseService.ts` | Phase 2 answer/revision/statute/owner；Phase 3 databaseRuntime/transaction/RLS | `MIXED_SEPARABLE` | PGlite flow證明 Phase 2 不依賴 Phase 3 | 僅 Phase 2；否 |
| `src/services/analyzer.ts` | 移除虛構 auto-fix 值 | `PHASE2_ONLY` | 16:40 Phase 2 acceptance patch | 是；否 |
| `src/services/legalReasoningEngine.ts` | clause split、UNKNOWN 優先、空白 answer、revision snapshot | `PHASE2_ONLY` | 14 情境與 corrective 重跑 | 是；否 |
| `tests/api_auth.test.ts` | Phase 2 HMAC cases；Phase 3 session lifecycle相容改寫 | `MIXED_SEPARABLE` | Phase 2 原 patch可還原 | 僅 Phase 2；否 |
| `tests/api_route_auth.test.ts` | Phase 2 production route/503；Phase 3 cookie/CSRF route | `MIXED_SEPARABLE` | Phase 2 child-process test重跑 | 僅 Phase 2；否 |
| `tests/legal_reasoning_corrective.test.ts` | mixed statement與空答案 regression | `PHASE2_ONLY` | 16:52 patch | 是；否 |
| `tests/mvp_complete_flow.test.ts` | Phase 2 answer/revision；Phase 3 database runtime hooks | `MIXED_SEPARABLE` | Phase 2 PGlite flow獨立通過 | 僅 Phase 2；否 |
| `tools/judicial3_mvp_audit.py` | Phase 2 33-check audit；Phase 3 production checks擴張 | `MIXED_SEPARABLE` | 找到原始 Phase 2 patch，非改名或推測 | 僅 Phase 2；否 |
| `vite.config.ts` | production host/config hardening | `PHASE3_ONLY` | Phase 3 patch | 否；否 |

## Untracked 差異逐檔分類

| 路徑 | 分類 | 理由／處置 |
|---|---|---|
| `docs/ACCEPTANCE_BASELINE.md` | `PHASE2_ONLY` | Phase 2 acceptance patch；納入 |
| `docs/MVP_ACCEPTANCE_MATRIX.md` | `PHASE2_ONLY` | Phase 2 acceptance patch；納入 |
| `docs/MVP_ACCEPTANCE_REPORT.md` | `PHASE2_ONLY` | Phase 2 acceptance patch；納入 |
| `docs/MVP_DEFECTS.md` | `PHASE2_ONLY` | Phase 2 acceptance patch；納入 |
| `docs/PHASE2_ACCEPTANCE_BASELINE.md` | `PHASE2_ONLY` | 17:06 Phase 2 文件；納入 |
| `docs/PHASE2_ACCEPTANCE_REPORT.md` | `PHASE2_ONLY` | 同上；納入 |
| `docs/PHASE2_AUTH_SECURITY.md` | `PHASE2_ONLY` | 同上；納入 |
| `docs/PHASE2_BROWSER_ACCEPTANCE.md` | `PHASE2_ONLY` | 同上；納入，歷史 browser 證據與本次重跑分開表述 |
| `docs/PHASE2_DATABASE_DEPLOYMENT.md` | `PHASE2_ONLY` | 同上；納入 |
| `docs/PHASE2_DEFECTS.md` | `PHASE2_ONLY` | 同上；納入 |
| `docs/PHASE2_EXTERNAL_SERVICES.md` | `PHASE2_ONLY` | 同上；納入 |
| `tests/api_owner_isolation.test.ts` | `PHASE2_ONLY` | 16:59/17:03 Phase 2 patch；納入 |
| `tests/production_start.test.ts` | `PHASE2_ONLY` | 17:00 Phase 2 patch；納入 |
| `database/migrations/0011_production_auth.sql` | `PHASE3_ONLY` | production auth schema；排除 |
| `database/migrations/0012_phase3_security_hardening.sql` | `PHASE3_ONLY` | 名稱與 patch 均明示 Phase 3；排除 |
| `docs/PHASE3_ACCEPTANCE_REPORT.md` | `PHASE3_ONLY` | 排除 |
| `docs/PHASE3_AUTH_DESIGN.md` | `PHASE3_ONLY` | 排除 |
| `docs/PHASE3_BASELINE.md` | `PHASE3_ONLY` | 排除 |
| `docs/PHASE3_DATABASE_DESIGN.md` | `PHASE3_ONLY` | 排除 |
| `docs/PHASE3_DEFECTS.md` | `PHASE3_ONLY` | 排除 |
| `docs/PHASE3_DEPLOYMENT_READINESS.md` | `PHASE3_ONLY` | 排除 |
| `docs/PHASE3_SECURITY_TESTS.md` | `PHASE3_ONLY` | 排除 |
| `render.yaml` | `PHASE3_ONLY` | production deployment blueprint；排除 |
| `src/server/config.ts` | `PHASE3_ONLY` | production config parser；排除 |
| `src/server/databaseRuntime.ts` | `PHASE3_ONLY` | PostgreSQL/PGlite runtime abstraction；排除 |
| `src/server/devSession.ts` | `PHASE3_ONLY` | Phase 3 session architecture；排除 |
| `src/server/errors.ts` | `PHASE3_ONLY` | Phase 3 error boundary；排除 |
| `tests/auth_session_lifecycle.test.ts` | `PHASE3_ONLY` | cookie session lifecycle；排除 |
| `tests/browser_acceptance.test.ts` | `PHASE3_ONLY` | Phase 3 harness；排除 |
| `tests/database_runtime.test.ts` | `PHASE3_ONLY` | databaseRuntime test；排除 |
| `tests/helpers/` | `PHASE3_ONLY` | Phase 3 test infrastructure；排除 |
| `tests/production_config.test.ts` | `PHASE3_ONLY` | Phase 3 config test；排除 |
| `tests/rls_policy.test.ts` | `PHASE3_ONLY` | PostgreSQL/RLS；排除 |
| `tools/migrate.ts` | `PHASE3_ONLY` | Phase 3 migration runner；排除 |
| `tools/provision_user.ts` | `PHASE3_ONLY` | production user provisioning；排除 |
| `package-lock.json` | `AMBIGUOUS` | Phase 2 曾由 npm 產生，之後又被 Phase 3 改寫；原始 Phase 2 lock blob不存在，且目前 npm peer resolution失敗。以已驗證 `bun.lock` 為唯一 lock，排除 |
| `.env`／實際 token／`database/pglite_store/` | `SENSITIVE` | runtime秘密或資料庫狀態；未讀入提交、未納入 |
| `D:\工作用\judicial1` 的 `legal-case-web/` 與 `criminal-investigation-assistant/` | `UNRELATED` | 錯誤 repository/branch內容；未搬入 |

## 統計

- `PHASE2_ONLY`：17 個明確檔案（4 個 tracked 程式／migration／測試，加上 13 個 untracked 報告與測試）。
- `PHASE3_ONLY`：25 個檔案／目錄。
- `MIXED_SEPARABLE`：12 個檔案。
- `MIXED_DEPENDENT`：0 個 Phase 2 必要區塊。
- `AMBIGUOUS`：1 個（`package-lock.json`，已排除）。
- `SENSITIVE`：3 類路徑，均排除。
- `UNRELATED`：2 個錯誤專案根目錄，均排除。

核心 Phase 2 功能沒有依賴 Phase 3 runtime；此結論由乾淨基準上的獨立測試直接證明。
