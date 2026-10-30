# Phase 3.2.1 Provisioning Security

## 目標與環境

基準 SHA `9f55ab8c47e4f8287b436986a2a3a7e036a2c219`。Provisioning 僅由受控 CLI 使用 `JUDICIAL3_PROVISIONING_DATABASE_URL`；密碼由 stdin 輸入，不接受命令列密碼。

## 修改與驗證

`tools/provision_user.ts` 在輸入驗證後才建立 runtime，以 `finally` 關閉 Pool，不呼叫同步 `process.exit`，錯誤會遮蔽 PostgreSQL URL。既有 SQL 身分檢查維持 `session_user=judicial3_provisioner_login`、`current_user=judicial3_provisioner`。執行 `npm test` 與 embedded PostgreSQL acceptance 驗證本機合約。

## 限制

Staging 真實 role、重複帳號、rollback 與連線清理證據為 `NOT_RUN`；需要獨立 Staging provisioning URL，且不得在一般對話傳遞。Production provisioning 未執行。
