# Phase 2 重建限制

- 原始 Phase 2 沒有獨立 commit；可還原來源是 main SHA 加上完整 JSONL patch 時序。這是操作級證據，但不是原生 Git commit。
- `package-lock.json` 的純 Phase 2 blob 無法從 reflog、stash、fsck 或 session 取得；目前 npm 解析也因 peer conflict 失敗，因此排除。`bun.lock` 已以 frozen install驗證。
- 本次沒有重新執行歷史上的 Codex 內建瀏覽器人工流程；只保留其原始報告，並重跑可重複的 CLI/API/PGlite/build/start 測試。
- 真實 PostgreSQL、RLS、Render、正式登入／登出／撤銷與外部法律檢索仍為 `NOT_RUN` 或 `BLOCKED`。
- Phase 2 HMAC/dev-session 僅證明本機 MVP 邊界，不等於 Phase 3 production auth。
- 法律推理測試通過只證明既定案例與程式行為，不構成個案法律結論或完整罪章覆蓋。
- 原始混合工作目錄、錯誤遠端分支與 Phase 3 未提交成果均保留，未 reset、clean、rebase、cherry-pick 或 force push。
