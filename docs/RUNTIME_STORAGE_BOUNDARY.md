# Runtime 資料保存邊界（P0 文件對齊）

> 本文件對齊 `legal-case-web/app/storage.py`、`SYSTEM_ARCHITECTURE.md` 與根 README 的實際行為。
> **不得**為了讓文件「看起來一致」而暗示未實作的持久化能力。

## 三種 Store

| 類別 | 檔案 | 行為 | 典型啟用 |
|------|------|------|----------|
| `EphemeralCaseStore` | `app/storage.py` | **程序記憶體**；單一案件；重啟／重新部署即失 | 本機 loopback 預設、部分 Render 記憶體模式 |
| `CaseStore` | `app/storage.py` | SQLite + `protect_json` 加密 payload | 相容／本機路徑設定時；**不保證**為目前 HTTP 預設 |
| `SupabaseCaseStore` | `app/storage.py` | PostgREST；`encrypted_payload`；owner RLS；軟刪 `deleted_at` | Render + Supabase 正式單人部署 |

## 與 README 的關係

- README 提到 Render + Supabase、AES／Fernet、RLS：**在 Supabase 部署路徑上成立**。
- `SYSTEM_ARCHITECTURE.md` 寫 Ephemeral 為實際 runtime、重啟遺失：**在本機預設與未接 Supabase 的程序上成立**。
- 兩者並非互斥，而是 **部署模式不同**：
  - 本機開發：多為 ephemeral。
  - 雲端單人：可為 Supabase 加密持久化。
- 任何文件若寫「案件一定永久保存」，在 ephemeral 模式下為**錯誤**。

## 安全檢查清單（人工／CI）

1. 目前 `server.py` 實際注入的是哪一個 store？
2. 案件正文是否經 `protect_json`／Supabase `encrypted_payload`？
3. 金鑰是否僅在伺服器環境、未進前端與 git？
4. MFA／單一 owner／RLS 是否在雲端路徑啟用？
5. 重啟後資料是否仍在？（預期：ephemeral 否；Supabase 是）
6. 日誌是否排除案情自由文字與姓名？

## 變更原則

- 改變預設 store 必須同步改本文件、README、SYSTEM_ARCHITECTURE，並加測試。
- 測試綠燈不代表個資或法律合規驗收完成。
