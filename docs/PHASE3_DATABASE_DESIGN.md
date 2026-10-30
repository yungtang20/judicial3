# Phase 3 資料庫設計

正式 runtime 使用 pg pool；PGlite 僅供本機／測試。12 個 forward-only migrations 由 schema_migrations 保存版本、SHA-256 checksum 與時間；PostgreSQL migration 使用 advisory lock，單一 migration 與 ledger row 原子提交，checksum drift／未知版本／legacy 無 ledger 均 fail closed。

withTransaction 對 PostgreSQL client 設定 transaction-local app.current_user_id，完成後由 transaction 自動清除；PGlite 測試以序列化交易避免單一連線交錯。案件儲存另有 idempotency replay 與 optimistic revision check。

真實 PostgreSQL migration、rollback、連線池併發與 app role 權限尚未執行，標示 BLOCKED；PGlite PASS 不升級為 PostgreSQL PASS。
