# Phase 3.2.3 Security Acceptance

## 安全條件

基準 SHA `9f55ab8c47e4f8287b436986a2a3a7e036a2c219`。必驗項目：三種 DB role 分離、Web 無 privileged secrets、RLS、session/CSRF/origin、停用帳號、未授權 API、Cookie attributes、無 dev session/legacy bearer/開放註冊、log 不洩密。

## 本機證據

`npm test`、`npm run lint`、`npm run test:postgres-embedded`、`python tools/secret_scan.py` 驗證程式合約；Production config 對 privileged env fail closed。這些不是 Render Live 證據。

## 狀態

Repository security regression 為 `PASS`：lint、18 個 application/browser tests、build、embedded PostgreSQL、Python DR tests、secret scan 與 production dependency audit 均通過。Render security acceptance 為 `NOT_RUN`。需要 Staging URL、兩個測試使用者、停用帳號及三組 Staging-only DB credentials。Production 未觸碰。
