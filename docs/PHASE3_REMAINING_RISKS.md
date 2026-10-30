# Phase 3 Remaining Risks and External Environment Requirements

## 目前風險

基準 SHA `9f55ab8c47e4f8287b436986a2a3a7e036a2c219`。未建立 Staging 代表角色、RLS、session、browser、backup/restore、rollback 與 monitoring 均無 live evidence。免費 PostgreSQL 的期限與復原限制不符合長期 DR。依 2026-10-30 官方價格，兩個最小 private runner 約 USD 14/月，最小付費 PostgreSQL 約 USD 6/月另加儲存，因此最低持續成本約 USD 20/月起；異地儲存與 restore DB 另計。Production 狀態不可由 repository 推論。

## 集中外部需求清單

| 項目 | 用途／最低權限 | 取得位置 | 安全傳遞 |
|---|---|---|---|
| Render Workspace plan/usage/billing read access | 確認免費額度與持續費用 | Render Dashboard | 由管理員查看後記錄非敏感摘要 |
| Staging resource 費用核准 | DB、private migrator、private acceptance runner、restore DB | 組織核准流程 | 僅核准資源名稱、方案、上限，不貼付款資料 |
| Render API token | 僅管理 judicial3 Staging service/deploy/job | Render Account Settings | GitHub `staging` environment secret `RENDER_API_KEY` |
| Staging DB bootstrap/migration/provisioning URLs | 建立分離角色並執行 acceptance | Render DB access | 本機 credential store 或 GitHub environment secrets，不貼對話 |
| Staging test users | Login/session/RLS browser tests | 受控 admin CLI | GitHub secrets `JUDICIAL3_STAGING_TEST_USERNAME/PASSWORD` |
| age recipient/private key | Backup encryption/restore | 管理員 key store | public recipient 可設定；private key 僅 secret store |
| Object storage credentials/retention policy | 異地 encrypted backup | 核准的 R2/S3 provider | 專用最小權限 secret，禁止 Git/聊天 |
| Notification destination | Staging alerts | Render Notifications/核准通道 | 僅 resource/status，不傳 Secret/個資 |

## 下一步與安全邊界

先確認方案與月費，再建立獨立 Staging；建立後依 migration → deploy → browser/live DB → backup/restore → rollback/alerts 順序執行。所有 Production migration、data mutation、credential rotation、restore 與 deploy 仍需另一個明確授權，不能以本文件替代。
