# ARCHITECTURE GAP AUDIT (架構差距稽核與根因分析報告)

- **專案名稱**: yungtang20/judicial2
- **任務編號**: JUDICIAL2-LEGAL-REASONING-RESEARCH-RECONSTRUCTION-AND-REMEDIATION-001
- **版本**: 2026-10-29
- **稽核員角色**: 軟體架構師 / 程式碼稽核與根因分析工程師 / 法律人工智慧系統架構師

---

## 目錄

1. [現行系統架構現狀審查](#一現行系統架構現狀審查)
2. [根本原因分析 (Root Cause Analysis, RCA)](#二根本原因分析-root-cause-analysis-rca)
3. [目標架構 vs. 現行架構差距詳細比對矩陣](#三目標架構-vs-現行架構差距詳細比對矩陣)
4. [核心資料合約與狀態機定義 (Data Contracts & State Machine)](#四核心資料合約與狀態機定義)
5. [重構工程與修復實施計畫 (Remediation Plan)](#五重構工程與修復實施計畫)

---

## 一、現行系統架構現狀審查

### 1.1 現有程式庫檔案資產總覽
目前專案儲存庫包含以下核心模組：
- **前端呈現層**:
  - `src/App.tsx`: 具備 Google 式單一對話框首頁（Landing Mode）及多視角搜尋結果頁面（Results View），支援法規、裁判、論著標籤切換與筆錄編輯。
  - `src/services/caseAnalyzer.ts`: 提供多種典型案件之預設樣板（如虛擬貨幣假投資、ATM 車手、遺失物盜刷、竊盜、傷害恐嚇等），結合正則實體抽取。
- **後端與推理服務層**:
  - `src/services/analyzer.ts`: 宣告包含 Gate 1 到 Gate 5 之分析函式，具備基本 9 類問句產生與公文條陳驗證邏輯。
  - `src/server/databaseService.ts`: 整合 PGlite WASM 輕量化 PostgreSQL 16 引擎，具備 24 張核心資料表與版本快照存檔能力。
- **資料庫遷移與稽核套件**:
  - `database/migrations/`: 0001 到 0009 遷移腳本，定義完整 Enums、資料表、外鍵與 RLS 安全性宣告。
  - `database/scripts/sim_2026_001_runner.ts`: 針對單一模擬案件（SIM-2026-001）之端到端驗證腳本。

### 1.2 發現之重大系統架構缺陷
1. **靜態正則分支導致單一罪名隧道偏誤 (Tunnel Vision Bias)**:
   - `caseAnalyzer.ts` 以大型 `if...else if` 正則匹配（如 `/投資|虛擬貨幣/`）直接鎖定單一 `analyzeCryptoInvestment` 樣板，未能同時對「民事債務糾紛」、「單純提供帳戶幫助犯」、「正犯洗錢罪」等進行平行多候選路徑檢驗。
2. **缺乏上游變更引發下游自動無效化之狀態機 (Missing Downstream Invalidation)**:
   - 當使用者在介面中編輯案件事實（如將涉案金額從 30 萬改為 0 元，或將「承認」改為「否認」）時，系統僅局部更新文字，並未自動將關聯之構成要件、候選罪名評估、問句優先級及條陳標記為 `STALE` 並重算。
3. **二值邏輯陷阱 (Binary Logic Trap)**:
   - 部分邏輯在處理未知狀態（`UNKNOWN`）時，容易退化為當作「不存在」；對於涉嫌人「否認（`DENIED`）」之辯解，缺少與客觀監視器、扣案物證比對產生「矛盾衝突問句（Contradiction Inquiry）」之自動化機制。

---

## 二、根本原因分析 (Root Cause Analysis, RCA)

| 根因編號 | 缺陷現象 | 技術與法理根因 (Root Cause) | 潛在實務危害 |
| :---: | :--- | :--- | :--- |
| **RCA-01** | 單一罪名隧道視野 (Tunnel Vision) | 採用單一分類器思想，把「輸入案情」當成「罪名判決標籤匹配」，忽略了刑事偵查初期事實往往尚未明朗，必須同時考量主位罪名、備位罪名及阻卻違法事由。 | 偵查方向過早定型，忽略替代抗辯（例如：誤把侵占離本人持有物直接當成加重竊盜，或忽略民事糾紛可能性），導致筆錄遺漏關鍵脫罪待證事實。 |
| **RCA-02** | 混淆 UNKNOWN 與 FALSE (三值邏輯缺失) | 程式設計慣用布林邏輯（`boolean`：true/false），未落實法律推理必備之三值邏輯（Three-Valued Logic: True, False, Unknown）。 | 將「尚不清楚收款帳戶實際身分」誤判為「無收款帳戶」，忽略了偵查機關應主動調取金流與通聯之法定職責。 |
| **RCA-03** | 混淆 DENIED 與事實不存在 | 將行為人「否認犯意」或「辯稱跑腿」直接視為不成立犯罪，或反向將否認直接視為狡辯而忽略調查其辯解之真實性。 | 違反《刑事訴訟法》第2條「實施刑事訴訟程序之公務員，就該管案件，應於被告有利及不利之情形，一律注意」之法定核心原則。 |
| **RCA-04** | 缺少下游資料連動無效化 (No Invalidation Engine) | 缺乏狀態相依圖（Dependency Graph）與版本拓撲排序。事實變更時，衍生之要件該當狀態未即時轉為 `STALE`。 | 警詢筆錄問句已針對新案情更新，但輸出之公務條陳仍記載舊版本的犯罪事實，造成公私文書記載矛盾。 |
| **RCA-05** | 版本凍結不可竄改性欠缺程式層保證 | 過去依賴資料庫 Trigger 保證，但在前端與服務層缺乏對已鎖定版本（Locked Revision）的防寫防竄改攔截。 | 誤覆蓋已簽核之公文版本，破壞司法偵查證據保管鏈（Chain of Custody）。 |

---

## 三、目標架構 vs. 現行架構差距詳細比對矩陣

| 架構領域 | 現行系統狀況 (Current State) | 目標架構規範 (Target Architecture) | 差距等級 | 改善方案 |
| :--- | :--- | :--- | :---: | :--- |
| **事實語意狀態** | 支援字串型態 `ASSERTED`, `DENIED`, `UNKNOWN`，但分析器常回退為單純文字串接。 | 嚴格五元狀態：`ASSERTED`（陳述）、`ADMITTED`（坦承）、`DENIED`（否認）、`INFERRED`（推論）、`UNKNOWN`（未知），並綁定證據強度。 | **P0** | 建立 `LegalReasoningEngine`，支援結構化事實狀態推導與三值評估。 |
| **候選法律方向** | 依關鍵字預設單一方向，備位方向僅為靜態文字陣列。 | 支援 `PRIMARY`（主位方向）、`ALTERNATIVE`（備位/替代方向）、`REJECTED`（已排除方向）、`UNRESOLVED`（未決待查）。 | **P0** | 實作多路徑平行涵攝引擎，針對詐欺/侵占/竊盜/民事糾紛自動展開對比矩陣。 |
| **構成要件涵攝** | 要件僅具備名稱與說明，無即時反向事實與矛盾事實關聯。 | 要件具備 `SATISFIED`, `PENDING_VERIFICATION`, `UNSUPPORTED`，並分別關聯支持、反對與未知事實清單。 | **P0** | 每個候選方向配賦完整構成要件樹，自動根據事實狀態計算滿足度。 |
| **偵訊筆錄生成** | 支援 9 類問句模板，但問句與要件未有雙向動態關聯。 | 依據當前未滿足要件（PENDING）與否認抗辯（DENIED），動態產生針對性之非誘導性中性問句。 | **P1** | 問句生成器自動針對 `UNKNOWN` 事實與爭點產出查證問句。 |
| **連動無效化機制** | 僅前端重新執行 analyze，缺少版本失效標籤（STALE）。 | 實作響應式失效狀態機：事實異動 $\rightarrow$ 標記下游要件/罪名/條陳為 `STALE` $\rightarrow$ 觸發重算或提示人工覆核。 | **P0** | 於引擎中建立 `invalidateDownstream()` 與版本遞增邏輯。 |
| **公文條陳產出** | 支援公務條陳體裁，但摘要未與已確認事實完全綁定。 | 公務條陳嚴格僅引用「經查證或主辦確認之指定版本事實」，未審核事實不得作為定罪結論寫入條陳。 | **P1** | 條陳生成模組加入前置驗證約束，不合格時拋出驗證警示。 |

---

## 四、核心資料合約與狀態機定義

### 4.1 核心五元事實狀態 (AssertionStatus)
```typescript
export type AssertionStatus = 
  | 'ASSERTED'  // 當事人或證人陳述，尚未經客觀證物獨立補強
  | 'ADMITTED'  // 被告或涉嫌人自白坦承
  | 'DENIED'    // 被告或涉嫌人抗辯否認（非代表事實不存在，而係爭點焦點）
  | 'INFERRED'  // 偵查員或模型基於間接事證推論（嚴禁自動視為確定事實）
  | 'UNKNOWN';  // 客觀事實未明、待查項目（嚴禁視為 FALSE，必須引導追查）
```

### 4.2 候選罪名狀態 (CandidateStatus)
```typescript
export type CandidateStatus =
  | 'PRIMARY'        // 主位候選罪名（當前事證最相符之方向）
  | 'ALTERNATIVE'    // 備位/競合或替代法律方向（防範起訴法條變更或漏未起訴）
  | 'LOW_CONFIDENCE' // 事證顯著不足之暫定方向
  | 'REJECTED'       // 經調查已確定排除之方向（須註明排除理由）
  | 'UNRESOLVED';    // 關鍵爭點未明，尚無法定性
```

### 4.3 下游無效化狀態機流程 (Invalidation Pipeline)
```text
[FactItem 修正/新增] 
        │
        ▼ (觸發無效化)
[標記關聯 LegalElement -> STALE]
        │
        ▼
[標記關聯 LegalCandidate -> STALE / RE_EVALUATING]
        │
        ▼
[標記關聯 InterviewQuestions -> STALE (重新計算優先級)]
        │
        ▼
[標記 OfficialReport -> STALE (禁止輸出為正式已審核文件)]
        │
        ▼
[產生新版本快照 Revision (N + 1) 並保留歷史紀錄]
```

---

## 五、重構工程與修復實施計畫

1. **第 1 階段：實作獨立之法律推理核心引擎 (`src/services/legalReasoningEngine.ts`)**
   - 封裝階層犯罪論涵攝邏輯。
   - 實作多候選方向生成器（支援詐欺取財、加重詐欺、侵占離本人持有物、普通竊盜、洗錢、傷害、恐嚇取財、民事債務不履行等雙向或多向對比）。
   - 實作五元事實狀態機與矛盾事實保留邏輯。
   - 實作 9 大分類非誘導性問句動態映射。
   - 實作下游失效（Cascade Invalidation）與版本遞增機制。

2. **第 2 階段：建立 16 案情端到端回歸測試套件 (`tests/legal_reasoning_scenarios.test.ts`)**
   - 涵蓋：未知管領力、櫃檯店員管領、脫離占有即時送交、否認與監視器矛盾、證人歧異指述、連續多被害人行為、未遂與預備、民事違約 vs. 刑事詐術、偽造文書 vs. 不正操作、洗錢 vs. 贓物、傷害 vs. 殺人未遂、共同正犯 vs. 幫助犯、事實變更連動失效、版本凍結防竄改、9 類問句全覆蓋、警政公文嚴格格式驗證等 16 大真實情境。

3. **第 3 階段：建立目標達成靜態與邏輯稽核腳本 (`tools/legal_reasoning_goal_audit.py`)**
   - 自動檢驗所有交付檔案之存在性、資料型別定義合約、禁絕項目（如禁止單一罪名硬編碼、禁止 UNKNOWN=FALSE 邏輯）、測試執行結果報告完整性。

4. **第 4 階段：回歸驗證與編譯驗收**
   - 執行 `npx tsx tests/legal_reasoning_scenarios.test.ts`。
   - 執行 `python3 tools/legal_reasoning_goal_audit.py`。
   - 執行 `compile_applet` 確保前端 SPA 構建零錯誤。
