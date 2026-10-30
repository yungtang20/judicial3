# Phase 3.1 Remaining Risks

- `PASS（disposable）`：embedded PostgreSQL 16.13 已完成 migration rollback／ledger、role grant、RLS、pool context 與 provisioning 驗收；外部 staging 仍需使用三組隔離 URL 重跑。
- `BLOCKED`：Render staging、HTTPS cookie、部署前 migration 與正式備份／回復尚未執行。
- `BLOCKED`：Render staging、正式資料庫的角色 bootstrap、備份／回復與部署前 migration 尚未執行。
- 角色建立與密碼管理仍屬部署平台 bootstrap 責任；repository 不保存正式帳密，也不由 migration 建立 login role。
- 未完成上述驗收前，結論只能是 `PARTIAL_PASS`，不可宣稱正式部署 ready。
