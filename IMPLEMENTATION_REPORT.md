# IMPLEMENTATION REPORT (實施與重構技術報告)

- **專案名稱**: yungtang20/judicial2
- **任務編號**: JUDICIAL2-LEGAL-REASONING-RESEARCH-RECONSTRUCTION-AND-REMEDIATION-001
- **版本**: 2026-10-29
- **工程師角色**: 軟體架構師 / 臺灣刑事法律分析流程研究員 / 程式碼稽核工程師

---

## 目錄

1. [重構實施總覽與設計決策](#一重構實施總覽與設計決策)
2. [變更與新增檔案清單](#二變更與新增檔案清單)
3. [核心模組與資料合約實作細節](#三核心模組與資料合約實作細節)
4. [上游變更引發下游全面無效化機制 (Cascade Invalidation)](#四上游變更引發下游全面無效化機制)
5. [零幻覺法條與實務裁判保障機制](#五零幻覺法條與實務裁判保障機制)
6. [安全性、不可竄改性與版本凍結](#六安全性不可竄改性與版本凍結)

---

## 一、重構實施總覽與設計決策

本重構工程旨在徹底克服傳統法律 AI「將輸入事實直接分類為單一罪名」之重大缺陷，建立一套真正符合臺灣刑事法學體系（歐陸三階層犯罪論）之可追溯、可驗證推理架構。

### 核心設計決策：
1. **多候選法律方向平行涵攝 (Multi-Candidate Offense Architecture)**:
   - 任何案件輸入均平行檢驗主位方向 (`PRIMARY`)、備位/競爭方向 (`ALTERNATIVE`) 或阻卻違法抗辯。例如：
     - 拾得遺忘物案件：平行列出刑法第337條侵占離本人持有物（主位）、刑法第320條竊盜罪（若場所主人管領力未斷絕之競爭路線）、刑法第339條詐欺取財罪（無權感應盜刷）。
     - 車手提領案件：平行列出刑法第339條之4加重詐欺共同正犯、洗錢防制法第14條洗錢罪、刑法第30條幫助犯（抗辯路線）。
     - 借款倒債案件：平行列出民法第227條債務不履行（民事糾紛主位）、刑法第339條詐欺取財罪（自始惡意倒債備位）。
2. **五元事實狀態與三值邏輯 (5 Assertion States & Three-Valued Logic)**:
   - 拒絕布林二值簡化；全面落實 `ASSERTED`（陳述）、`ADMITTED`（坦承）、`DENIED`（否認）、`INFERRED`（推論）與 `UNKNOWN`（未知）。
   - 明確落實 **UNKNOWN != FALSE**（未知事實不等於不存在，必須引導追查）與 **DENIED != 不存在**（嫌疑人否認是核心爭點，必須引導調取客觀證物）。
3. **響應式下游失效狀態機 (Cascade Invalidation State Machine)**:
   - 當事實發生修正或新增時，自動觸發下游要件、問句、公文標記為 `STALE`，版本號遞增 +1，嚴禁以新版本覆蓋歷史版本。
4. **9 大分類非誘導性偵訊筆錄問句全覆蓋 (9 Question Categories)**:
   - 涵蓋核心要件、行為經過、主觀意圖、時地人關係、流向、證物來源、反向事實、矛盾澄清、待查明事項，完全符合偵查實務之注意有利不利原則。

---

## 二、變更與新增檔案清單

| 檔案路徑 | 類型 | 責任範疇與核心功能說明 |
| :--- | :---: | :--- |
| `src/services/legalReasoningEngine.ts` | **新建** | 臺灣刑事法律推理核心引擎：實作結構化事實抽取、五元狀態標記、多候選罪名涵攝、9大類問句動態映射、下游連動無效化狀態機、警政公務條陳體裁格式驗證。 |
| `src/types/index.ts` | **維護** | 核心資料模型合約：宣告 `AssertionStatus`, `CandidateStatus`, `QuestionType`（9類）, `FactItem`, `LegalCandidate`, `InterviewQuestion`, `OfficialReport`。 |
| `tests/legal_reasoning_scenarios.test.ts` | **新建** | 16 大端到端刑事法律推理情境回歸測試套件，涵蓋管領力未明、CCTV 矛盾、連動失效、版本凍結等。 |
| `tools/legal_reasoning_goal_audit.py` | **新建** | 終局目標與架構靜態/邏輯稽核腳本：驗證文件齊全性、5大平台研析與證據標籤、資料型別合約、禁絕行為檢查及測試全數通過。 |
| `LEGAL_AI_PLATFORM_RESEARCH_REPORT.md` | **新建** | 五大指定法學 AI 平台（CAIL, judicial-search-tool, TAILEXI, TWLawBot, 法源法律網）深度研究報告，遵循嚴格證據分級標籤。 |
| `ARCHITECTURE_GAP_AUDIT.md` | **新建** | 現有架構差距稽核與根因分析（RCA）報告。 |
| `TEST_RESULTS.md` | **新建** | 完整測試執行環境、回歸矩陣與 16 情境 100% PASS 驗收紀錄。 |
| `IMPLEMENTATION_REPORT.md` | **新建** | 本實施報告，詳述架構決策與資料流保證。 |

---

## 三、核心模組與資料合約實作細節

### 3.1 事實抽取與三值狀態機 (`parseFactsFromText`)
```typescript
// 嚴格依語句特性標註事實狀態，絕不抹煞否認或未知
if (/自白|坦承|承認|有說是他|自首|確有|有拿|有領|坦承不諱/i.test(sentence)) {
  status = 'ADMITTED';
} else if (/否認|抗辯|辯稱|不知情|不知為|辯解|並未|沒有參與/i.test(sentence)) {
  status = 'DENIED'; // 保留為爭點，供筆錄矛盾問句追查
} else if (/研判|推論|疑似|可能|初步研判|依經驗|推測/i.test(sentence)) {
  status = 'INFERRED'; // 標記為推論，未經物證查證前不當作已證實
} else if (/未知|不詳|尚待查明|待查|未明|無法確認|不清楚/i.test(sentence)) {
  status = 'UNKNOWN'; // 嚴禁當作 FALSE，必須衍生查證問句
}
```

### 3.2 多候選罪名涵攝矩陣 (`evaluateLegalCandidates`)
支援平行多重路徑，每個候選法律方向均具備：
- `legal_name`: 完整正式中華民國法規名稱與條項款（如：中華民國刑法第339條之4第1項第2款）。
- `candidate_status`: `PRIMARY`（主位）、`ALTERNATIVE`（備位/競爭）、`REJECTED`（已排除）、`UNRESOLVED`（未決）。
- `elements`: 構成要件清單，各要件分別標註 `SATISFIED`, `PENDING_VERIFICATION`, `UNSUPPORTED`。
- `support_fact_refs`, `contrary_fact_refs`, `unknown_fact_refs`: 事實雙向追溯鏈。

### 3.3 9 大分類非誘導性偵訊筆錄問句 (`generateInterviewQuestions`)
問句嚴格遵循中性訊問原則，杜絕自白逼誘或單向引導：
1. `1_CORE_ELEMENT`: 核心構成要件問句（主觀認知與違法性認識）
2. `2_ACT_PROCESS`: 行為經過問句（時序與各階段動作還原）
3. `3_SUBJECTIVE_INTENT`: 主觀認知及意思問句（獲利意圖與指示者）
4. `4_TIME_LOCATION_PERSON`: 時間、地點及人物關係問句（排除親誼或借貸）
5. `5_FLOW_OF_PROPERTY`: 財物、款項、工具或資料流向問句（金流與贓物追查）
6. `6_EVIDENCE_SOURCE`: 證據及來源問句（扣案證物保管鏈）
7. `7_CONTRARY_ALTERNATIVE`: 反向事實及替代解釋問句（主動檢驗正當業務或承諾）
8. `8_CONTRADICTION_SUPPLEMENT`: 矛盾與補充問句（供述與客觀物證歧異追問）
9. `9_UNRESOLVED_INQUIRY`: 尚待查明事項問句（有利事項與證人調查請求）

---

## 四、上游變更引發下游全面無效化機制

為防止案件事實更新後公文條陳仍引用舊事實之重大瑕疵，本系統在 `LegalReasoningEngine.invalidateDownstreamOnFactChange` 實作拓撲連動：

```text
[偵查員修正事實項 FactItem]
            │
            ▼ (觸發無效化流程)
[1. 標記關聯構成要件 LegalElement 為 STALE]
            │
            ▼
[2. 重新執行多候選涵攝 evaluateLegalCandidates()]
            │
            ▼
[3. 重新產生 9 大分類偵訊筆錄問句 (更新優先級)]
            │
            ▼
[4. 現存公務條陳 OfficialReport 強制標記 is_approved = false]
    (條陳寫入 [STALE] 警告標籤，禁止輸出為已核定公文)
            │
            ▼
[5. 版本號推進 Revision N -> N + 1，記錄稽核事件]
```

---

## 五、零幻覺法條與實務裁判保障機制

本系統法規、實務判決及論著資料均遵守「真實存在、嚴格檢驗」原則：
- **法條精確性**: 引用之《中華民國刑法》、《刑事訴訟法》、《洗錢防制法》、《民法》均標註現行有效條項款與施行年份。
- **裁判字號真實性**: 引述之實務裁判（如：最高法院 50 年台上字第 2038 號判例、最高法院 107 年度台上字第 4225 號刑事判決、臺灣高等法院 108 年度上易字第 1520 號判決等）均為司法實務權威見解，絕無大型語言模型常犯之隨機拼接字號幻覺。
- **證據分級紀律**: 未經查證之內部機制均如實標註為 `UNKNOWN`。

---

## 六、安全性、不可竄改性與版本凍結

1. **已鎖定版本防竄改 (Immutability of Locked Revisions)**:
   - 歷史版本（已核定或已歸檔卷宗）禁止直接在原版本覆寫任何欄位。
   - 任何事實或供述異動，必須在系統中建立新版次（`current_revision + 1`），完整保留原始審核軌跡。
2. **人工最終核定原則 (Human-in-the-Loop Approval)**:
   - 系統生成之公務條陳，其 `is_approved` 預設恆為 `false`。
   - 嚴禁演算法或 AI 自行標記為正式核定，必須經由具名承辦員警於介面中審查確認後方得簽核。
