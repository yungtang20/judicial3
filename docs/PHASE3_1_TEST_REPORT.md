# Phase 3.1 Test Report

本輪應執行 `npm run lint`、`npm test`、`npm run build`、`python tools/judicial3_phase3_audit.py`，並保留 Phase 2 法律情境、corrective、session、CSRF、owner isolation、idempotency、revision lock、browser 與 axe 測試。

PGlite clean-seed、role idempotency、current-user guard 與既有回歸屬於本機補充證據；`tools/judicial3_postgres_acceptance.py` 在沒有外部 URL 時會嘗試 disposable embedded PostgreSQL，安全檢查不滿足時才輸出 `BLOCKED` 並 exit 2。embedded PostgreSQL 16.13 acceptance 已實際完成並輸出 `PASS=1 FAIL=0 NOT_RUN=0 BLOCKED=0 EXIT_CODE=0`。
