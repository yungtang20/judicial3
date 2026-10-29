# 新 AI 接手操作手冊（AI_HANDOVER.md）

## 1. 專案身分與紅線
- 本專案為獨立全新之臺灣刑事案件偵查輔助系統。
- 專案不可自動認定犯罪成立，必須維持人工審核機制。
- 外部 AI 預設停用，嚴禁未授權傳送案情資料。
- 第一階段不採用 MFA，採用單一核准公務員登入模型。
- 目前暫停雲端部署操作，未獲使用者授權前禁止向 Render 或 Supabase 執行正式建立。

## 2. 核心檔案導引
- 前端進入點：`src/App.tsx`, `src/types/index.ts`
- 業務邏輯與驗證：`src/services/analyzer.ts`, `src/services/storage.ts`
- 稽核檢核腳本：`scripts/audit_predeploy.py`, `src/services/auditPredeploy.ts`
- 規格庫：`docs/`
