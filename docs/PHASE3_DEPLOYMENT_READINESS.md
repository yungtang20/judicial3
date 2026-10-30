# Phase 3 部署準備度

render.yaml 已提供 Node web service、npm ci --legacy-peer-deps && npm run build、pre-deploy npm run db:migrate、/api/health/ready、PostgreSQL engine、secret references、關閉 auto deploy／test seed／dev session。未寫入實際 secret。

Production 缺 DATABASE_URL、非 PostgreSQL engine、非 HTTPS public origin、dev session 或 load seed 時 fail closed；readiness 會檢查 migration ledger。正式資料不依賴 Render ephemeral filesystem。

Blueprint 靜態檢查與本機 build PASS；Render 實際部署、staging migration、HTTPS cookie、備份／回復演練為 BLOCKED，本階段未觸發部署。
