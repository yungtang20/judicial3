# Phase 3 缺陷與殘餘風險

## 已修復

- Windows HTTP harness 改用 Node 載入 tsx CLI，避免不存在的 tsx.exe。
- 測試 server 停用 HMR 時由 server.ts 明確傳入 hmr=false，避免固定 WebSocket port 競爭。
- npm test 改為 test-concurrency=1，避免多個隔離 server／PGlite 測試互相競爭。
- Phase 3 Python audit 支援 Windows npm.cmd 與 UTF-8 輸出。

## 未關閉

- 真實 PostgreSQL app role、RLS、migration concurrency：BLOCKED。
- Render staging、正式 HTTPS cookie、secret／backup／rollback 演練：BLOCKED。
- live external AI 與法律來源 retrieval：NOT_RUN／BLOCKED。
- 本機測試不能證明正式部署可用，也不能把候選法律路由當成已查證法律結論。
