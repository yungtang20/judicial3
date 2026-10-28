# 檔案分類清單（2026-10-28）

> 本文件是 `AUDIT_REPORT`。`runtime_dependency` 的 `DIRECT` 表示正式執行直接載入，`BUILD_TIME` 表示只在編譯／匯入時使用，`NONE` 表示正式流程不使用。

## 應用程式與入口

| file_path | file_type | file_category | current_purpose | runtime_dependency | modification_allowed | evidence | notes |
|---|---|---|---|---|---|---|---|
| `app/__init__.py` | Python | SOURCE | package marker | DIRECT | YES | Python import path | 無案件資料 |
| `app/documents.py` | Python | SOURCE | DOCX、條陳、頁數驗證 | DIRECT | YES | server import | LibreOffice 本機 renderer |
| `app/domain.py` | Python | SOURCE | Gate、候選、revision payload 規則 | DIRECT | YES | workflow/server import | 法律結論不得由此自動認定 |
| `app/legal_query.py` | Python | SOURCE | 外部查詢去識別守門 | DIRECT | YES | server import | 外部傳送預設停用 |
| `app/question_bank.py` | Python | SOURCE | runtime JSON 白名單 loader | DIRECT | YES | domain/server import | 拒絕 audit/report |
| `app/server.py` | Python | SOURCE | 本機 HTTP API | DIRECT | YES | `python -m app.server` | loopback only |
| `app/storage.py` | Python | SOURCE | SQLite revision 與獨立 audit | DIRECT | YES | server import | audit 不保存案件正文 |
| `app/workflow.py` | Python | SOURCE | action dispatch 與來源漂移阻擋 | DIRECT | YES | server import | fail closed |
| `app/static/app.js` | JavaScript | SOURCE | Web UI 行為 | DIRECT | YES | `index.html` script | 本機 API only |
| `app/static/index.html` | HTML | SOURCE | Web UI 結構 | DIRECT | YES | server static route | 無內嵌案件資料 |
| `app/static/styles.css` | CSS | SOURCE | Web UI 樣式 | DIRECT | YES | HTML stylesheet | 375px 已驗收 |
| `start.ps1` | PowerShell | CONFIG | 本機啟動 | NONE | YES | 操作入口 | 不部署 |
| `requirements.txt` | text | CONFIG | Python 相依版本 | BUILD_TIME | YES | pip install input | 無 runtime 資料 |

## 正式問句、法律結構與模板來源

| file_path | file_type | file_category | current_purpose | runtime_dependency | modification_allowed | evidence | notes |
|---|---|---|---|---|---|---|---|
| `question_sources/families.manifest.json` | JSON | CONFIG | 問句來源白名單 | BUILD_TIME | YES | compiler input | 不掃描目錄 |
| `question_sources/procedure/common.md` | Markdown | SOURCE | 通用程序問句 | BUILD_TIME | YES | manifest/compiler | `HUMAN_REVIEW_REQUIRED` |
| `question_sources/procedure/modules.md` | Markdown | SOURCE | 條件式程序模組 | BUILD_TIME | YES | manifest/compiler | 依前置條件啟用 |
| `question_sources/families/01_人身暴力與生命身體.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 人工可讀主檔 |
| `question_sources/families/02_意思壓制自由與恐嚇.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 人工可讀主檔 |
| `question_sources/families/03_財物持有取走與侵占.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 人工可讀主檔 |
| `question_sources/families/04_財物毀損.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 人工可讀主檔 |
| `question_sources/families/05_欺罔財產處分與背信.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 人工可讀主檔 |
| `question_sources/families/06_文書印文與身分冒用.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 人工可讀主檔 |
| `question_sources/families/07_名譽與公開言論.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 人工可讀主檔 |
| `question_sources/families/08_隱私秘密與性影像.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 人工可讀主檔 |
| `question_sources/families/09_公共危險與交通.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 人工可讀主檔 |
| `question_sources/families/10_毒品槍砲與組織.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 槍砲／組織 route 仍阻擋 |
| `question_sources/families/11_妨害司法公務與秩序.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 人工可讀主檔 |
| `question_sources/families/12_電腦網路與數位證據.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 人工可讀主檔 |
| `question_sources/families/13_性自主兒少與性剝削.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 特別程序需疊加 |
| `question_sources/families/14_金流洗錢與贓物.md` | Markdown | SOURCE | 家族問句 | BUILD_TIME | YES | manifest/compiler | 洗錢／贓物 route 仍阻擋 |
| `question_sources/families/15_特殊專責路線.md` | Markdown | SOURCE | 專責路線導覽問句 | BUILD_TIME | YES | manifest/compiler | 不把異質罪章硬併同骨架 |
| `legal_sources/routes.snapshot.json` | JSON | SOURCE | 44／310 route 結構快照 | BUILD_TIME | YES | compiler/import input | 法律審查未完成 |
| `legal_sources/routes.snapshot.lock.json` | JSON | CONFIG | route 快照 hash lock | BUILD_TIME | YES | importer/compiler validation | 漂移即失敗 |
| `legal_sources/extension_routes.json` | JSON | SOURCE | 4 條擴充 route 阻擋資料 | BUILD_TIME | YES | compiler input | 不得算入 310 child |
| `legal_sources/law_versions.json` | JSON | SOURCE | 10 部法規官方版本釘選 | BUILD_TIME | YES | official query + compiler input | 無案件內容；條文內容仍待逐條核對 |
| `legal_sources/article_verifications.json` | JSON | SOURCE | 310 child route 現行條號存在性證據 | BUILD_TIME | YES | official query + snapshot hash | 不代表要件或行為時法正確 |
| `legal_sources/route_corrections.json` | JSON | SOURCE | 官方條文比對校正 overlay | BUILD_TIME | YES | compiler validates route/law/article | 不覆寫 imported snapshot |
| `legal_sources/constitutional_route_verifications.json` | JSON | SOURCE | 憲法判決造成的 route 限縮與排除證據 | BUILD_TIME | YES | compiler validates fact fragments/excluded status | 第140條限縮、第141條之1失效 |
| `data/templates/victim.docx` | DOCX | SOURCE | 被害人公司模板 | DIRECT | YES | document builder | hash 鎖定 |
| `data/templates/suspect.docx` | DOCX | SOURCE | 涉嫌人公司模板 | DIRECT | YES | document builder | hash 鎖定 |
| `data/templates/transfer.docx` | DOCX | SOURCE | 移送公司模板 | DIRECT | YES | document builder | hash 鎖定 |
| `data/templates/manifest.json` | JSON | CONFIG | 模板 hash 與版本 | DIRECT | YES | QuestionBank/template loader | 漂移需 rebase |
| `data/templates/questions.json` | JSON | SOURCE | 模板語義題與 binding | DIRECT | YES | question scheduler | 由匯入器產生 |

## 編譯產物、工具、測試與文件

| file_path | file_type | file_category | current_purpose | runtime_dependency | modification_allowed | evidence | notes |
|---|---|---|---|---|---|---|---|
| `data/runtime/question_bank.json` | JSON | SOURCE | 正式 runtime 問句庫 | DIRECT | GENERATED_ONLY | QuestionBank allowlist | 不手改，須由 compiler 產生 |
| `data/runtime/route_coverage.json` | JSON | SOURCE | route 覆蓋證據 | DIRECT | GENERATED_ONLY | QuestionBank allowlist | deterministic build |
| `data/runtime/source_manifest.json` | JSON | CONFIG | runtime 來源 fingerprint | DIRECT | GENERATED_ONLY | QuestionBank allowlist | basis pin |
| `tools/compile_questions.py` | Python | SOURCE | MD → immutable JSON 編譯 | BUILD_TIME | YES | README command | 拒絕 audit 路徑 |
| `tools/import_company_templates.py` | Python | SOURCE | 公司模板匯入與拆題 | BUILD_TIME | YES | template build | round-trip gate |
| `tools/import_route_snapshot.py` | Python | SOURCE | route 快照匯入與 lock | BUILD_TIME | YES | legal source build | 不作法律推論 |
| `tools/seed_question_sources.py` | Python | SOURCE | 建立／擴充問句來源 | BUILD_TIME | YES | source maintenance | 不由 runtime 呼叫 |
| `tests/test_documents.py` | Python | TEST | 文件與八頁測試 | TEST_ONLY | YES | pytest discovery | 虛構資料 |
| `tests/test_question_bank.py` | Python | TEST | 題庫、310／930 覆蓋與隔離 | TEST_ONLY | YES | pytest discovery | 不作法律核准 |
| `tests/test_revision_and_gate.py` | Python | TEST | Gate、revision、route、失效測試 | TEST_ONLY | YES | pytest discovery | 虛構資料 |
| `tests/test_security_and_schema.py` | Python | TEST | audit schema 與外部查詢邊界 | TEST_ONLY | YES | pytest discovery | 無真實案件 |
| `README.md` | Markdown | SOURCE | 操作及安全邊界文件 | NONE | YES | 人工閱讀 | 非 runtime 資料 |
| `docs/PROJECT_TODO.md` | Markdown | AUDIT_REPORT | 實作進度與 Human Gate | NONE | YES | 人工閱讀 | 不得編譯 |
| `docs/audit/README.md` | Markdown | AUDIT_REPORT | 報告隔離規則 | NONE | YES | audit 目錄 | 不得編譯 |
| `docs/audit/IMPLEMENTATION_STATUS.md` | Markdown | AUDIT_REPORT | 實作狀態稽核 | NONE | YES | audit 目錄 | 不得編譯 |
| `docs/audit/FILE_CLASSIFICATION.md` | Markdown | AUDIT_REPORT | 本檔案分類清單 | NONE | YES | audit 目錄 | 不得編譯 |
| `docs/audit/LAW_VERSION_AUDIT.md` | Markdown | AUDIT_REPORT | 官方現行法版本定位稽核 | NONE | YES | audit 目錄 | 不得編譯 |
| `docs/audit/REQUIREMENT_AUDIT.md` | Markdown | AUDIT_REPORT | 整合計畫逐條驗收 | NONE | YES | audit 目錄 | 不得編譯 |
| `docs/audit/HIGH_FREQUENCY_ROUTE_AUDIT.md` | Markdown | AUDIT_REPORT | 第一批高頻 route 內容稽核 | NONE | YES | audit 目錄 | 不得編譯 |
| `docs/audit/SECOND_BATCH_ROUTE_AUDIT.md` | Markdown | AUDIT_REPORT | 第二批 route 內容稽核 | NONE | YES | audit 目錄 | 不得編譯 |
| `docs/audit/THIRD_BATCH_ROUTE_AUDIT.md` | Markdown | AUDIT_REPORT | 第三批 route 內容稽核 | NONE | YES | audit 目錄 | 不得編譯 |
| `docs/audit/FOURTH_BATCH_ROUTE_AUDIT.md` | Markdown | AUDIT_REPORT | 第四批 route 內容與憲法效力稽核 | NONE | YES | audit 目錄 | 不得編譯 |
| `docs/audit/ELEMENT_GAP_QUESTION_AUDIT.md` | Markdown | AUDIT_REPORT | 具體要件與三角色問句直接對應稽核 | NONE | YES | audit 目錄 | 不得編譯 |

## 保護與隔離結果

- 舊專案 `D:/工作用/judicial1/legal-case-web`：本次未修改、未刪除、未移動、未重新命名；但該工作樹原本已有大量未提交變更，不能把整體狀態宣稱為乾淨。
- 新專案：依使用者實作授權新增及修改；不是 Phase 0 唯讀盤點。
- 報告：只放在 `docs/audit/` 或 `docs/PROJECT_TODO.md`，正式 loader 不讀取。
- 未確認：原始公司 `.doc` 到目前 `.docx` 轉換前的機關內部製作流程與證人具結內規仍為 `UNKNOWN`。
