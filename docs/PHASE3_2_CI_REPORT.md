# Phase 3.2 CI 報告

## 設計

- **PASS（靜態 FACT）**：`.github/workflows/ci.yml` 於 Pull Request 與 `main` push 觸發。
- **PASS（靜態 FACT）**：Workflow 執行 `npm ci --legacy-peer-deps`、安裝 Playwright Chromium、`npm run lint`、`npm test`、`npm run build` 與 Python audit。
- **PASS（靜態 FACT）**：CI 不宣告或讀取 production database credentials；embedded/local PostgreSQL 與 Render live validation 分開標示。
- **PASS（實作 FACT）**：沒有外部 test URL 時，`tools/judicial3_postgres_acceptance.py` 會啟動 `tools/postgres_acceptance_embedded.ts`；它建立 disposable PostgreSQL、驗證 bootstrap 後 migration、idempotent rerun 與 provisioning identity。
- **NOT_RUN（實作 FACT）**：Windows embedded-postgres 失敗後會重設 server process，無法可靠保留 failure-case ledger inspection；因此 missing-role rollback 仍須由 Render staging 驗證，不能標示 PASS。
- **PASS（靜態 FACT）**：audit exit code `1` 會使 workflow 失敗；exit code `2` 只代表外部驗收 `BLOCKED`/`NOT_RUN`，不會被報告為 live PASS。

## 執行證據

- **PASS（GitHub FACT）**：[PR #2 run 41061500158](https://github.com/yungtang20/judicial3/actions/runs/41061500158) 於 Ubuntu runner 完成，`verify` job 結論為 `SUCCESS`。
- **PASS（GitHub FACT）**：依賴安裝、Playwright Chromium、TypeScript lint、application tests（16/16）、production build 與 Phase 3.2 audit workflow step 全部通過。
- **PASS（語意邊界）**：audit 仍輸出 Render staging `BLOCKED` 與 missing-role failure-case `NOT_RUN`；workflow success 僅證明 repository-local gate，未升級為 Render live PASS。
- **風險**：runner 顯示 `actions/checkout@v4`、`actions/setup-node@v4`、`actions/setup-python@v5` 的 Node.js 20 deprecation warning；本次不影響結論，但後續應隨官方 major release 更新。
