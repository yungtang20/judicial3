# LEGAL_REASONING_AUDIT

> 階段：第一階段唯讀盤點
>
> execution mode：`SINGLE_EXECUTOR`；runtime model identity：`UNVERIFIED`
>
> 本文件是 `AUDIT_REPORT`，不是正式問句、法條或 runtime 資料來源。

## 1. 盤點範圍與基線

本次盤點目標是「超商拾得手機案」的候選罪名判斷、構成要件對應、區辨問句與回答後重算流程。盤點範圍限於：

- `app/domain.py`
- `app/storage.py`
- `app/question_bank.py`
- `app/workflow.py`
- `app/documents.py`
- `app/static/`
- `tests/`
- `legal_sources/`
- `question_sources/`

**FACT：**目前工作分支為 `codex/sim-case-remediation`，分支上已有前一輪尚未提交的修正；本階段未再修改正式程式、題庫或資料庫。

**FACT：**既有驗證證據為 `91 passed`、題庫 `--check` PASS、`node --check` PASS；本報告不把這些結果擴張解讀成法律正確性或人工法律核准。

## 2. 實際執行流程

```text
HTTP /api/cases 或 make_case
  → extract_facts / 初步人物、行為、付款、證據抽取
  → analyze_candidates
  → _element_gaps
  → plan_next_batch
  → confirm_answers / update_confirmed_answers
  → _disputed_facts
  → analyze_candidates 重新排序
  → complete_gate2 / 文件輸出
```

案件保存流程為：

```text
RevisionStore.create
  → case_revision immutable snapshot
  → RevisionStore.commit_revision(CAS + command_id)
  → _insert_revision 寫入 normalized tables 與 payload_json
```

## 3. 模組與函式盤點

| 功能 | 實際位置 | 目前行為 | 證據狀態 |
|---|---|---|---|
| 案情輸入 | `app/server.py`：`POST /api/cases`；`app/domain.py`：`make_case` | 強制時間、地點、摘要及案件類型 | `FACT` |
| 初步事實抽取 | `app/domain.py`：`extract_facts` | 產生時間、地點、摘要、人物及通用未知欄位 | `FACT` |
| 人物／行為／付款／證據 | `app/domain.py`：`_initial_parties`、`_initial_behavior_events`、`_initial_payment_events`、`_initial_evidence_items` | 由摘要做有限度的 reported/inferred 結構化抽取 | `FACT`；完整性仍 `UNKNOWN` |
| Fact 保存 | `app/storage.py`：`case_fact`、`_insert_revision` | 以 revision 複製保存，並有 FK、索引及不可變 revision trigger | `FACT` |
| Evidence 保存 | `app/storage.py`：`evidence_item`、`fact_evidence_link` | 有資料表，但目前初始 evidence 尚未自動建立穩定 fact-evidence linkage | `FACT` / `GAP` |
| 法律 route | `app/question_bank.py`：`child_routes`；`data/runtime/route_coverage.json` | 提供 parent/child route、法條欄位與 fact elements | `FACT`；法律人工核准仍 UNKNOWN |
| 候選產生 | `app/domain.py`：`analyze_candidates` | 以 `ROUTE_RULES` 關鍵詞命中、反向線索及使用者指定路線計分 | `FACT` |
| 候選排序 | `app/domain.py`：`analyze_candidates`、`_available_questions` | 以 score 排序；問句只使用最高及接近的第二候選 | `FACT` |
| 要件缺口 | `app/domain.py`：`_element_gaps` | 由 child route 的 `fact_elements` 建立 UNKNOWN／ANSWERED_PENDING_REVIEW | `FACT`；與具體 fact 的精確 linkage 不足 |
| 問句生成 | `app/domain.py`：`_route_element_questions`、`_available_questions`、`plan_next_batch` | 題庫＋family＋route element 組成 1–5 題批次 | `FACT` |
| 問句理由 | `plan_next_batch` | 以 `why` 字串說明要件缺口或候選用途 | `FACT`；尚無獨立 question purpose/schema 欄位 |
| 回答更新 | `confirm_answers`、`update_confirmed_answers` | 新增或替換 answer fact，重新計算 disputed facts、候選及下一批問句 | `FACT` |
| 矛盾處理 | `_disputed_facts` | 只比較 victim/suspect 相同 fact_target 的回答，不覆寫原回答 | `FACT`；證據矛盾關聯不足 |
| revision / audit | `app/storage.py`：`commit_revision`、`_audit` | CAS、冪等、basis digest、歷史 snapshot、去識別 audit | `FACT` |

## 4. 已確認的法律資料邊界

**FACT：**`legal_sources/article_verifications.json` 已保存官方查證批次、法規名稱、pcode、條號查詢範圍及查證狀態。

**FACT：**官方全國法規資料庫目前列示刑法第320條為竊盜罪，第337條為侵占遺失物、漂流物或其他離本人持有之物；本報告引用的官方來源為：

<https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=C0000001>

**UNKNOWN：**本系統目前保存的是現行法條定位及 route fact elements，不等於已完成行為時法、裁判實務或機關內規核對。

## 5. 錯誤可能發生的層級

### 5.1 候選入口層：仍有關鍵字依賴

**FACT：**`analyze_candidates` 仍先用 `ROUTE_RULES` 對摘要及事實文字做 substring hit，再以命中數計算 score。

**INFERENCE：**即使已修正「手機／帳號／密碼」等孤立詞，仍可能有以下風險：

- 「遺留、失主、拾得」會提高 embezzlement route，但尚未先確認物品是否已脫離持有。
- 「拿走」會提高 theft route，但尚未先確認原持有狀態及主觀意圖。
- route score 仍不是由法律要件滿足度計算，而是文字線索的代理分數。

### 5.2 Fact 語義層：狀態尚未完全符合任務要求

**FACT：**目前 Fact 實際出現 `FACT`、`INFERENCE`、`UNKNOWN`、`NARRATIVE`、`STATEMENT`、`USER_CONFIRMED` 等狀態。

**GAP：**尚未完整提供 `ASSERTED`、`ADMITTED`、`DENIED` 的角色化 assertion record；目前回答主要寫入 `case.answers` 及 answer fact。

**INFERENCE：**若乙先否認、後承認、再提出不同說法，現有結構可能保留 revision，卻不足以表達「同一 party 對同一 fact 的多次 assertion 及其證據關聯」。

### 5.3 法律要件對應層：有 route elements，沒有完整候選推理鏈

**FACT：**child route 具備 `fact_elements`，`element_gaps` 具備 candidate、child route、element、element_type 及 status。

**GAP：**目前沒有一個獨立、可查詢的 candidate-element assessment，完整保存下列六項：

1. 法律依據及版本。
2. 構成要件。
3. 支持該要件的具體 fact assertion。
4. 不支持或矛盾的 fact assertion。
5. 尚待確認的 fact。
6. 證據及核心爭點。

### 5.4 候選狀態層：相容狀態不足

**FACT：**目前主要狀態為 `CANDIDATE`、`NEEDS_FACTS`、`LOWERED`、`UNSUPPORTED_ROUTE`。

**GAP：**尚未提供任務要求的 `PRIMARY`、`ALTERNATIVE`、`LOW_CONFIDENCE`、`UNRESOLVED`、`REJECTED` 對應欄位。

**最小相容對應建議：**

| 現有狀態 | 建議語義狀態 | 說明 |
|---|---|---|
| `CANDIDATE` | `PRIMARY` 或 `ALTERNATIVE` | 依要件證據覆蓋及區辨事實決定，不直接依 keyword count |
| `NEEDS_FACTS` | `UNRESOLVED` | 關鍵要件仍未知 |
| `LOWERED` | `LOW_CONFIDENCE` 或 `ALTERNATIVE` | 有相反事實，但不應直接刪除 |
| `UNSUPPORTED_ROUTE` | `REJECTED` 或保留原 blocked 狀態 | 明確表示不是法律結論，而是 runtime 不支援 |

### 5.5 問句層：有理由，但尚未完整分類及去重

**FACT：**`plan_next_batch` 會產生 `question_id`、`text`、`fact_target`、`element_type`、`layer`、`requirement`、`route_ids`、`route_element_keys` 及 `why`。

**GAP：**尚未獨立保存：

- `question_type`：核心、追問、區辨、證據核對。
- `generation_basis`：由哪個 candidate-element assessment 產生。
- `follow_up_condition`：回答什麼狀態才觸發下一問。
- 去重 key／同義問句抑制理由。

**INFERENCE：**目前相同或相近 element 仍可能由 family question 與 route supplement 各自產生；scheduler 沒有明確的「同一爭點已充分回答」判斷。

### 5.6 回答重算與矛盾層

**FACT：**`confirm_answers` 及 `update_confirmed_answers` 會建立新 revision，舊 revision 仍可讀，並重新計算候選。

**GAP：**回答更新主要依文字串及 `fact_target` 比較，尚未把「監視器顯示」「乙陳述」「店員證述」作為同一 fact 的多來源 assertion graph。

## 6. 既有測試能證明什麼

### 能證明

- `tests/test_revision_and_gate.py`：CAS、冪等、revision 保留、候選重算、相反線索、角色差異及問句排程基本行為。
- `tests/test_sim_case_remediation.py`：先前詐欺案例不因手機、帳號、密碼誤觸發竊盜／電腦 route；新增 schema tables、FK 及不可變 revision。
- `tests/test_question_bank.py`：題庫 manifest、family、child route、角色 coverage 及 runtime 隔離。
- `tests/test_security_and_schema.py`：audit 不保存案件正文、核心表存在及法律查詢欄位白名單。

### 不能證明

- 不能證明第320條與第337條在每個事實狀態下的法律結論正確。
- 不能證明「持有／脫離持有」會改變候選順位。
- 不能證明回答 A、B、C、D 會產生不同且合理的要件評估。
- 不能證明 `ASSERTED`／`ADMITTED`／`DENIED` 多次矛盾陳述可追溯。
- 不能證明問句已經完成去重、區辨、追問及證據核對分類。
- 不能證明實際 DOCX 中的法律推理鏈會被正確呈現。

## 7. 最小修正方案

### P0：先建立可驗證的 candidate-element assessment

在既有 `candidate` payload 中增加相容欄位，不立即重建全資料庫：

```text
candidate_status
candidate_role: PRIMARY | ALTERNATIVE | LOW_CONFIDENCE | UNRESOLVED | REJECTED
legal_basis: law_name, article_no, source_url, checked_at, status
element_assessments[]:
  element_id
  element_text
  status: SUPPORTED | CONTRADICTED | UNKNOWN | DISPUTED
  supporting_fact_ids[]
  contrary_fact_ids[]
  evidence_ids[]
  issue_ids[]
```

以「持有狀態」「他人動產／遺失物」「不法所有意圖」作為超商拾得手機案的第一個區辨 fact set。若三項仍 UNKNOWN，竊盜與第337條並列，不使用精確機率取代不確定性。

### P1：新增 assertion 與 evidence linkage

沿用既有 `case_fact`、`evidence_item`、`fact_evidence_link`，新增最小 `fact_assertion` payload 使用：

```text
ASSERTED | ADMITTED | DENIED | INFERRED | UNKNOWN
party_id
source_type: INTAKE | ANSWER | CCTV | WITNESS | DOCUMENT
source_ref
```

回答不得覆寫舊 assertion；修正只建立新 revision 及新 assertion。

### P1：問句生成改為爭點驅動

先由 element assessment 產生：

1. 一題核心問句。
2. 一題區辨問句。
3. 只有回答為 UNKNOWN、CONTRADICTED 或 DISPUTED 時產生追問。
4. 有客觀資料時才產生證據核對問句。

每題新增 `question_type`、`issue_id`、`generation_basis` 及 `follow_up_condition`；保留既有 `question_id` 與 `why`。

### P2：反事實回歸測試

新增基準、A、B、C、D 四組測試，驗證語義欄位及關聯，不只比較文字：

- A：持有狀態偏向 theft，但仍保留意圖 UNKNOWN。
- B：遺失物 route 優先，但第337條意圖仍 UNKNOWN。
- C：交給店員降低不法所有意圖，但不自動 REJECT。
- D：保留兩筆 assertion、建立 contradiction issue、產生針對性追問。

## 8. 可能影響的其他模組

- `app/domain.py`：候選、要件評估、問句排程及回答重算。
- `app/storage.py`：若將 assessment/assertion 正規化，需增加 revision child tables 及 migration。
- `app/server.py`：`public_case` 需輸出新欄位，但維持既有 `candidates` 欄位相容。
- `app/static/app.js`：候選卡片與問句說明需顯示法律要件、爭點及證據狀態。
- `app/documents.py`：若文件需要包含分析鏈，需確認不把候選假設寫成已證實事實。
- `tests/`：新增四組反事實與矛盾追問測試；不得刪除或降低既有 assertion。

## 9. 第一階段結論（修改前基線）

`PARTIAL_PASS`

**已確認：**既有系統已有 revision、route elements、問句批次、候選重算及部分 evidence schema。

**尚未通過：**候選順位仍有 keyword proxy；候選與法律要件、具體 assertion、證據及核心爭點尚未形成完整可追溯鏈；A/B/C/D 反事實測試尚未建立。

本節記錄第二階段實作前的基線；後續實作結果另見 `IMPLEMENTATION_REPORT.md` 與 `TEST_RESULTS.md`。本稽核報告本身不會被 runtime 載入。
