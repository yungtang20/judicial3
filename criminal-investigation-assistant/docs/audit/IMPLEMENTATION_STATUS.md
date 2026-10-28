# 本機整合實作狀態（2026-10-28）

> 本文件是 `AUDIT_REPORT`，不是問句、法條或 runtime 資料來源。

## 執行邊界

- execution mode：`SINGLE_EXECUTOR`
- runtime model identity：`UNVERIFIED`
- 部署：未授權、未執行
- 外部 AI：關閉
- 真實案件資料：未匯入、未外傳
- 法律核准：所有題目與 route 維持 `HUMAN_REVIEW_REQUIRED`；`AI_REVIEWED` 不等於人工法律核准。

## 已有可執行成果

| 項目 | 狀態 | 證據 |
|---|---|---|
| 問句主檔 | PASS | 15 個家族 MD、2 個程序 MD，經 manifest 白名單編譯 |
| route 結構 | PASS（結構） | 44 parent／310 snapshot child hash 鎖定；第141條之1依憲法判決維持排除 |
| route 法律完備 | HUMAN_REVIEW_REQUIRED | 310 個 snapshot route 已完成現行條號及條文摘要第一輪比對；第140條、第141條之1另核對憲法效力，行為時法、其他判決與內規仍待審查 |
| Gate 1 | PASS | 可追溯 intake 原文、修正推論／未知事實、修改即建立 revision |
| Gate 2 | PASS（本機功能） | 每批 1–5 題、child route 案情相關性排序、相關 route 必要題完成檢查、候選升降、要件缺口與相反事實 |
| 逐要件問句對應 | PASS（結構／執行） | 1,025 個 route-element、三角色 3,075 個直接 key mapping；回答只更新實際涵蓋缺口 |
| Gate 5 指定路線 | PASS | 無被害人案件強制指定 44 支援或 4 阻擋路線；指定不等於認定 |
| 固定模板 | PASS（語義匯入） | 三份公司 DOCX hash、原順序與原子題 binding |
| 文件 | PASS（本機） | DOCX、LibreOffice 實際頁數、八頁 fail closed、500 字及民國年 |
| 附件 | PASS（metadata） | 單檔 5 MB、Base64 驗證、content-addressed `.bin`、revision 僅存 metadata |
| 稽核 | PASS | 獨立 audit DB 與 UI；只含 command、digest、結果、時間 |
| 官方法規版本 | PASS（現行法定位） | 只以 10 個法規名稱查詢官方資料；保存 pcode、最新公布日、特殊施行日及來源 URL，未傳案件內容 |
| 外部案件查詢 | DISABLED | 去識別 locator 驗證器存在，但 runtime 不會送出案件或問答 |

## 2026-10-28 驗證

- `py -3 -X utf8 tools/compile_questions.py --check` → PASS
- `py -3 -X utf8 -m pytest -q` → `88 passed`
- `node --check app/static/app.js` → PASS
- `py -3 -X utf8 -m compileall -q app tools tests` → PASS
- 本機 HTTP：health、48 route options、選定 route、附件及 audit → PASS
- Codex 內建瀏覽器：首頁、稽核頁、Gate 1、Gate 2（辱罵員警先問第140條四項缺口且完成鍵保持鎖定）、Gate 5、回答修正、15 家族、375px 無橫向溢位、console 無錯誤 → PASS

## 未完成／Human Gate

1. 310 個 snapshot child route 已完成現行條文摘要第一輪比對，共套用 29 項校正；第140條依憲法判決限縮，第141條之1維持違憲失效排除。行為時法、專屬問句、其他判決與人工法律審查仍待完成。
2. 槍砲、組織犯罪、洗錢、贓物缺正式 crosswalk，維持 `BLOCKED_NO_FORMAL_CROSSWALK`。
3. 警詢證人具結的機關內規仍為 `UNKNOWN`。
4. 條陳最終正式版面依使用者指示暫緩。
5. 多人、登入、PostgreSQL／Supabase、RLS 與部署未授權。

## 隔離結論

- Runtime 只載入 `data/runtime/*.json` 白名單。
- `docs/audit/`、`review/`、`evidence/` 路徑不能成為編譯來源。
- 本報告不含問句記錄，也不得被題庫載入器使用。
