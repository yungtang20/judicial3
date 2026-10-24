# Supabase 單一所有人部署

本模式只允許一個經機關核准的使用者。案件正文先由 Render 應用程式加密，再寫入 Supabase。瀏覽器不保存 Supabase access token、refresh token、publishable key 或加密金鑰。

## 1. Supabase Auth

1. 在 Supabase Dashboard 建立唯一使用者並完成電子郵件確認。
2. 記錄該使用者 UUID，作為 `SUPABASE_OWNER_USER_ID`。
3. 關閉公開註冊及匿名登入。
4. 在方案支援時啟用 Leaked Password Protection。
5. 保持 TOTP MFA enrollment 與 verification 啟用。
6. 不建立第二個應用程式使用者。

## 2. 資料表與 RLS

1. 開啟 `deploy/supabase_single_owner.sql`。
2. 將全部 `OWNER_USER_UUID_HERE` 替換為唯一使用者 UUID。
3. 確認沒有剩餘 placeholder。
4. 在 Supabase SQL Editor 執行整份交易。
5. 在 Data API 設定關閉自動公開新資料表。
6. 確認 `anon` 無權限，`authenticated` 仍須同時通過固定 UUID、`owner_id` 與 `aal2` RLS。
7. 確認 `cases_require_mfa` 是 `RESTRICTIVE` policy，避免日後新增 permissive policy 時繞過 MFA。

不得移除 `FORCE ROW LEVEL SECURITY`、固定 owner UUID 或 MFA 條件。

## 3. Render Secrets

在既有 `legal-case-workbench` 設定下列值，不得寫入 Git、文件、log 或瀏覽器：

| Key | Value |
|---|---|
| `SUPABASE_URL` | Supabase Project URL（HTTPS） |
| `SUPABASE_PUBLISHABLE_KEY` | Publishable key；不要使用 `service_role` 或 secret key |
| `SUPABASE_OWNER_USER_ID` | 唯一核准使用者 UUID |
| `JUDICIAL_ENCRYPTION_KEY` | 固定 Fernet key；遺失後既有案件無法解密 |

`render.yaml` 另固定：

- `AUTH_REQUIRED=true`
- `AUTH_PROVIDER=supabase`
- `CASE_STORAGE_PROVIDER=supabase`
- `ALLOW_EXTERNAL_AI=false`

產生 Fernet key 時只能在可信任環境執行，將結果直接貼入 Render Secret，不要貼入聊天、程式碼或命令紀錄：

```powershell
py -3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 4. 驗收

1. 非指定帳號登入必須失敗。
2. 正確密碼但未完成 MFA 時，不得進入工作台或案件 API。
3. 完成 MFA 後建立案件，案件清單只顯示 UUID、狀態與更新時間。
4. 重新部署 Render，重新登入後案件仍可開啟。
5. Supabase `encrypted_payload` 必須是密文，不得出現姓名或案情明文。
6. 以 `anon` key 直接查詢 `cases` 必須得到拒絕或空結果。
7. 以非 owner 的 `aal2` 使用者查詢仍必須得到拒絕或空結果。
8. Render log 不得出現電子郵件、姓名、案號、案情、JWT 或密鑰。

## 5. 邊界

- 下載的 DOCX 是明文，由使用者依機關規定保存。
- 真實案件模式禁止外部 AI；法律查詢只能使用不含可識別資訊的抽象法律問題。
- Render 與 Supabase 是經授權的資料處理邊界。若機關授權條件改變，應先停止雲端寫入。
- 本文件不授權建立其他使用者、分享案件或開啟協作功能。
