# JUDICIAL3 MVP 實作報告

日期：2026-10-29。

## 本次修正

1. 新增 `0010_mvp_traceability.sql`，讓既有 PGlite store 也能以 idempotent migration 補上 `raw_text`、Evidence 狀態／來源／Fact refs、構成要件 refs 及問句 metadata。
2. `databaseService.ts` 保存並重新讀取原始案情；保存 Evidence、Candidate Elements、Question traceability；revision 仍以交易方式建立。
3. PGlite 路徑支援 `JUDICIAL3_DATABASE_PATH`，供隔離的完整流程測試使用；初始化失敗不切換記憶體庫。
4. `server.ts` 將 `/api/chat` 納入認證，新增僅非 production 可用的本機 dev session bridge，讓沒有正式登入服務的本機 MVP 能取得受保護 API session。
5. `App.tsx` 自動取得本機 dev session 並將 Authorization token 帶入案件 API；production 不開放 dev session。
6. 新增 `tests/mvp_complete_flow.test.ts`，實際使用臨時 PGlite 驗證建案、保存、重新讀取、第二 revision、Fact／Evidence／問句追溯及跨 owner 隔離。
7. 新增 `tests/api_route_auth.test.ts`，實際啟動 `server.ts` 驗證受保護 route 拒絕未登入請求、接受驗證 token。

## 架構裁決

- 保留現有模組化單體及 PGlite，不重寫前端或資料庫。
- migration 使用 `ADD COLUMN IF NOT EXISTS`，避免為測試刪除或重建使用者資料。
- 本機 dev session 只為本地 MVP 操作便利，正式環境必須由正式登入服務提供 token；不得將 dev session 宣稱為 production authentication。
- 法律候選 registry 仍採有限範圍，不擴充全部罪章。

## 尚存問題

- 問句的新增／刪除／人工確認 UI 尚未形成完整獨立編輯器。
- 正式登入、token rotation、真實 PostgreSQL/RLS 整合尚未完成。
- TaiLexi 及 LawBank 部分來源本次無法完整讀取。
- 舊案型候選仍有部分尚未遷移至 registry。
