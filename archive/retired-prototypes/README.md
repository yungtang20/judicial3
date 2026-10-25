# 已淘汰原型

封存日期：2026-10-25

## web_app

- 原路徑：`legal-case-web/web_app/`
- 類型：Next.js 原型
- 狀態：已淘汰，非正式 runtime
- 原始碼：16 個 Git 追蹤檔
- HEAD tree：`a7b112244c3aed3c33eb450861678cbb57b30f88`
- 排除內容：`.env.local`、`node_modules/`、`.next/`

## app_prototype

- 原路徑：`legal-case-web/app_prototype/`
- 類型：Streamlit 原型
- 狀態：已淘汰，非正式 runtime
- 原始碼：2 個 Git 追蹤檔
- HEAD tree：`34ca140a0ce34225872ed85b22a11e9cf363baca`
- 排除內容：`.env`
- 已知限制：歷史預設路徑 `../review/` 在封存位置不再成立。本原型僅供追溯，不列入正式驗證。

## 邊界

- 正式流程為 `legal-case-web/app/server.py` → `app/workflow.py` → `rules/questions` → `documents/storage`。
- `reasoning-flow/` 是另一套獨立研究工作台，本次未封存。
- 原始本機秘密留在原路徑並由根 `.gitignore` 精確排除，未讀取、未複製、未加入 Git。
