# Phase 3.2.3 Browser Acceptance

## 目標與命令

基準 SHA `9f55ab8c47e4f8287b436986a2a3a7e036a2c219`。`npm run test:staging-browser` 對 HTTPS Staging 執行 health、匿名拒絕、錯誤密碼、登入、Cookie、reload、logout、console/network 與 axe 驗收，保存去識別化 screenshot 與 summary。

## 證據保護

帳密僅由 GitHub `staging` environment secrets 傳入；artifact 保留 14 天。summary 只含時間、commit、失敗數與錯誤數，不含 Secret 或 response body。

## 實際結果

Render browser acceptance：`NOT_RUN`。缺少 Staging HTTPS URL 與測試帳號。CI 的本機 browser test 只屬 repository gate。下一步是部署 Staging 後手動觸發 `staging-release`；Production 不執行。
