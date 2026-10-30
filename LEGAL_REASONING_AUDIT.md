# JUDICIAL3 法律推理獨立驗收稽核

日期：2026-10-29。執行模式：`SINGLE_AGENT_MODE`。

## FACT：實際路徑與根因

- `src/App.tsx` 的 `handlePerformSearch` 直接呼叫 `LegalReasoningEngine.analyzeFullCase`；`src/services/caseAnalyzer.ts` 是委派相容層。
- `analyzeFullCase` 依序呼叫事實抽取、證據抽取、候選要件分析、問句生成與條陳生成。
- `evaluateLegalCandidates` 原本以案型正規表示式建立固定候選，且多處直接設定 `SATISFIED`，未要求已取得 Evidence。
- `parseBehaviorsAndEvidence` 原本只要文字出現監視器、匯款或信用卡即標記 `OBTAINED`。
- `server.ts` 原本案件 API 無後端認證、owner filter 或跨案件授權；`databaseService.ts` 原本會刪 `postmaster.pid` 並在 persistent PGlite 失敗時切 memory fallback。
- `database/pglite_store` 原本有 165 個、約 22.9 MB 執行期檔案被 Git 追蹤。

## 本次修正

- 新增 `normalizeCandidateTraceability`：`SATISFIED` 必須有有效 Fact 與已取得 Evidence 關聯，否則降級；保留 UNKNOWN、DENIED 與反向事實。
- 新增 `src/services/offenseRegistry.ts`：第320條、第337條及第277／305／271條以持有、取得、行為、結果、主觀認知與反向事實等要件並列評估；手機及暴力路線不再使用舊案型候選分支。
- registry 路線問句改為中立事實問句，並綁定候選與要件 ID。
- Fact 變更會保存舊 revision 的完整 facts、evidence、candidate、question、answer 與 report 快照。
- 證據抽取改為明示已取得／已調閱／已檢附才是 `OBTAINED`，否則 `PENDING_SEARCH`。
- 增加超商手機案及暴力家族反事實測試，驗證第 320／337 條及第 277／305／271 條並列、未知不定罪、Evidence 追溯及 revision 失效。
- 加入後端 HMAC session token middleware；user ID 從已驗證 token subject 取得，資料庫查詢／寫入再以 owner 篩選。
- PGlite 初始化 fail-closed，不刪除既有資料或鎖檔。
- runtime DB 改為 Git ignored 並從 index 移除，工作目錄資料未刪除。
- 研究報告新增逐來源核對表；無法由公開頁面核實者維持 `UNKNOWN`／`NOT_VERIFIED`。

## 限制

既有案型正規表示式候選入口仍存在；本次由追溯閘門限制其法律狀態，尚未完成完整法規資料驅動 registry。尚未完成正式登入身分服務與真實 PostgreSQL/RLS 整合測試，因此總驗收不能宣稱全面 PASS。
