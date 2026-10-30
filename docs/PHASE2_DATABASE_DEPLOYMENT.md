# Phase 2 資料庫與部署前驗收

## 資料庫

| 項目 | 結果 | 證據／原因 |
|---|---|---|
| PGlite 建案、保存、重開、修訂、owner 隔離 | PASS | `tests/mvp_complete_flow.test.ts`、`tests/api_owner_isolation.test.ts` |
| 候選法條逐筆 round-trip | PASS | 同一 revision 保存 §320、§337，讀回 article_number 分別為 320、337。 |
| 真實 PostgreSQL 版本／隔離 DB | NOT_RUN | `psql` 與 Docker 不存在，未提供測試 DATABASE_URL。 |
| PostgreSQL application client | FAIL | runtime 僅匯入 `@electric-sql/pglite`，沒有 `DATABASE_URL` client path。 |
| migration ledger／升級 | FAIL | 初始化仍以 `cases` 表是否存在判斷 0001–0009，無 ledger/checksum；新庫會載入測試 seed。 |
| 真實 PostgreSQL RLS | BLOCKED | 應用層未以 transaction `SET LOCAL app.current_user_id`，亦無非 superuser app role 實測。 |
| 真實 PostgreSQL rollback／restart | NOT_RUN | 缺少隔離 PostgreSQL。PGlite 結果不可替代。 |

## Render／production

| 項目 | 結果 | 證據／原因 |
|---|---|---|
| `npm start` | PASS | 修正為 `tsx server.ts`；`tests/production_start.test.ts` 實際啟動 health 與 built UI。 |
| production build | PASS | Vite 1662 modules，exit 0；有既存 `__dirname` config warning。 |
| `render.yaml` | FAIL | repository 不存在部署 Blueprint。 |
| 必要 env 文件 | PASS（本機） | `.env.example` 去除重複 secret，新增 dev session、external AI 與 PGlite 說明。 |
| Render 實際環境 | NOT_RUN | 未提供 Render 唯讀權限；未部署、未修改環境變數。 |
| 持久化 | FAIL（部署設計） | PGlite 需要 persistent disk；目前無 Blueprint／disk／PostgreSQL 設計可驗證。 |

## 部署裁決

尚未具備部署審查條件。需先選定正式 PostgreSQL 或受控 persistent disk、完成正式 auth、migration ledger、production seed gate、Render 設定與 staging 驗收。
