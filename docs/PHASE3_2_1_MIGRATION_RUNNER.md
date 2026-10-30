# Phase 3.2.1 Migration Runner

## 目標與設計

基準 SHA `9f55ab8c47e4f8287b436986a2a3a7e036a2c219`。`judicial3-staging-migrator` 為不接受公開流量的 Private Service；只持有 migration `DATABASE_URL` 與預期角色名稱，不持有 provisioning secret。One-Off Job 繼承 base service artifact 與環境，因此不得以 Web 作為 base service。

## 執行流程

`.github/workflows/staging-release.yml` 僅接受已在 `main` 的完整 SHA，先跑 quality gate，再以 `python tools/render_one_off_job.py` 建立 `npm run db:migrate` job；成功後才部署 Web。API 僅輸出 job ID 與狀態。`npm run runner:migration-idle` 的 base process 只回 404。

## 驗證與限制

本機可執行 `python -m py_compile tools/render_one_off_job.py`。Live job、artifact SHA 與 log 為 `NOT_RUN`。目前 runner 方案會有持續費用，Workspace plan 又無法確認，因此建立資源為 `BLOCKED`。Production runner 不在本次建立或觸發範圍。
