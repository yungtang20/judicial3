# Phase 3 關鍵缺陷修復報告

## 修復

1. 新增 0013_system_roles.sql：正式角色字典 seed，無測試帳號、預設密碼或預設管理員；role_code 冪等。
2. user_roles 維持 RLS，只開放角色字典 SELECT，撤銷一般寫入；production role grants 以條件式 migration 保留 role separation。
3. provisioning 改用無 user context 的 atomic transaction，角色查詢與帳號建立同一交易，密碼仍使用 bcrypt。
4. getDatabaseHealth 強制 owner context，案件／revision 統計透過 withTransaction，移除一般使用者不必要的 schema integrity 詳細資訊。
5. migration wrapper 改為 lexer-based parser，支援前置註解、DO block、字串與 dollar quote，只移除最外層 BEGIN／COMMIT。
6. Python audit 改用明確 PASS／FAIL／NOT_RUN／BLOCKED 統計；存在環境缺口時回傳 exit 2。

## 狀態

本機程式與 PGlite 回歸已通過。真實 PostgreSQL transaction atomicity、role grants、RLS 與 Render 仍為 BLOCKED，未宣稱正式環境 PASS。
