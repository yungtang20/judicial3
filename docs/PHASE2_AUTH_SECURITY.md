# Phase 2 認證與授權驗收

## 實際流程

正式登入供應商尚不存在。開發模式在 `JUDICIAL3_ALLOW_DEV_SESSION=true`、非 production 且 loopback 時，後端簽發 HMAC token；受保護 API 由 `requireApiUser` 驗章與期限，owner 只取自 token `sub`，不相信 request body。

| 方法／路徑 | 認證 | owner 檢查 | 實測狀態 |
|---|---|---|---|
| `POST /api/auth/dev-session` | 本機條件閘門 | N/A | production 404；本機明確開關 PASS |
| `POST /api/chat` | Bearer token | N/A | 未登入 401；有效 token 且 AI 關閉 503 PASS |
| `GET /api/database/status` | Bearer token | N/A | middleware 路徑存在；獨立 route 未逐一 HTTP 重跑，NOT_RUN |
| `GET /api/cases` | Bearer token | `lead_investigator_id` | A 可見自己的案件；B 不可見 A，PASS |
| `GET /api/cases/:id` | Bearer token | case id + owner | A=200、B=404、未登入=401，PASS |
| `POST /api/cases/save` | Bearer token | owner 取自 token | caller 偽造 `ownerId=B` 仍保存為 A；無效 nested payload=400，PASS |

## A01–A05

- A01 Token 驗證：PASS。未提供、缺 subject、過期、錯誤簽章、格式錯誤均遭 401；`x-user-id` 不被信任。
- A01 正式登入：FAIL。沒有帳號密碼／SSO/OIDC 登入入口；production browser 無法取得正式 session。
- A02 登出與 revoke：FAIL。沒有伺服器端 session store、撤銷、rotation、停權或 security stamp。
- A03 dev-session：PASS。production 實際 route 404；未明確開關或非 loopback 亦拒絕。
- A04 owner 隔離：PASS（list/read/save）。修改／刪除 API 尚不存在，無法驗收相應路由。
- A05 結論：本機 API 身分與 owner 邊界可驗證；正式認證不可上線。

## 剩餘風險

Token 儲存在 `localStorage`，若發生 XSS 可能遭竊；沒有 CSP、revoke、登入稽核、rate limit 或正式 secret rotation。這些是部署阻擋條件，不得以 HMAC middleware PASS 取代。
