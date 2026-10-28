# Audit Reports 隔離區

本目錄只允許放置盤點、分析、稽核及規劃報告，不是正式問句或法律資料來源。

- Runtime 唯一問句入口：`data/runtime/question_bank.json`。
- 編譯器只接受 `question_sources/families.manifest.json` 白名單內的來源。
- `audit`、`review`、`evidence` 路徑會被編譯器拒絕。
- 本目錄不得放姓名、案號、摘要、回答、文件正文或真實案件 fixture。
- 報告不得自行把 `AI_REVIEWED` 升格為 `HUMAN_LEGAL_APPROVED`。
