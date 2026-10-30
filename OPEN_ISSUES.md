# 2026-10-29 尚未完成項目

- 第320／337條及第277／305／271條已進入 registry；詐欺及其他罪名仍保留既有案型入口，尚未完成全罪名 registry 遷移。
- `JUDICIAL3_SESSION_SECRET` 目前是 HMAC session token 的本機／測試基礎；尚未完成登入服務、token 輪替與正式 secret 管理。
- 尚未在真實 PostgreSQL/RLS 服務完成跨案件整合測試；本次未對既有 runtime DB 做破壞性操作。
- TWLawBot、LawBank 及部分第三方工具的內部能力無法由公開頁面逐項證明，已降級，不得當成法律正確性證據。
- 固定問句生成器仍需後續拆成候選／要件／區辨問句並加入答案驅動排程。
