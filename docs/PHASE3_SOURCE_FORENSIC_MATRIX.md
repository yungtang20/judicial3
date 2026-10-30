# Phase 3 來源溯源矩陣

- 整合基準：fb42764a3c706742302d694117b42eb0b7390ebd（origin/main）
- 來源目錄：D:/工作用/judicial3（只讀，原始工作樹未被修改）
- 目標：D:/工作用/judicial3-phase3-integration-wt
- 分支：codex/judicial3-phase3-integration

| 來源／檔案 | 分類 | 證據與整合決定 |
|---|---|---|
| database/migrations/0011_production_auth.sql | PHASE3_ONLY | 原始目錄相對 origin/main 新增；提供 session lifecycle schema，已整合。 |
| database/migrations/0012_phase3_security_hardening.sql | PHASE3_ONLY | 原始目錄相對 origin/main 新增；提供 idempotency、RLS 窄門與索引，已整合。 |
| src/server/config.ts、databaseRuntime.ts、devSession.ts、errors.ts | PHASE3_ONLY | 原始目錄新增且被 Phase 3 tests／server import；已整合。 |
| tools/migrate.ts、tools/provision_user.ts | PHASE3_ONLY | 正式 migration 與受控帳號初始化入口；已整合。 |
| render.yaml、.env.example、package.json | MIXED_SEPARABLE | 部署與依賴設定可從 Phase 2 workflow 分離；只整合必要設定。 |
| server.ts、src/server/auth.ts、src/server/databaseService.ts、src/App.tsx | MIXED_SEPARABLE | 同時含 Phase 2 與 Phase 3；採必要區塊整合，未帶入文件刪除。 |
| tests/auth_session_lifecycle.test.ts、database_runtime.test.ts、rls_policy.test.ts、production_*.test.ts、browser_acceptance.test.ts | PHASE3_ONLY | 原始目錄新增之可執行驗收證據；已整合。 |
| docs/PHASE2_* | ALREADY_IN_MAIN | 乾淨基準已有文件；不因原始工作樹刪除而刪除。 |
| node_modules、dist、.env、資料庫檔 | SENSITIVE | 不納入版本控制，未從來源複製。 |

不確定內容保留在原始工作樹，未覆蓋或清理。
