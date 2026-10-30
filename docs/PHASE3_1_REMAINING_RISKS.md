# Phase 3.1 Remaining Risks

- `BLOCKED`：尚未提供隔離 PostgreSQL 的 migration、app、provisioner 三組連線，因此正式 role grant、RLS、pool context、rollback 與並行 migration 未完成實測。
- `BLOCKED`：Render staging、HTTPS cookie、部署前 migration 與正式備份／回復尚未執行。
- 角色建立與密碼管理仍屬部署平台 bootstrap 責任；repository 不保存正式帳密，也不由 migration 建立 login role。
- 未完成上述驗收前，結論只能是 `PARTIAL_PASS`，不可宣稱正式部署 ready。
