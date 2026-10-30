# Phase 3.2.1 Credential Isolation

## 目標與環境

在 `codex/judicial3-phase3-2-1-to-3-3`（基準 `9f55ab8c47e4f8287b436986a2a3a7e036a2c219`）將 Web、Migration、Provisioning 憑證分離。最終實作 SHA 由 PR 與 `git rev-parse HEAD` 留存。

## 執行與證據

- `render.yaml` 的 Web 僅保留 application `DATABASE_URL`，移除 pre-deploy migration 與兩種高權限 URL。
- Production Web 啟動時拒絕任何 migration/provisioning 變數，並要求 `session_user=current_user=judicial3_app`。
- `render.migration-runner.yaml` 是獨立 runner；Migration 身分必須符合預期角色且不可有 cluster-wide 權限。
- `python tools/secret_scan.py`、`npm test`、`npm run test:postgres-embedded` 為本機／CI 證據。

## 結果與限制

Repository 隔離設計經 `npm run lint`、18 個 application/browser tests、embedded PostgreSQL acceptance 與 secret scan 驗證為 `PASS`；Render 現有服務環境變數刪除與重新查詢為 `BLOCKED`，因目前沒有 judicial3 live resource，且未取得可安全建立付費 runner 的方案／費用核准。Production 未修改。下一步是建立獨立 Staging 後執行 live role acceptance。
