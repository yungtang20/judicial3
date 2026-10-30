# Phase 3.1 Test Report

本輪應執行 `npm run lint`、`npm test`、`npm run build`、`python tools/judicial3_phase3_audit.py`，並保留 Phase 2 法律情境、corrective、session、CSRF、owner isolation、idempotency、revision lock、browser 與 axe 測試。

PGlite clean-seed、role idempotency、current-user guard 與既有回歸屬於本機證據；`tools/judicial3_postgres_acceptance.py` 缺少隔離資料庫時輸出 `BLOCKED` 並 exit 2。真實 PostgreSQL PASS 只有在 acceptance script 實際連線並完成所有 assertion 後才能成立。
