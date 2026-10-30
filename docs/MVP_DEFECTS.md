# JUDICIAL3 MVP 缺陷與修復紀錄

## DEF-001：dev session 可在未明確設定時啟用

- 嚴重性：P0 邊界缺陷
- 根因：原程式只排除 production，未要求明確的本機開關，也未限制 loopback。
- 修復：`JUDICIAL3_ALLOW_DEV_SESSION === 'true'` 且來源必須是 loopback；production 一律 404。
- 回歸：`tests/api_route_auth.test.ts` 實際 production child process 驗證 404、未登入 401、有效 token 200。

## DEF-002：案件重開後只用 raw text 重新分析

- 嚴重性：P1
- 根因：`handleLoadSavedCase()` 忽略持久化的候選、要件、問句及答案。
- 修復：資料庫 API 回傳 elements、revision history；前端依目前 revision 還原 Fact、Evidence、Candidate、Element、Question、答案及條陳摘要。
- 回歸：隔離 PGlite 流程驗證保存、重讀、修訂及歷史版本。

## DEF-003：問句答案未持久化

- 嚴重性：P1
- 根因：保存 API payload 有 answerText，但資料表與 INSERT 未保存。
- 修復：migration 0010 新增 `interview_questions.answer_text`，保存與重新讀取均使用該欄位。
- 回歸：`tests/mvp_complete_flow.test.ts` 驗證問句追溯及答案欄位。

## DEF-004：前端缺少問句管理操作

- 嚴重性：P1
- 根因：原 UI 只能編輯回答，不能編輯問句文字、刪除或新增。
- 修復：加入問句文字編輯、新增、刪除控制，變更時標記下游需重新確認。
- 回歸：TypeScript 與 production build 通過；瀏覽器互動仍 `NOT_RUN`。

## DEF-005：報告便利修正會填入虛構資料

- 嚴重性：P0 資料正確性風險
- 根因：`analyzer.ts` 的 `autoFixReport()` 以固定日期、機關、人員、案號補值。
- 修復：改為待填標記，不再捏造案件欄位；摘要超過 500 Unicode 字元時拒絕驗證。
- 回歸：型別、14 情境、corrective、MVP audit 及 build 通過。

## 尚未修復／未完成

- 正式登入、token rotation、logout/revoke 及 PostgreSQL/RLS 實際部署驗證。
- 外部 LLM／法律檢索故障注入與瀏覽器下載、鍵盤、axe 驗收。
- 全部罪章 route 及正式 DOCX／公司模板 round-trip。
