# Phase 2 缺陷與修復

| ID | 嚴重性 | 根因 | 修復／狀態 | 回歸證據 |
|---|---|---|---|---|
| P2-001 | P1 | 混合句只產生一個 fact，辯解／未知遭漏失 | 拆分轉折與待確認 clause；UNKNOWN 先於 INFERRED | corrective + 內建瀏覽器 6 facts |
| P2-002 | P0 資料正確性 | `expected_clarification` 被當成已填回答 | 新問句回答固定空字串 | corrective + UI 空白回答 |
| P2-003 | P1 | 每個 candidate 都取 statute table 第一筆 | 解析 `statuteRef`，依 law/article/paragraph 查找或建立 UNVERIFIED row | MVP flow 320/337 round-trip + browser |
| P2-004 | P1 安全 | 只要有 Gemini key 即外傳，失敗仍 200 fallback | 顯式 external AI gate、無設定／錯誤回 503、固定 system prompt、輸入限制 | API route test |
| P2-005 | P1 | `npm start` 用 Node 直接解析 `.ts` 與 `.js` import | start 改為 `tsx server.ts` | production start test |
| P2-006 | P1 安全 | save API 只驗頂層 | fact/candidate/question 巢狀 schema、enum 與長度限制；body 1 MB | owner route invalid payload=400 |
| P2-007 | P2 | 表單缺可辨識名稱 | 補上 `aria-label` | TypeScript/build + browser DOM |
| P2-008 | P2 | predeploy audit 把 AI gate 硬編 PASS | 改讀實際 server control | Python/static audit |
| P2-009 | P0 部署阻擋 | 正式 auth/revoke 不存在 | 未修復；需要身分服務與 server-side session lifecycle | FAIL |
| P2-010 | P1 部署阻擋 | 真實 PostgreSQL client、migration ledger、RLS context 不存在 | 未修復；缺隔離 PostgreSQL且需架構工作 | FAIL/BLOCKED |
| P2-011 | P1 部署阻擋 | 無 Render Blueprint／持久化策略 | 未修復；不得在未決定 DB/auth 前建立誤導性 Blueprint | FAIL |
| P2-012 | P1 法律來源 | runtime 法律檢索不存在 | 未修復；未核對法條明確標 UNKNOWN | FAIL |
| P2-013 | P2 | 實際下載、axe 與網路中斷無可重跑 harness | 未修復 | NOT_RUN |

沒有刪除或降低測試標準。未修復項目均未標示 PASS。
