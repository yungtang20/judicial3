# Phase 2 獨立重建報告

## 裁決

`PASS`：Phase 2 可由 `6505a2c` 加上 2026-10-29 16:39:38–17:07:08 的已記錄 patch 獨立重建，不需要 Phase 3 的 PostgreSQL runtime、cookie session、RLS、deployment 或 migration 0011/0012。

## 重建方法

1. 保持 `D:\工作用\judicial3` 唯讀。
2. 以 `6505a2c776187706f6b987b4d2d1afc87170d230` 建立隔離 worktree。
3. 以 Codex JSONL session 中的原始 `apply_patch` 作為 `STRONG` 證據。
4. 確認 main 已包含 12:29 前成果，只重播 Phase 2 acceptance 時段；17:21 之後 Phase 3 patch 全數排除。
5. 對複合 patch 只拆分有獨立上下文的 Phase 2 檔案區塊；`package-lock.json` 因歷史 blob 不存在而排除。
6. 使用 `bun install --frozen-lockfile`，再於重建 worktree 重跑全部驗收。

## 可追溯功能

- Fact/Evidence/element/question traceability、`DENIED`/`UNKNOWN`/`PENDING_SEARCH`。
- 問句預期釐清與實際回答分離，回答持久化。
- 案件保存、重開、revision history。
- 刑法第 320/337 條候選映射與未查證法源標記。
- HMAC API 認證、server-authenticated owner、跨使用者隔離。
- 外部 AI 預設關閉且未設定時 HTTP 503。
- production build/start 與靜態 UI。

`tools/judicial3_mvp_audit.py` 的 Phase 2 原始 patch 已找到，因此保留為歷史還原版，不是將 Phase 3 稽核改名，也未複製舊 PASS 數字；本次已重新執行。

## 排除

Phase 3 的 production auth、cookie/CSRF、PostgreSQL runtime、RLS、Render、provision/migrate 工具與其測試均未整合。錯誤分支 `codex/phase2-gate1` 的另一套專案也未搬入。
