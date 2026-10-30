# Phase 3.3 Monitoring

## 設計

基準 SHA `9f55ab8c47e4f8287b436986a2a3a7e036a2c219`。監測 Web health、DB/readiness、pool/query timeout、HTTP 4xx/5xx、login/provision/migration/backup/restore/deploy failure、CPU/memory/storage。分類 system/user/database/permission/external errors，log 禁止 password、token、session、API key 與完整 DB URL。

## 告警

Web down、DB unavailable、migration/provisioning/backup failure、backup overdue、storage threshold、pool exhausted、5xx/login failures spike 應透過 Render Notifications 或核准的安全通道通知。敏感內容只提供 resource ID、timestamp、status 與 correlation ID。

## 驗證狀態

Live notifications、metrics、failure injection 與恢復：`NOT_RUN`。Workspace 通知設定與方案不可見，且沒有 Staging。下一步建立 Staging 後依序模擬 health timeout、DB unavailable、migration/backup failure；禁止在 Production 注入故障。
