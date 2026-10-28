# 整合計畫逐條驗收（2026-10-28）

> 本文件是 `AUDIT_REPORT`，不是 runtime 輸入。`PASS` 只代表已列明的本機功能證據，不代表法律正確性已獲人工核准。

| 計畫區段 | 狀態 | 本機證據 | 尚存邊界 |
|---|---|---|---|
| 核心流程 | PASS | 事實先行、候選動態重算、相反事實、必要題排程 | 候選永遠不是法律結論 |
| 首頁與建案 | PASS | 8 格入口、三欄必填、案件類型、附件 | 附件不提供遠端同步 |
| Gate 1 | PASS | 人、事、時、地、物、行為、主觀、結果、因果、權利、證據及來源狀態 | AI 抽取仍須使用者確認 |
| Gate 2 | PASS（功能） | 1–5 題批次、家族骨架、核心、補強、區辨、證據、回答修正；child route 依案情排序且相關 route 要件未答完不得完成 | 問句法律內容仍 `HUMAN_REVIEW_REQUIRED` |
| 候選卡 | PASS | 支持／相反／缺口、child route、法名條號、官方法規版本、查核日及憲法限縮狀態 | 行為時法未自動判斷 |
| Gate 2.5 | PASS | 證明單、婦幼代號、詐欺 165 條件欄位 | 實際案號由使用者補登 |
| Gate 3 | PASS（本機） | 被害人模板、DOCX、條陳、複製、下載、下一步 | 最終條陳版面暫緩 |
| Gate 4 | PASS（本機） | 涉嫌人角色隔離、爭議事實、辯解／有利事實問句 | 不把被害人說法升格為事實 |
| Gate 5 | PASS（本機） | 使用者強制指定初始 route、移送模板、無被害人條陳 | 4 條 extension fail closed |
| 問句主檔 | PASS（結構） | 15 家族 MD、2 程序 MD、schema、manifest、immutable JSON；1,025 個 route-element／三角色 3,075 個直接補強題對應 | 法律人工審查及一般人語句逐題潤飾未完成 |
| revision／CAS | PASS | immutable revision、expected revision、command idempotency、basis digest | 未建多人 DB；本機 SQLite only |
| Gate 失效 | PASS | intake、事實、回答、route、source pack 變動均清除下游狀態 | 無跨裝置協作 |
| 模板 round-trip | PASS | 三份模板 hash、語義項目、原子題 binding | 原始機關 `.doc` 製作流程未取得 |
| 八頁限制 | PASS | LibreOffice 實際轉 PDF 計頁，必要內容超限 fail closed | renderer 不可用時禁止宣稱通過 |
| 條陳規則 | PASS | 500 Unicode 字元、民國年、超限拒絕 | 最終格式由使用者日後決定 |
| 法律來源 | PARTIAL | 10 部法規版本定位；310 child route 現行條號無 missing，現行條文摘要已完成第一輪比對並校正 29 項；第140、141-1條另核對憲法效力 | 行為時歷史法、其餘實務判決、機關內規及人工法律核准未完成 |
| UI 行為 | PASS | 一題聚焦、返回修正、失效警告、TODO、375px | 可再做使用者實地可用性測試 |
| Audit 隔離 | PASS | 獨立 DB、無案件正文欄位、UI 只顯示 hash metadata | command id 由 server 限 UUID |
| Phase 6 多人部署 | SKIPPED_WITH_REASON | 未取得部署、登入、保留年限授權 | 不屬目前本機授權 |

## 結論

- 本機產品流程：`PASS`。
- 問句資料庫結構與 runtime：`PASS`。
- 法律內容完備性：`PARTIAL / HUMAN_REVIEW_REQUIRED`。
- 外部部署：`NOT_AUTHORIZED`。
- 整體不得標示為 `HUMAN_LEGAL_APPROVED` 或 `DUAL_MODEL_PASS`。
