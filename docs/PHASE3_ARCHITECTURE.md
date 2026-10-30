# Phase 3 正式架構

server.ts 是唯一正式 HTTP runtime。production 啟動先執行 production config gate，再使用 PostgreSQL runtime；production 不允許退回 PGlite。PGlite 僅供本機／測試模式。

瀏覽器 same-origin cookie session → Express auth／CSRF middleware → owner-scoped service → withTransaction → PostgreSQL pool 或測試用 PGlite → migration ledger、RLS 與 revision traceability。

外部 AI 預設關閉；法律檢索未接入時維持 NOT_IMPLEMENTED／UNKNOWN，不把模型輸出當成已查證法源。
