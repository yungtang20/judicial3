# Phase 3 認證設計

正式環境採 bcrypt 密碼雜湊、opaque server-side session、SHA-256 session／CSRF token hash、HttpOnly SameSite=Strict cookie；production cookie 使用 __Host-judicial3_session 與 Secure。

所有 mutation route 需 CSRF token；production login 驗證 exact Origin。legacy HMAC bearer 僅限非 production、明確開關與 loopback。

tools/provision_user.ts 從 stdin 讀密碼，不接受命令列密碼，也不內建預設帳密。真實 HTTPS、正式 DB role 權限與 Render 驗證仍是 BLOCKED。
