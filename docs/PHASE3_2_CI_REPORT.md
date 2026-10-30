# Phase 3.2 CI 報告

## 設計

- **PASS（靜態 FACT）**：`.github/workflows/ci.yml` 於 Pull Request 與 `main` push 觸發。
- **PASS（靜態 FACT）**：Workflow 執行 `npm ci --legacy-peer-deps`、`npm run lint`、`npm test`、`npm run build` 與 Python audit。
- **PASS（靜態 FACT）**：CI 不宣告或讀取 production database credentials；embedded/local PostgreSQL 與 Render live validation 分開標示。
- **PASS（實作 FACT）**：沒有外部 test URL 時，`tools/judicial3_postgres_acceptance.py` 會啟動 `tools/postgres_acceptance_embedded.ts`；它建立 disposable PostgreSQL、驗證 bootstrap 後 migration、idempotent rerun 與 provisioning identity。
- **NOT_RUN（實作 FACT）**：Windows embedded-postgres 失敗後會重設 server process，無法可靠保留 failure-case ledger inspection；因此 missing-role rollback 仍須由 Render staging 驗證，不能標示 PASS。
- **PASS（靜態 FACT）**：audit exit code `1` 會使 workflow 失敗；exit code `2` 只代表外部驗收 `BLOCKED`/`NOT_RUN`，不會被報告為 live PASS。

## 執行證據

- **NOT_RUN**：本次尚未取得 GitHub Actions run URL；PR 建立後須以實際 run 結果更新。
- **NOT_RUN**：在本機安裝依賴並執行 CI 完整命令的結果，記錄於 final report，不以靜態 workflow 內容替代。
