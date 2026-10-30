# Phase 3.2 PostgreSQL 驗收報告

## 判定：PARTIAL_PASS / BLOCKED

- **PASS（靜態）**：Application、Migration、Provisioning 三組 env 名稱在設定與程式流程中分離。
- **PASS（靜態）**：Provisioning CLI 僅接受 `JUDICIAL3_PROVISIONING_DATABASE_URL`，且 password 由 stdin 傳入。
- **PASS（靜態）**：migration ledger/checksum、0014 grant/revoke 與 RLS migration 存在。
- **BLOCKED**：尚無獨立 Render staging PostgreSQL，因此不能宣稱 live migration、role identity、provisioning、RLS、pool context 或 cleanup 通過。
- **PASS（local test design）**：缺少外部 URL 時會執行 embedded PostgreSQL disposable suite；該 suite 明確輸出 embedded test evidence，不冒稱 Render live。
- **NOT_RUN**：embedded PostgreSQL failure-case 後的 ledger inspection 在 Windows process reset 下不可靠，missing-role atomic rollback 保留給 staging PostgreSQL。
- **NOT_RUN**：Render staging PostgreSQL live suite 尚未執行。

## 禁止的替代

PGlite、單元測試與 repository 靜態檢查只能作為 local evidence，不能替代 Render staging PostgreSQL。任何外部 URL 若非明確 test/staging/sandbox/disposable 資料庫，驗收必須 BLOCKED。
