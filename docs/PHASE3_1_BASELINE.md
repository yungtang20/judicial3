# Phase 3.1 Baseline

- 基準：`da654fc51a0557f0f1b4c8e63a3ee01059cac83e`
- 原始工作目錄 `D:\工作用\judicial3` 保持既有未提交變更，本輪使用獨立 worktree。
- Phase 3 已具備 PGlite migration、RLS、owner-scoped health 與 transaction provisioning；真實 PostgreSQL role grants 尚未驗收。
- 本輪禁止連接正式資料庫；只接受名稱含 `test`、`staging`、`sandbox` 或 `disposable` 的隔離資料庫 URL。
