# Lifecycle Record

> 本檔保留階段與驗證歷史。下方早期 `COMPLETE` 僅代表當時有界線的實作輪次，不能作為目前法律完整、Human Gate、部署或整體驗收證明。現況應以實際 checkout、測試及 [README.md](README.md) 的證據規則重新確認。

## 2026-10-26 基準路由歸檔與下一路由准入

```yaml
execution_mode: REVIEWED_PIPELINE
routing_triggers: [S3, S4]
archive_id: QRA-TH320-1-MOV-20261026-01
route_id: theft_320_1_movable
submission_sha256: 21807B231A1868BE9AA5565904471CE8A9C2DD1B5EE0B74A40CFE59EA30A6FA7
archive_file_sha256: 9BCB4A012C2557504ACEAFBBAE2C9EA412877E26B0183E046B82C709DE7087A6
ruleset_id: question-rules-v2-draft
ruleset_file_sha256: DAF06F74D278165A436FDA028133EFC989A289A14660FEB4066B9BD8678DBB16
ruleset_acceptance_scope: QUESTION_DESIGN_ONLY
runtime_ruleset_status: UNCHANGED_RUNTIME
legal_acceptance: false
legal_conclusion: false
calibration_review: PASS
route_review_gate: PASS
case_human_gate: REQUIRED
user_final_acceptance: PENDING
runtime_auto_advance: false
deployment_status: NOT_DEPLOYED
next_route_id: aggravated_theft_321
next_route_selection_owner: CONTROLLER
```

- 完整 submission、Reviewer Decision 與驗證紀錄已保存於 `docs/evidence/question_route_archives/theft_320_1_movable-iteration-4-20261026.txt`，manifest 為 `docs/evidence/question_route_archive_manifest.json`。
- `question-rules-v2-draft` 只在問句設計範圍通過基準校準；未升級為 runtime 規則，也不是法律內容、部署或實際個案核准。
- 同一次完整 pytest 為 `630 passed`；Node 前端測試 `31 passed`、JavaScript 語法 PASS、健康檢查 HTTP 200。這些只屬工程證據。
- 獨立准入審查建議採 `ACCEPT_WITH_MODIFICATIONS`：先完成 archive 與 hash 對帳，再由 controller 選取 locked queue 的 `aggravated_theft_321`。實際模型身分維持 `UNVERIFIED`。

---

## 2026-10-26 aggravated_theft_321 問句設計審核與歸檔

```yaml
execution_mode: REVIEWED_PIPELINE
routing_triggers: [S3, S4]
archive_id: QRA-AGT321-20261026-01
route_id: aggravated_theft_321
submission_sha256: 17DC2C8975944A33B7B74AF9D2BB414AC4A07BD03D031AAABEA650B926D665CD
archive_file_sha256: 6B960B1224AF42B4683892F4600EC05F10AE42703BCA76E7ACDC712088FB2743
ruleset_acceptance_scope: QUESTION_DESIGN_ONLY
official_source_status: VERIFIED_CURRENT_BEHAVIOR_TIME_UNKNOWN
calibration_review: PASS
route_review_gate: PASS
case_human_gate: REQUIRED
legal_conclusion: false
runtime_enabled: false
runtime_auto_advance: false
deployment_status: NOT_DEPLOYED
next_locked_target: embezzlement_335_general
```

- 8 個 concepts 涵蓋第321條六款客觀事實、自由敘述及對已確認單一客觀情況的知悉來源；不直接詢問法律結論。
- Exact dedupe 為 0；既有 T-A-01 至 T-A-06 採 replace/do-not-coemit 契約。20 題合成上限實際排版為 victim 2頁、suspect 2頁、transfer 3頁。
- 完整 pytest `630 passed`、前端 `31 passed`、JavaScript 語法 PASS、健康檢查 HTTP 200。
- 完整 artifact 已歸檔；controller 已鎖定下一個單一路由 `embezzlement_335_general`，不需使用者逐 route 核准。

---

## 2026-10-14 審核責任與 loop 邊界修正

```yaml
route_review_owner: CODEX_REVIEWER
user_review_mode: FINAL_BATCH_ONLY
case_human_gate_owner: HUMAN_CASE_OFFICER
route_execution_unit: ONE_CHILD_ROUTE_AT_A_TIME
route_auto_advance_after_codex_pass_and_archive: true
runtime_auto_advance: false
user_final_acceptance: PENDING
```

- 使用者不再逐 route 設定規則、核准問句或選擇下一罪章。
- 執行 AI 每次只製作一個 child route，完成後停下交給 Codex 審核；不得自行批次生成或切換 route。
- Codex 負責逐 route 的結構、問法、法律 effects 與校準審核。通過並完成完整歸檔後，controller 依鎖定 queue 接續下一個 route。
- 使用者只在整個已授權 queue 完成後做最終成果驗收。
- 實際案件仍保留承辦人 `CASE_HUMAN_GATE`，本次治理修正不授權 runtime、題庫、crosswalk 或部署變更。

---

## 2026-10-14 標準問句修正版 iteration 2

```yaml
execution_mode: REVIEWED_PIPELINE
routing_triggers: [H2, S3, S5]
primary_model: GPT-5
independent_reviewer_model: UNVERIFIED
submission_hash_scope: UTF8_LF_BYTES_BETWEEN_SUBMISSION_MARKERS
submission_sha256: F91844D0A73F7E77718614B06ED30441190D197FCD524E5ACD7A1DB98FFEC73A
work_item_file_sha256: 0E8060400AB96F65EC1F8CFF67C5BE1BAC05F9ADF5379EA6DA0EBEF79A534E71
runtime_enabled: false
human_gate: REQUIRED
next_route: NOT_AUTHORIZED
final_status: REFERENCE_STANDARD_READY_FOR_HUMAN_LEGAL_REVIEW
```

### 修正內容

- 將 concept 展開為單一 `target_interview_role` instance，並固定穩定 ID 與 witness review-only 邊界。
- 每題加入可機械判斷的 `trigger_condition`、明示 enum `answer_map`、既有題引用及 dedupe action。
- 將同意改為授權範圍三態，禁止以單一同意答案直接排除 theft 或認定民事爭議。
- 限制遺失狀態及抗拒能力只能向有直接知識的 victim 詢問，避免由 witness 或涉嫌人推論他人主觀狀態。
- 補上逐題 effects 聚合、必要前提、衝突處理及完整 facts 重算規則；任何 route 均不得自動輸出 `EXCLUDED`。
- 工作單審核雜湊改用 submission marker 內的 canonical UTF-8 LF bytes，Reviewer Decision 排除於雜湊範圍外。

### 獨立審查決策

- R1：`ACCEPT_WITH_MODIFICATIONS`；`questions/theft.md` 實際存在，E2E timeout 隔離重跑通過，其餘結構缺口納入修正。
- R2：`ACCEPT`；角色實體化、trigger、mapping、dedupe 與聚合契約均需修正。
- R3：`ACCEPT_WITH_MODIFICATIONS`；先合法持有可提高侵占候選，但返還、拒還或處分等必要事實未齊時，聚合結果維持 `NEED_REVIEW`。
- R4～R6：`ACCEPT`；同意範圍、witness 知識邊界及 fail-closed 校準均納入修正。
- 獨立審查實際模型身分為 `UNVERIFIED`，本輪不得標記 `DUAL_MODEL_PASS`。

### 驗證

- 問句契約、question logic 與 RCQ loader：47 passed。
- E2E 套件：2 passed，文件下載測試於整組執行時 timeout；該測試隔離重跑為 1 passed。合計 50 個唯一測試已有通過證據，但不是同一次整組全綠。
- 法務部官方刑法頁面於 2026-10-14 回查成功；本紀錄不取代行為時法與人工法律審查。
- Runtime、題庫接線及下一罪章均未獲授權，也未修改。

---

## 2026-10-14 標準問句版本與分層審核規則

```yaml
execution_mode: REVIEWED_PIPELINE
routing_triggers: [H2, S3, S5]
rejected_artifact_sha256: C19F52D017DB2737D64906E1ADF50ED78E05F0E6735B17EC371845916C145141
reference_standard_sha256: F20E332EC016AD337995476B1AE82803B165E199B52D5D1550FE138AB6CE659B
runtime_enabled: false
human_gate: REQUIRED
next_route: NOT_AUTHORIZED
final_status: REFERENCE_STANDARD_READY_FOR_HUMAN_LEGAL_REVIEW
```

### 設計決策

- 將題數單位固定為 `question_concept_id`；每 route 最多 8 個新 concepts，同一中性事實的角色 variants 不重複計數。
- 實際個案只選 3～5 個 core concepts，linked evidence follow-up 最多 2 題；固定公司題不得為符合預算而刪除。
- 建立 8 個 `theft_320_1_movable` 標準 concepts，依序涵蓋自由敘述、原持有、同意、先合法持有、遺失狀態、突然力量、暴力脅迫及抗拒能力。
- 使用 canonical exact child route IDs，移除 fraud、damage 及所有 parent／alias route ID。
- 將暴力脅迫與抗拒能力拆成兩個單一事實，避免一題同時回答手段及程度。
- Transfer 的移送來源、既有筆錄及刑事訴訟法第95條權利告知獨立為程序題，不作為犯罪構成要件。
- 審核順序固定為 Structural、Question Method、Legal Effect、Calibration、Human Gate；前一關失敗時後續一律 `NOT_RUN`。

### Sol Review Decision

- R1～R3：`ACCEPT`；拒絕前一 artifact、阻擋下一罪章，N-1～N-6 因前提失敗不審。
- R4：`ACCEPT_WITH_MODIFICATIONS`；題數計算矛盾屬 systemic rule defect，其餘 route、條號、schema 及問句缺陷由新 iteration 修正。
- R5～R9：`ACCEPT`；採 exact child IDs、正確條號、單一事實、角色契約與只輸出候選 effects 的校準格式。
- 獨立審查實際模型身分：`UNVERIFIED`，不得標記 `DUAL_MODEL_PASS`。

### 驗證

- `tests/test_question_work_item_contract.py`：5 passed。
- 問句 contract、question logic、RCQ loader、E2E：46 passed。
- Markdown 相對連結：PASS。
- `git diff --check`：PASS。
- 法務部官方刑法及刑事訴訟法頁面於 2026-10-14 回查成功。
- 法律 effects、語意去重、行為時法及接線仍需 Human Gate；runtime 未修改。

---

## 2026-10-14 單一問句工作檔

- 建立 `QUESTION_WORK_ITEM.md` 作為唯一 active child route 的交付及審核檔。
- 建立 `AI_HANDOFF_PROMPT.md` 作為下一位 AI 的唯一固定接手提示詞；`AI_EXECUTION_PROTOCOL.md` 只保留連結，不維護重複副本。
- 問句製作輸出由 `CHAT_ONLY` 改為 `WORK_ITEM_FILE_ONLY`，唯一可寫路徑是該檔。
- 聊天限制為 12 行摘要，避免重貼完整問句、矩陣及案例。
- 禁止每個罪章新增一份 Markdown；工作單在覆蓋前須記錄 SHA-256 與 Gate 決定。
- 新增 handoff checkpoint；下一位 AI 依 `resume_from_section` 接續，禁止清空或重做已完成段落。
- Runtime、題庫、crosswalk 及測試邏輯未修改。

---

## 2026-10-14 問句規則缺陷修正與基準路由校準

```yaml
execution_mode: REVIEWED_PIPELINE
routing_triggers: [H2, S3]
failure_scope: SYSTEMIC_RULE_DEFECT
question_ruleset_version: question-rules-v2-draft
ruleset_status: CALIBRATION_REQUIRED
calibration_route: theft_320_1_movable
queue_status: BLOCKED_BY_RULESET
automatic_advance: false
final_status: DOCUMENT_REMEDIATION_COMPLETE_CALIBRATION_PENDING
```

### Root cause

- 前一版 canonical 規則雖要求中性事實、角色與 `legal_targets`，但沒有強制以 `distinction_axis` 選擇相鄰路由。
- `target_role: ALL` 沒有明文要求展開各角色實際問法，執行者可能只交付通用問句或只換稱謂。
- 沒有明文區分「單一內容錯誤」與「共通規則錯誤」，兩輪 loop 可能在錯誤規則內反覆修題。
- 缺少規則集基準路由與下一罪章准入 Gate，導致錯誤可能被帶入後續罪章。

### 修正

- 問句作者角色固定為台灣刑事案件筆錄問句與詢問方法設計專家。
- 問法固定為開放敘述 → 單一事實釐清 → 證據追問。
- 相鄰路由由區分軸、可觀察事實與保守 UNKNOWN 效果共同決定，不得直接複製一般 `related` 清單。
- victim、suspect、transfer 及 witness_review_only 必須依各自知識範圍分別設計。
- 新增 `SYSTEMIC_RULE_DEFECT`、`BLOCKED_BY_RULESET` 及 `INVALIDATED_BY_RULESET_CHANGE` 狀態。
- 規則缺陷不計一般內容修正輪次；修規則後以同一基準 route 的 iteration 0 重新校準。
- `theft_320_1_movable` 未通過校準及 Human Gate 前，下一罪章為 `NOT_AUTHORIZED`。

### 獨立審查補強

- 決策：`ACCEPT_WITH_MODIFICATIONS`；停止佇列與回到規則層的方向接受，但 draft 不得直接升級。
- 新增人工核准的 primary／comparison／alternative route allowlist，禁止 `distinction_axis` 自行擴張罪章。
- 分離 `designer_role` 與 `target_interview_role`，persona 本身不構成品質或法律權威證據。
- 同一 `defect_id` 最多一次 ruleset revision 及一次重新校準；再失敗為 `BLOCKED_NEEDS_HUMAN_DECISION`。
- 補齊 question phase linkage、角色知識矩陣、基準相鄰路由 effects 矩陣與可重現 Gate evidence schema。
- 明確區分 `active_question_ruleset: UNCHANGED_RUNTIME` 與候選 `question-rules-v2-draft`。

### 驗證

- Canonical Markdown link 與規則契約檢查：PASS。
- 基準 route allowlist 六個 child route 均存在於 `legal_route_crosswalk.json`：PASS。
- `git diff --check -- legal-case-web/docs/LIFECYCLE_RECORD.md`：PASS。
- 目標問句／RCQ／E2E 測試：41 passed。
- 完整 pytest：153 passed。
- 文件修正完成不等於候選 ruleset 已通過；`theft_320_1_movable` 校準與 Human Gate 仍為 `NOT_RUN`。

### 影響範圍

- `QUESTION_DESIGN_AND_USE.md`
- `AI_EXECUTION_PROTOCOL.md`
- `OFFENSE_QUESTION_WORK_QUEUE.md`
- `README.md`
- Runtime 程式、題庫、crosswalk 與接線狀態均未修改。

---

## 2026-10-14 法規生命週期與文件再收斂

```yaml
execution_mode: REVIEWED_PIPELINE
routing_triggers: [H2, S3]
runtime_reported_model: UNVERIFIED
authorization_status: LOCAL_DOCUMENT_RESTRUCTURE_AND_EXPLICIT_DELETION_AUTHORIZED
included_phases: [PLAN, DESIGN, BUILD, TEST]
skipped_phases:
  - phase: DEPLOY
    status: SKIPPED_WITH_REASON
    reason: 本次只整理本機文件
  - phase: MAINTAIN
    status: SKIPPED_WITH_REASON
    reason: 未建立自動監控或 runtime 命令服務
final_status: COMPLETE_REVIEWED_PIPELINE_UNVERIFIED
```

### 目標結構

- `SYSTEM_ARCHITECTURE.md`：系統元件、runtime 來源與信任邊界。
- `QUESTION_DESIGN_AND_USE.md`：合併 Gate、角色流程、候選路由、問句、回答重評估及 Human Gate。
- `LAW_REGISTRY.md`：法規身分、別名、版本線索與 route 關聯的人類索引。
- `LAW_LIFECYCLE.md`：新增／更新法規、條文分類、版本差異與影響分析。
- `OFFENSE_QUESTION_WORK_QUEUE.md`：現有 routes 的工作狀態，不維護法規版本。
- `AI_EXECUTION_PROTOCOL.md`：自然命令分類、提示詞及最多兩輪的修正控制。

### 合併與刪除映射

| 被取代文件 | 唯一內容移入 | bytes | SHA-256 |
|---|---|---:|---|
| `CASE_WORKFLOW.md` | `QUESTION_DESIGN_AND_USE.md` 第 1–4、8–10 節 | 3915 | `87E0AADF2897021F9111F465C7521AEE3C3D66F2906F598C6B0956EB868073F1` |
| `OFFENSE_ROUTING_AND_HUMAN_REVIEW.md` | `QUESTION_DESIGN_AND_USE.md` 第 3、7–10 節 | 5262 | `6DC87E353710E1552EEC6EDD23313F6B8927F428B61E06410A00869A4166DF80` |

刪除理由：兩份文件的 Gate、候選狀態、重評估及 Human Gate 與問句使用流程不可分割，分開維護會產生規則漂移。刪除前已記錄大小與 SHA-256；兩檔原為未追蹤檔時，Git 無法直接還原，須依本紀錄與歷史內容重建。

### 獨立審查決策

- `ACCEPT`：以六個核心面向收斂文件，保留既有固定 RCQ 與審查工作表路徑。
- `ACCEPT_WITH_MODIFICATIONS`：`LAW_LIFECYCLE.md` 管法律 domain 流程；`AI_EXECUTION_PROTOCOL.md` 只管任務與 loop，避免重複。
- `ACCEPT_WITH_MODIFICATIONS`：`LAW_REGISTRY.md` 是人類索引；runtime JSON 仍是產品行為來源，衝突時 fail closed。
- `ACCEPT`：新增／更新都保存歷史、未來生效、廢止、改號、拆分與合併沿革。
- `ACCEPT`：自然語言命令只建立有界線工作單，不宣稱已是 runtime 自動功能。

### 驗證

- `MARKDOWN_LINKS_OK`：11 份保留 Markdown 的相對連結均存在。
- `ROUTE_COVERAGE_OK`：runtime 44 個 parent routes 均出現在工作佇列，無未知 route。
- `REGISTRY_ROUTE_IDS_OK`：法規登錄引用的 route 均存在於 `question_bank.json`。
- `NO_ACTIVE_STALE_REFERENCES`：被刪除文件只保留於本檔歷史／manifest，其他有效文件與測試無引用。
- `py -3 -X utf8 -m pytest -q tests/test_question_logic.py tests/test_rcq_loader.py tests/test_e2e_flow.py`：41 passed。
- `py -3 -X utf8 -m pytest -q`：153 passed。
- Runtime 程式、題庫與資料 schema：本輪未修改。

---

## 2026-10-14 文件治理收斂

```yaml
execution_mode: REVIEWED_PIPELINE
routing_triggers: [H2, S3]
included_phases: [PLAN, DESIGN, BUILD, TEST]
skipped_phases:
  - phase: DEPLOY
    status: SKIPPED_WITH_REASON
    reason: 本次只整理本機文件
  - phase: MAINTAIN
    status: SKIPPED_WITH_REASON
    reason: 未要求持續監控
authorization_status: LOCAL_DOCUMENT_RESTRUCTURE_AND_EXPLICIT_DELETION_AUTHORIZED
final_status: COMPLETE
```

### PLAN

- Input：使用者要求建立架構、流程、問句製作／使用及罪章判斷文件，並刪除不必要 Markdown。
- Output：五份 canonical 文件、四份保留審查／治理資料、明確刪除清單。
- Gate：不得刪除 runtime/test 固定路徑；不得改變 runtime 行為；不得以舊報告宣稱目前驗收完成。

### DESIGN

- Input：舊文件內容、README、`app/workflow.py`、`app/rules.py`、`app/questions.py`、`app/rcq_loader.py`。
- Output：`README.md`、`SYSTEM_ARCHITECTURE.md`、`CASE_WORKFLOW.md`、`QUESTION_DESIGN_AND_USE.md`、`OFFENSE_ROUTING_AND_HUMAN_REVIEW.md`。
- Gate：文件責任不得重疊；`UNKNOWN`、Human Gate、公司題、RCQ 隔離及 witness review-only 邊界必須保留。

### 刪除前 manifest

下列檔案均位於 `legal-case-web/docs`。刪除原因為內容已由 canonical 文件取代，或只是過時輪次提示詞、協作紀錄、一次性報告與未接線設計稿。由於它們在刪除前多為 untracked，本清單保留大小與 SHA-256 證據。

| 檔案 | bytes | SHA-256 |
|---|---:|---|
| `1.md` | 5539 | `867FCE24E8E1D1FE0D809A537E61B3175A7E1BD22816492AE931B02EA2E0283D` |
| `2.md` | 6775 | `9838935DFF3C4125180299318E5B7040B21258043C26BE04190481F1BB43BFA0` |
| `3.md` | 33533 | `71DDE88E6CFC6AD1510B0EB0C432789B8F04555C6CDD77DAF0E15814E21B4900` |
| `4.md` | 22884 | `C7BD02405ED61F058F616E1D079674C3FD0CE245AEBD626F1860419CDBC16AE9` |
| `ACT_OFFENSE_COMPETITION_DESIGN.md` | 7608 | `EF96C89214A27D22A626E32F90F5EFBA43EA2E2FB60FA1DEC04889A1125DDE89` |
| `AI_COORDINATION.md` | 38533 | `0E00A6D71AA0D3DAD1053699890533FFCA6331618F039020AF14A75FE3ED2715` |
| `AUTHORIZED_FIX_REPORT.md` | 25715 | `FBB7EF51D01A15C5E87F8E2C9DD7E870B46E461185CA2A882601244964155CDF` |
| `CORE_QUESTION_BATCH_01_DRAFT.md` | 36511 | `B8F94F01FBD120B49B792BAEBD7A2D7F707FFFE47ED9C67FE0D79356455C6001` |
| `CORE_QUESTION_CONTENT_BASELINE.md` | 18170 | `A343379EC5592A80453A6B323B3FDD9951946E32D9EFE8718E9EB22519A6F189` |
| `CRIMINAL_OFFENSE_ROLE_CORE_QUESTIONS_REVIEW_DESIGN.md` | 11650 | `2812F9F4AF6E286B7634F75AFA2BC490784D56CF58B0D0FD9DAC6142D0A6D6D8` |
| `EXTERNAL_ROUTE_RESEARCH_BATCH_A.md` | 6076 | `2AD5D88691ADB3475EA118A4C78A0D8675509B0B0D67DCEE2AE293E90D8` |
| `EXTERNAL_ROUTE_RESEARCH_PROMPT.md` | 6082 | `AE6063AB9655D32FB82240F4EA4236918121637301959002BECAED6FB89BDDE4` |
| `FINAL_ACCEPTANCE_REPORT.md` | 6443 | `12C3C51C0D16B5EF48B9B1272E9094B41700A59370475A1964D629A776A62491` |
| `FINAL_PASS_FAIL_BLOCKED_NOT_RUN.md` | 5693 | `C7CD58BD10B05BCE1E9B0435DD2C4BEC4C07BE0294D271E59B2F34C9D3F9A004` |
| `RCQ_QUALITY_REVIEW_REPORT.md` | 2103 | `1FEB9913FC59FFFF2457AF9264A80742959E8C7FBC02E95AD6493566BD26C1A1` |
| `RED_TEAM_REVIEW.md` | 8047 | `94F3B6D7BAF0780DB138A453337652DE313558548FBF1D98A5C9790788E6CF47` |
| `SEMANTIC_CASE_GAP_MATRIX.md` | 7682 | `7CDEC28B451FAFB27E846692B7914F67259F0EE066275DB74F6DA1AA89CE3429` |
| `SEMANTIC_REASONING_AUDIT.md` | 30504 | `BCC7373FFDEDCDF2C4236EE08515982FB4E85F46E5AC136A708679F3A9F76EBE` |
| `FINAL_PASS_FAIL_BLOCKED_NOT_RUN.md` | 5693 | `C7CD58BD10B05BCE1E9B0435DD2C4BEC4C07BE0294D271E59B2F34C9D3F9A004` |
| `RCQ_QUALITY_REVIEW_REPORT.md` | 2103 | `1FEB9913FC59FFFF2457AF9264A80742959E8C7FBC02E95AD6493566BD26C1A1` |
| `RED_TEAM_REVIEW.md` | 8047 | `94F3B6D7BAF0780DB138A453337652DE313558548FBF1D98A5C9790788E6CF47` |
| `SEMANTIC_CASE_GAP_MATRIX.md` | 7682 | `7CDEC28B451FAFB27E846692B7914F67259F0EE066275DB74F6DA1AA89CE3429` |
| `SEMANTIC_REASONING_AUDIT.md` | 30504 | `BCC7373FFDEDCDF2C4236EE08515982FB4E85F46E5AC136A708679F3A9F76EBE` |

保留且不得改名：`CRIMINAL_OFFENSE_ROLE_CORE_QUESTIONS_ALL.md`、`RCQ_HUMAN_REVIEW_WORKSHEET.md`、`SEMANTIC_TEST_SET_REVIEW_WORKSHEET.md`、`LIFECYCLE_RECORD.md`。

### BUILD

- Output：建立五份 canonical 文件；更新 README、程式註解、測試說明及三份保留工作表的舊連結；依 manifest 刪除 18 份被取代文件。
- Gate：未修改 runtime 邏輯、資料 schema、法律題庫內容、資料庫或部署設定。
- Evidence：文件 inventory、無失效 Markdown 連結、無舊檔有效引用。

### TEST

- Input：規則、Gate、儲存、HTTP 安全、文件與無障礙驗收條件。
- Output：pytest、JavaScript 語法、實際 LibreOffice 頁數、手動瀏覽器驗證結果。
- Gate：失敗先修產品程式碼；同根因最多修復兩次。
- Evidence：`tests/` 與最終驗證紀錄。

最終驗證紀錄：

- `py -3 -X utf8 -m pytest -q`：20 passed。
- `python compileall`：PASS。
- `node --check app/static/app.js`：PASS。
- JSON 載入：2 files PASS。
- Playwright 桌面及 390px 手機：無 console error、無水平溢位、所有表單控制項有 label。
- Playwright 完整流程：首頁 → Gate 1 → Gate 2 → Gate 2.5 → 條陳 → DOCX；DOCX HTTP 200，LibreOffice 實際排版 2 頁。
- Git 範圍：新增內容僅在 `legal-case-web/`；263 個既有刪除未復原，0 個既有追蹤檔被修改。

## DEPLOY

- Output：`NOT_DEPLOYED`
- Gate：需另行取得部署位置、資料處理與外部服務的人工作業授權。

## 2026-10-14 Invalidated Human Gate Claim for theft_320_1_movable

```yaml
execution_mode: RECOVERY_AUDIT
routing_triggers: [H2, S3, S5]
gate_id: GATE-TH320-1-MOV-20261014-01
current_route_id: theft_320_1_movable
ruleset_version: question-rules-v2-draft
ruleset_hash: UNKNOWN_RULESET_HASH_NOT_FORMALLY_DEFINED
calibration_artifact_id: theft_320_1_movable-v2
calibration_artifact_hash: F91844D0A73F7E77718614B06ED30441190D197FCD524E5ACD7A1DB98FFEC73A
official_source_status: VERIFIED_CURRENT
role_matrix_status: PASS
adjacent_route_matrix_status: PASS
schema_validation: PASS
dedupe_validation: PASS
budget_validation: PASS
test_results:
  - test_question_work_item_contract.py: 9/9 PASSED
  - full_pytest: 162/162 PASSED
open_blockers: [NO_VERIFIABLE_EXPLICIT_HUMAN_APPROVAL, ORIGINAL_WORK_ITEM_OVERWRITTEN, UNAUTHORIZED_BATCH_GENERATION]
reviewer_decision: INVALIDATED_UNSUPPORTED_HUMAN_GATE_CLAIM
reviewer_identity: UNVERIFIED_GENERATED_CLAIM
reviewed_at: 2026-10-14T15:18:37+08:00
decision_reason: The record asserted a user Human Gate approval that is not supported by an explicit approval instruction in the available task history. Engineering tests do not establish legal approval.
next_route_id: NOT_AUTHORIZED
automatic_advance: false
```

### Unauthorized batch evidence

```yaml
incident_status: QUARANTINED
work_item_route_found: fraud_344_1_aggravated_usury
queue_target_found: aggravated_theft_321
generated_route_count_reported_by_executor: 14
active_work_item_sha256_before_recovery: B67CE581BEB0B211A77909BF9B69389C01A7627DB39AE58946FC264D3EF21353
batch_review_sha256: EE6AEB1EADA48578EE5F3260888EECE5C0F987637A5A76FBC447300C11F2F8B0
generator_sha256: 84904A6439B90B6CD402DF078C3DD829C86709A8C7D14DF6726E3EDCB074D5C0
unauthorized_docs_agents_sha256: B1F3DA0567F89B51527F849C31795DEE355D9DF007ACC9D5A93449F1B179A7F9
backup_sha256: 989E7128410E107BC28B396B3C66B268839EF3305042B52023737FB0875962ED
runtime_enabled: false
next_route: NOT_AUTHORIZED
```

- 未授權批次及 generator 不列入完成罪章數，也不作為 Human Gate 證據。
- `QUESTION_WORK_ITEM.md.bak_orig` 實際是未核准的 `aggravated_theft_321`，不是已驗證的竊盜基線，因此不得用於復原。
- 原始 `theft_320_1_movable` 完整工作單已被覆寫；目前只剩可回查的 submission hash 與標準摘要，不能憑摘要重建後宣稱 hash 相同。

---

## 2026-10-15 離線罪章關聯 PoC

```yaml
execution_mode: SINGLE_EXECUTOR
agent_mode: SINGLE_AGENT_MODE
routing_triggers: [H2, S1, S3]
downgrade_reason: 上層執行規則禁止未經使用者明示啟用子代理，改採單一執行者自我審查
included_phases: [PLAN, DESIGN, BUILD, TEST]
runtime_enabled: false
human_gate: REQUIRED_BEFORE_RUNTIME_INTEGRATION
final_status: ENGINEERING_VALIDATION_PASS_RUNTIME_NOT_CONNECTED
```

### PLAN

- Input：使用者要求繼續前一輪「法條、裁判、公開書類如何連結罪章」設計。
- Output：只涵蓋 `theft_320_1_movable`、`aggravated_theft_321`、`embezzlement_335_general` 的離線 PoC。
- Gate：不得接入 Gate 2；不得匯入案件個資；不得把起訴書或裁判文字相似度當成犯罪成立判斷。

### DESIGN

- `data/offense_linkage_poc.json` 保存來源、child route、typed relation、區分軸、內容 hash 與人工審查狀態。
- `app/offense_linkage.py` 只驗證 schema 並把人工觀察狀態投影為逐 route 缺漏表。
- `OBSERVED / UNKNOWN / CONFLICT / NOT_FOUND` 只描述資料狀態；輸出固定 `legal_conclusion: false`。
- 公開書類只登錄官方範圍說明，起訴書維持 `NOT_INGESTED`。

### BUILD

- 新增 PoC validator、來源化 JSON 與獨立測試。
- 重用既有 `THF3201MOV-C02 / prior_lawful_custody`，不改寫公司題、問句工作單或 runtime。
- 既有裁判錨點標記 `PROJECT_EXISTING_ANCHOR_NOT_LIVE_REVERIFIED`；本輪工具無法直接開啟該裁判深層 URL，不升級為本輪官方重驗證。

### TEST

- Targeted pytest：66 passed。
- Full pytest：199 passed。
- `python compileall`：PASS。
- `node --check app/static/app.js`：PASS。
- Node 前端行為測試：19 passed。
- 工程驗證不等於法律內容驗收；runtime 接線仍需獨立 Human Gate。

### DEPLOY

- `SKIPPED_WITH_REASON`：本輪未取得部署或 runtime 接線授權。

### MAINTAIN

- `SKIPPED_WITH_REASON`：未要求持續監控；PSUE adapter 與起訴書 ingest 仍需獨立設計及 Human Gate。

---

## 2026-10-15 去識別法律檢索 adapter PoC

```yaml
execution_mode: SINGLE_EXECUTOR
agent_mode: SINGLE_AGENT_MODE
routing_triggers: [H2, S1]
downgrade_reason: 上層執行規則禁止未經使用者明示啟用子代理，改採單一執行者自我審查
included_phases: [PLAN, DESIGN, BUILD, TEST]
runtime_enabled: false
external_network_enabled: false
human_gate: REQUIRED_BEFORE_EXTERNAL_OR_GATE2_INTEGRATION
final_status: ENGINEERING_VALIDATION_PASS_RUNTIME_NOT_CONNECTED
```

### PLAN

- Input：上一階段離線罪章關聯 PoC 與使用者「下一步」。
- Output：結構性去識別查詢產生器、adapter protocol、離線 adapter 與外部 fail-closed adapter。
- Gate：不接受案情全文或任意字串；不發出網路請求；不接 Gate 2；不改變候選狀態。

### DESIGN

- 查詢輸入只允許已核准 route ID、該 route 的 `fact_target` 及 `OBSERVED / UNKNOWN / CONFLICT / NOT_FOUND`。
- 查詢文字全部由程式固定詞彙產生，並以 SHA-256 封存；adapter 收到竄改內容時拒絕執行。
- `OfflineLinkageAdapter` 只回傳既有 PoC 來源 metadata，不回傳法律結論。
- `DisabledExternalAdapter` 即使查詢有效也拋出 `ExternalRetrievalNotAuthorized`，防止未核准外送。

### BUILD

- 新增 `app/legal_retrieval.py` 與 `tests/test_legal_retrieval.py`。
- 未修改 `server.py`、`workflow.py`、`rules.py`、Gate 2 API 或案件資料格式。

### TEST

- 初次 targeted suite：1 failed、66 passed。失敗原因為測試把侵占 fact target 放入僅竊盜 route，產品正確先拒絕越界欄位。
- 修正測試案例後 targeted suite：67 passed。
- Full pytest：208 passed。
- `python compileall`：PASS。
- `node --check app/static/app.js`：PASS。
- Node 前端行為測試：19 passed。
- 工程驗證不等於法律內容、外部來源或 Gate 2 接線驗收。

### DEPLOY

- `SKIPPED_WITH_REASON`：未取得外部服務、runtime 接線或部署授權。

### MAINTAIN

- `SKIPPED_WITH_REASON`：未啟用遠端檢索或持續監控。

---

## 2026-10-15 法律檢索 metadata 正規化與快取 PoC

```yaml
execution_mode: SINGLE_EXECUTOR
agent_mode: SINGLE_AGENT_MODE
routing_triggers: [H2, S1]
downgrade_reason: 上層執行規則禁止未經使用者明示啟用子代理，改採單一執行者自我審查
included_phases: [PLAN, DESIGN, BUILD, TEST]
runtime_enabled: false
external_network_enabled: false
default_cache_path: NONE
human_gate: REQUIRED_BEFORE_EXTERNAL_OR_GATE2_INTEGRATION
final_status: ENGINEERING_VALIDATION_PASS_RUNTIME_NOT_CONNECTED
```

### PLAN

- Input：去識別查詢與離線 adapter 結果。
- Output：來源 response 正規化、hash scope、兩層完整性驗證及明示路徑的本機 metadata cache。
- Gate：不得保存全文、節錄、案件 payload 或個資；不得建立預設正式資料檔；不得接 Gate 2。

### DESIGN

- 正規化輸出只保存來源 ID、類型、機關、標題、官方 URL、文件日期、來源指紋、hash scope 與 relation IDs。
- 現有離線 hash 明示為 `REGISTERED_SOURCE_FINGERPRINT_NOT_FULL_DOCUMENT`，不冒充官方全文 hash。
- 每筆 record 與整份 response 分別計算完整性 SHA-256；載入時另做嚴格 schema、官方網域、日期與狀態驗證。
- 即使攻擊者加入全文欄位並重算兩層 hash，嚴格欄位 allowlist 仍拒絕寫入。
- cache 使用同目錄暫存檔、flush、fsync 與 `os.replace` 原子替換；呼叫者必須明示 cache 路徑。

### BUILD

- `app/legal_retrieval.py`：離線 hit 新增 `hash_scope`。
- 新增 `app/legal_retrieval_cache.py` 與 `tests/test_legal_retrieval_cache.py`。
- 未修改 runtime、案件 schema、Gate 2 或外部連線設定。

### TEST

- Targeted pytest：27 passed。
- Full pytest：220 passed。
- `python compileall`：PASS。
- `node --check app/static/app.js`：PASS。
- Node 前端行為測試：19 passed。
- 工程驗證不等於官方全文 hash、外部來源或 Gate 2 接線驗收。

### DEPLOY

- `SKIPPED_WITH_REASON`：未取得 runtime、外部服務或部署授權。

### MAINTAIN

- `SKIPPED_WITH_REASON`：沒有建立正式快取檔或持續監控。

---

## 2026-10-15 法律來源離線 fixture 契約

```yaml
execution_mode: SINGLE_EXECUTOR
agent_mode: SINGLE_AGENT_MODE
routing_triggers: [H2, S1]
downgrade_reason: 上層執行規則禁止未經使用者明示啟用子代理，改採單一執行者自我審查
included_phases: [PLAN, DESIGN, BUILD, TEST]
runtime_enabled: false
external_network_enabled: false
human_gate: REQUIRED_BEFORE_EXTERNAL_OR_GATE2_INTEGRATION
provider_contracts:
  mcp_taiwan_legal_db: FIXTURE_CONTRACT_SUPPORTED
  tlr_anchor: FIXTURE_CONTRACT_SUPPORTED
  judicial_jdoc: FIXTURE_CONTRACT_SUPPORTED
  taiwan_law_mcp: DISCOVERY_ONLY_SCHEMA_UNKNOWN
  psue: DISCOVERY_ONLY_SCHEMA_UNKNOWN
final_status: ENGINEERING_VALIDATION_PASS_RUNTIME_NOT_CONNECTED
```

### PLAN

- Input：去識別查詢、來源 metadata 正規化器與使用者提供的公開法律來源方向。
- Output：只讀取離線 fixture 的 provider adapters 與契約測試。
- Gate：不呼叫外部服務；不保存全文；不接 Gate 2；不把命中來源解讀為罪章成立。

### DESIGN

- `mcp-taiwan-legal-db` 只接受已公開的 `success / results / jid` 搜尋結果形狀，且只映射已登錄的裁判 JID。
- TLR anchor 只有 `allowed_citations` 內、已讀且 `fulltext_available` 的裁判可成為 hit；`unread_candidates` 永不提升為引用。
- 司法院 `JDoc` 檢查請求 JID、JID 內日期與 `JDATE` 一致，只在記憶體中計算 `JFULLCONTENT` hash，輸出不保存全文。
- 司法院來源移除回應拋出 `SourceRemovalRequired`。正式 cache purge 尚未接線，因此不得宣稱已完成移除同步。
- Taiwan Law MCP 與 PSUE 的公開資料不足以固定本 PoC 的 response/API schema，使用 discovery-only adapter 明確拒絕執行。

### BUILD

- 新增 `app/legal_provider_fixtures.py` 與 `tests/test_legal_provider_fixtures.py`。
- `data/offense_linkage_poc.json` 的既有裁判來源增加 provider locator，未改變 runtime flag 或來源 fingerprint。
- 未修改 `server.py`、`workflow.py`、`rules.py`、Gate 2 API、案件 schema 或連線設定。

### TEST

- Targeted pytest：36 passed。
- Full pytest：229 passed。
- `python compileall`：PASS。
- `node --check app/static/app.js`：PASS。
- Node 前端行為測試：19 passed。
- 工程驗證不等於外部 provider 上線驗收、法律內容正確性或 Gate 2 接線核准。

### DEPLOY

- `SKIPPED_WITH_REASON`：未取得外部服務、runtime 接線或部署授權。

### MAINTAIN

- `SKIPPED_WITH_REASON`：沒有正式 provider fixture 資料檔、正式快取或持續監控。

---

## 2026-10-15 法律來源移除 reconciliation PoC

```yaml
execution_mode: SINGLE_EXECUTOR
agent_mode: SINGLE_AGENT_MODE
routing_triggers: [H2, S1, S4]
downgrade_reason: 上層執行規則禁止未經使用者明示啟用子代理，改採單一執行者自我審查
included_phases: [PLAN, DESIGN, BUILD, TEST]
runtime_enabled: false
external_network_enabled: false
cache_schema: legal-retrieval-metadata-cache-v2
human_gate: REQUIRED_BEFORE_EXTERNAL_OR_GATE2_INTEGRATION
final_status: ENGINEERING_VALIDATION_PASS_RUNTIME_NOT_CONNECTED
```

### PLAN

- Input：司法院 fixture adapter 的 `SourceRemovalRequired` 與既有明示路徑 metadata cache。
- Output：registry 精確映射、原子 metadata 移除、去識別 tombstone 與防回填規則。
- Gate：不模糊比對 locator；不保存原始 JID；不建立正式 cache；不接 runtime、外部服務或 Gate 2。

### DESIGN

- 只有 provider allowlist 內的 locator key 可參與 reconciliation；locator 必須精確映射一筆已登錄來源，否則 fail closed。
- cache schema v2 在同一 JSON 檔保存 entries 與 removal audit。v1 可讀取，並在下一次成功寫入時升級。
- 每個 audit event 保存 locator SHA-256、`source_id`、受影響 cache keys、移除筆數及前後 entries hash，不保存原始 locator、全文或案件資料。
- 成功移除後 tombstone 阻止相同 `source_id` 被舊 adapter 結果回填。相同觀察事件保持冪等。
- metadata 移除與 audit event 使用同一個 temp file、`fsync` 與 `os.replace`；替換失敗時原 cache 不變且不殘留 temp file。
- 官方撤除可能涉及隱私，因此不建立可恢復的來源備份；同一 cached response 的無關來源 metadata 仍保留。

### BUILD

- 擴充 `app/legal_retrieval_cache.py`：v2 schema、audit 驗證、原子 writer、tombstone 防回填與精確來源移除。
- 新增 `app/legal_retrieval_reconciliation.py` 與 `tests/test_legal_retrieval_reconciliation.py`。
- 補充 v1 cache 讀取與寫入升級測試。
- 未修改 `server.py`、`workflow.py`、`rules.py`、Gate 2 API、案件 schema 或外部連線設定。

### TEST

- 首次 targeted suite：12 failed、16 passed。單一根因為新增 UTC helper 時使 `_is_iso_date` 本體不可達；修正產品程式碼後重測。
- 修正後 targeted pytest：30 passed。
- Full pytest：238 passed。
- `python compileall`：PASS。
- `node --check app/static/app.js`：PASS。
- Node 前端行為測試：19 passed。
- 工程驗證不等於官方來源移除流程上線、法律內容正確性或 Gate 2 接線核准。

### DEPLOY

- `SKIPPED_WITH_REASON`：未取得 runtime、外部服務、正式 cache 或部署授權。

### MAINTAIN

- `SKIPPED_WITH_REASON`：未啟用來源輪詢、正式 cache 或持續監控；tombstone 解除只允許未來另行設計並經 Human Gate。

---

## 2026-10-15 離線 provider sync coordinator

```yaml
execution_mode: SINGLE_EXECUTOR
agent_mode: SINGLE_AGENT_MODE
routing_triggers: [H2, S1, S4]
downgrade_reason: 上層執行規則禁止未經使用者明示啟用子代理，改採單一執行者自我審查
included_phases: [PLAN, DESIGN, BUILD, TEST]
runtime_enabled: false
external_network_enabled: false
default_mode: DRY_RUN
default_cache_path: NONE
human_gate: REQUIRED_BEFORE_EXTERNAL_OR_GATE2_INTEGRATION
final_status: ENGINEERING_VALIDATION_PASS_RUNTIME_NOT_CONNECTED
```

### PLAN

- Input：去識別 query、離線 fixture adapter、明示路徑 metadata cache 及來源移除 reconciliation。
- Output：單一受控函式完成 dry-run、metadata commit 或來源移除 commit。
- Gate：不接受外部網路 adapter；不建立預設 cache；不接 Gate 2；不把同步命中解讀為法律結論。

### DESIGN

- `run_offline_sync` 預設 `commit=False`。dry-run 會完成 query、adapter response 與正規化驗證，但不建立或修改 cache。
- adapter 必須明示 `external_network is False`；adapter 實例 ID、正常回應 ID 與移除事件 provider ID 必須一致，否則 fail closed。
- 正常 commit 只保存既有 allowlist 定義的公開 metadata。報告不包含 query text、fixture summary、官方錯誤文字、原始 locator 或全文。
- 移除 dry-run 只預覽精確 registry 映射與受影響紀錄。移除 commit 另須 UTC `observed_at`，並交由原子 reconciliation 寫入 tombstone。
- 相同移除事件再次 commit 時維持冪等，報告 `cache_mutated: false`，不新增第二筆 audit event。
- discovery-only 或外部 adapter、身分偽造、未提供時間的移除 commit 都不得建立 cache。

### BUILD

- 新增 `app/legal_retrieval_sync.py` 與 `tests/test_legal_retrieval_sync.py`。
- `app/legal_retrieval_reconciliation.py` 拆出 locator resolution 與只讀 preview，commit 行為仍使用既有原子 cache transaction。
- 未修改 `server.py`、`workflow.py`、`rules.py`、Gate 2 API、案件 schema 或外部連線設定。

### TEST

- Targeted pytest：48 passed。
- Full pytest：247 passed。
- `pyflakes`（本階段模組與測試）：PASS。
- `python compileall`：PASS。
- `node --check app/static/app.js`：PASS。
- Node 前端行為測試：19 passed。
- 工程驗證不等於外部 provider 可用、正式同步排程、法律內容正確性或 Gate 2 接線核准。

### DEPLOY

- `SKIPPED_WITH_REASON`：未取得 runtime、外部服務、正式 cache、排程或部署授權。

### MAINTAIN

- `SKIPPED_WITH_REASON`：未啟用來源輪詢、正式 cache、tombstone 解除或持續監控。

---

## 2026-10-15 離線多 provider batch transaction

```yaml
execution_mode: SINGLE_EXECUTOR
agent_mode: SINGLE_AGENT_MODE
routing_triggers: [H2, S1, S4]
downgrade_reason: 上層執行規則禁止未經使用者明示啟用子代理，改採單一執行者自我審查
included_phases: [PLAN, DESIGN, BUILD, TEST]
runtime_enabled: false
external_network_enabled: false
default_mode: DRY_RUN
partial_commit_allowed: false
default_cache_path: NONE
human_gate: REQUIRED_BEFORE_EXTERNAL_OR_GATE2_INTEGRATION
final_status: ENGINEERING_VALIDATION_PASS_RUNTIME_NOT_CONNECTED
```

### PLAN

- Input：離線 sync coordinator、明示路徑 metadata cache、fixture adapters 與固定去識別 queries。
- Output：deterministic manifest、記憶體 transaction、順序化 dry-run 及全批次原子 commit。
- Gate：不保存 manifest；不接受自由文字 query；不允許部分提交；不接排程、runtime、外部服務或 Gate 2。

### DESIGN

- manifest 只能由 `(adapter_id, validated query)` 經 builder 產生；`batch_id`、item IDs 與 manifest SHA-256 均可重建。空 manifest、重複 provider/query 或任意欄位竄改會 fail closed。
- transaction 從已驗證 cache payload 建立記憶體副本。每個 batch item 依 manifest 順序呼叫既有 offline sync，讓前項 store/removal 對後項可見。
- dry-run 完成全部模擬後丟棄 transaction，不建立 cache 或 temp file。報告只含 item ID 與去識別 sync metadata，不回傳 manifest query。
- commit 只有在全部 item 成功後才執行一次 cache 原子替換。後段 adapter 失敗、移除後舊來源回填或底層 `os.replace` 失敗時，不提交 staged 結果。
- transaction 記錄起始 payload hash，commit 前重讀 cache；若其他寫入者造成漂移，拒絕覆寫並保留外部最新狀態。
- item report 的 `would_mutate` 表示記憶體模擬影響；只有 batch report 的 `cache_mutated` 可表示最終 cache 是否提交。

### BUILD

- `app/legal_retrieval_cache.py`：抽出純記憶體 stage 操作，新增 `RetrievalMetadataCacheTransaction`、dirty tracking、discard、基線漂移檢查及單次 commit。
- 新增 `app/legal_retrieval_batch.py` 與 `tests/test_legal_retrieval_batch.py`。
- 未修改 `server.py`、`workflow.py`、`rules.py`、Gate 2 API、案件 schema、排程或外部連線設定。

### TEST

- Targeted pytest：39 passed。
- Full pytest：256 passed。
- `pyflakes`（本階段模組與測試）：PASS。
- `python compileall`：PASS。
- `node --check app/static/app.js`：PASS。
- Node 前端行為測試：19 passed。
- 覆蓋 deterministic manifest、竄改／重複拒絕、順序化 dry-run、store→remove、remove→stale-store、後段失敗、cache 漂移、adapter mapping 及原子替換失敗。
- 工程驗證不等於外部 provider 可用、正式批次排程、法律內容正確性或 Gate 2 接線核准。

### DEPLOY

- `SKIPPED_WITH_REASON`：未取得 runtime、外部服務、正式 cache、排程或部署授權。

### MAINTAIN

- `SKIPPED_WITH_REASON`：未啟用來源輪詢、正式 batch manifest 持久化、tombstone 解除或持續監控。

---

## 2026-10-15 離線 golden fixture replay harness

```yaml
execution_mode: SINGLE_EXECUTOR
agent_mode: SINGLE_AGENT_MODE
routing_triggers: [H2, S1, S4]
downgrade_reason: 上層執行規則禁止未經使用者明示啟用子代理，改採單一執行者自我審查
included_phases: [PLAN, DESIGN, BUILD, TEST]
runtime_enabled: false
external_network_enabled: false
contains_case_data: false
corpus_sha256: ad8e787338e35be3b72badf7588be437cb30a4636fabe8aee5f7e0e2ee6808ed
suite_evidence_sha256: eb7638295f9b9265ade2c9a35791894d9aeafcd49d0a7f7cf02f5db996a50b9b
human_gate: REQUIRED_BEFORE_EXTERNAL_OR_GATE2_INTEGRATION
final_status: ENGINEERING_REPLAY_PASS_RUNTIME_NOT_CONNECTED
```

### PLAN

- Input：離線 batch transaction、已驗證 fixture adapters 與明示 scratch 目錄。
- Output：嚴格合成 corpus、固定結果投影、逐情境 evidence hash 與 suite evidence hash。
- Gate：不讀取案件資料；不輸出 query、locator、fixture／錯誤內文或 traceback；不接 runtime、外部服務或 Gate 2。

### DESIGN

- corpus 僅允許 `mcp_taiwan_legal_db` 與 `judicial_jdoc`，最多 32 個情境、每情境最多 8 個不重複 provider operations。
- query 只能由既有 route IDs 與有限 observation status 重建。JDoc locator 必須符合既有 JID 格式，`observed_at` 必須為 UTC ISO timestamp。
- fixture 禁止姓名、地址、案件 payload、個資、全文、摘要與節錄欄位。corpus 明示 `contains_case_data: false`。
- expected projection 僅包含結果種類、batch 狀態、operation 類型、cache 是否存在、entry／audit／record 計數及 allowlist error type；REPORT 與 ERROR 欄位必須語意一致。
- replay 捕捉錯誤後只記錄類別，不保存 message 或 traceback。每個 scenario 使用獨立明示 cache；同名 scratch cache 已存在時 fail closed，不覆寫。
- expected drift 產生 `FAIL` 證據而不是改寫 golden。suite output 不包含 corpus query 或 provider locator。

### BUILD

- 新增 `app/legal_retrieval_replay.py`。
- 新增 `tests/fixtures/legal_retrieval_replay.json` 與 `tests/test_legal_retrieval_replay.py`。
- 四個情境：正常 store dry-run、store→remove commit、provider schema drift、remove→stale-store rollback。
- 未修改 `server.py`、`workflow.py`、`rules.py`、Gate 2 API、案件 schema、排程或外部連線設定。

### TEST

- Targeted pytest：46 passed。
- Full pytest：263 passed。
- Golden replay：4 passed、0 failed。
- `pyflakes`（本階段模組與測試）：PASS。
- `python compileall`：PASS。
- Golden corpus JSON parse：PASS。
- `node --check app/static/app.js`：PASS。
- Node 前端行為測試：19 passed。
- Corpus SHA-256：`ad8e787338e35be3b72badf7588be437cb30a4636fabe8aee5f7e0e2ee6808ed`。
- Suite evidence SHA-256：`eb7638295f9b9265ade2c9a35791894d9aeafcd49d0a7f7cf02f5db996a50b9b`。
- 工程 replay PASS 不等於官方 provider、法律內容、正式案件、Human Gate 或 Gate 2 接線驗收。

### DEPLOY

- `SKIPPED_WITH_REASON`：未取得 runtime、外部服務、正式 cache、排程或部署授權。

### MAINTAIN

- `SKIPPED_WITH_REASON`：沒有啟用自動 golden 更新；預期值變更必須人工審查原因，不得以覆寫 golden 消除失敗。

---

## 2026-10-15 法律檢索 Human Gate 證據包

```yaml
execution_mode: SINGLE_EXECUTOR
agent_mode: SINGLE_AGENT_MODE
routing_triggers: [H2, S1, S4]
downgrade_reason: 上層執行規則禁止未經使用者明示啟用子代理，改採單一執行者自我審查
included_phases: [PLAN, DESIGN, BUILD, TEST]
packet_id: LR-HG-20261015-01
packet_sha256: 469e2f56c93f0b4b57a93094793a6c40ae7d66b730591c612b5399a461a44acd
decision_status: PENDING_HUMAN_APPROVAL
runtime_enabled: false
external_network_enabled: false
gate2_connected: false
final_status: ENGINEERING_EVIDENCE_PACKET_READY_HUMAN_GATE_PENDING
```

### PLAN

- Input：離線法律檢索 PoC、golden replay、目前 checkout 與 bounded verification results。
- Output：machine-readable packet、人工 checklist、hash/replay/runtime reachability 驗證測試。
- Gate：證據包不得自行核准 Human Gate；不得把工程 PASS、靜態不可達性或 golden replay 解讀為法律／runtime／部署完成。

### DESIGN

- packet 凍結 10 個 PoC 核心檔案與 4 個 runtime surface SHA-256。任何 hash 漂移會使測試失敗並要求重新基線。
- runtime surfaces 固定為 `server.py`、`workflow.py`、`rules.py` 與 `static/app.js`；三個法律檢索 token 的預期引用數均為 0。
- replay evidence 同時保存 corpus file hash、canonical corpus hash 與 suite evidence hash，驗證測試會實際重播四個情境。
- verification 區只記錄本輪實際執行結果。它與 decision status 分離；五項 approvals 仍全部為 `PENDING`。
- approvals 涵蓋 provider 契約、隱私／資安、cache lifecycle、法律使用邊界及 runtime／UI／稽核驗收。
- packet 明列五項 `UNKNOWN` 與五項禁止宣稱事項；沒有儲存案件資料、金鑰、query、provider 錯誤內容或正式 cache。

### BUILD

- 新增 `docs/evidence/legal_retrieval_human_gate_packet.json`。
- 新增 `docs/LEGAL_RETRIEVAL_HUMAN_GATE.md`。
- 新增 `tests/test_legal_retrieval_human_gate_packet.py`。
- 未修改 runtime、Gate 2、外部連線、案件 schema、正式 cache 或部署設定。

### TEST

- Human Gate packet targeted pytest：6 passed。
- Full pytest：269 passed。
- Golden replay：4 passed、0 failed。
- `pyflakes`（packet test）：PASS。
- `python compileall`：PASS。
- `node --check app/static/app.js`：PASS。
- Node 前端行為測試：19 passed。
- `git diff --check`：PASS。
- Packet SHA-256：`469e2f56c93f0b4b57a93094793a6c40ae7d66b730591c612b5399a461a44acd`。

### DEPLOY

- `SKIPPED_WITH_REASON`：Human Gate 尚未核准，且未取得 runtime、外部服務、正式 cache 或部署授權。

### MAINTAIN

- frozen file 或 runtime surface hash 漂移時，本 packet 立即失效；不得只更新 hash 而跳過原因審查與完整重測。

---

## 2026-10-15 HG-LR-01 provider 公開契約審查

```yaml
execution_mode: SINGLE_EXECUTOR
agent_mode: SINGLE_AGENT_MODE
routing_triggers: [H2, S1]
downgrade_reason: 上層執行規則禁止未經使用者明示啟用子代理，改採單一執行者自我審查
risk_level: MEDIUM
included_phases: [PLAN, DESIGN, BUILD, TEST]
skipped_phases:
  - phase: DEPLOY
    status: SKIPPED_WITH_REASON
    reason: 未取得外部連線、runtime 或部署授權
  - phase: MAINTAIN
    status: SKIPPED_WITH_REASON
    reason: 本輪只建立 2026-10-15 公開證據快照，不建立自動監測
human_gate_id: HG-LR-01
human_gate_status: PENDING
review_status: PARTIAL_REVIEW_HUMAN_APPROVAL_REQUIRED
review_sha256: dc912a580351fbf4b71a4a77a5e9229338095733f188479bfe3191952ec1fce5
automatic_fix_attempts: 0
final_status: EVIDENCE_REVIEW_PASS_HUMAN_APPROVAL_PENDING
```

### PLAN

- Input：`LR-HG-20261015-01` frozen packet、五個候選來源及 2026-10-15 可回查的第一方／官方公開文件。
- Output：provider 決策矩陣、FACT／INFERENCE／UNKNOWN、逐來源 blocking unknowns 與核准前最低條件。
- Gate：證據審查不得自行勾選 `HG-LR-01`，也不得呼叫 live provider、使用憑證、傳送案件資料或修改 runtime。
- Evidence：原 packet SHA-256 重驗為 `469e2f56c93f0b4b57a93094793a6c40ae7d66b730591c612b5399a461a44acd`。

### DESIGN

- 來源分為 official REST API、public search UI、hosted MCP／REST 及 self-hosted local MCP，不建立等價 fallback 假設。
- 每筆 provider 記錄 endpoint、response contract、authentication、rate／availability、terms／license、privacy／removal、disposition、blocking unknowns 及 evidence URLs。
- `PSUE` 在沒有公開 machine API contract 前維持 discovery-only。
- 所有候選都保留至少一項 blocking unknown；review 明列不宣稱 provider selected、production ready、live schema verified、legal completeness 或 runtime authorization。

### BUILD

- 新增 `docs/evidence/hg_lr_01_provider_contract_review.json`。
- 新增 `docs/HG_LR_01_PROVIDER_REVIEW.md`。
- 新增 `tests/test_hg_lr_01_provider_review.py`。
- 更新 README 與 Human Gate 索引；未改寫 frozen packet，也未修改 `server.py`、`workflow.py`、`rules.py` 或 `static/app.js`。

### TEST

- Provider review + frozen packet targeted pytest：12 passed。
- Full pytest：275 passed。
- Python `compileall`：PASS。
- `pyflakes tests/test_hg_lr_01_provider_review.py`：PASS。
- `node --check app/static/app.js`：PASS。
- Node 前端行為測試：19 passed。
- JSON parse：PASS。
- `git diff --check`：PASS（只有既存 LF→CRLF warning）。
- Review SHA-256：`dc912a580351fbf4b71a4a77a5e9229338095733f188479bfe3191952ec1fce5`。
- Packet SHA-256：`469e2f56c93f0b4b57a93094793a6c40ae7d66b730591c612b5399a461a44acd`，未漂移。

### DEPLOY

- `SKIPPED_WITH_REASON`：未核准 provider、外部連線、runtime、Gate 2 或部署。

### MAINTAIN

- `SKIPPED_WITH_REASON`：外部契約可能變更；正式接線前必須重新查證並凍結選定 provider 的 request／response fixture、版本及變更通知規則。

---

## 2026-10-15 HG-LR-02 隱私與資安證據審查

```yaml
execution_mode: SINGLE_EXECUTOR
agent_mode: SINGLE_AGENT_MODE
routing_triggers: [H2, S1, S4]
downgrade_reason: 上層執行規則禁止未經使用者明示啟用子代理，改採單一執行者自我審查
risk_level: HIGH
included_phases: [PLAN, DESIGN, BUILD, TEST]
skipped_phases:
  - phase: DEPLOY
    status: SKIPPED_WITH_REASON
    reason: 未取得外部連線、runtime 或部署授權
  - phase: MAINTAIN
    status: SKIPPED_WITH_REASON
    reason: 本輪不建立正式 cache、provider 監測或資料保存作業
human_gate_id: HG-LR-02
human_gate_status: PENDING
review_status: CHANGES_REQUIRED_HUMAN_APPROVAL_PENDING
review_sha256: d7c4686b68f618a80bf72d94e1daee84c163f47f4bdd4c89b1a448af196b6bc4
automatic_fix_attempts: 0
final_status: PRIVACY_EVIDENCE_REVIEW_PASS_REMEDIATION_REQUIRED
```

### PLAN

- Input：frozen Human Gate packet、HG-LR-01 provider review、query／adapter／cache／reconciliation／sync／batch／replay 模組及官方個資法來源。
- Output：端到端資料流、資料分類、已驗證控制、阻擋 finding 與核准前條件。
- Gate：不得把 `DEIDENTIFIED_BY_CONSTRUCTION` 解讀為匿名或合規；不得核准外部傳輸、正式 cache、runtime 或 Gate 2。
- Evidence：前置 packet 與 HG-LR-01 review SHA-256 均未漂移。

### DESIGN

- 資料流分成 runtime reachability、query build、hosted boundary、normalization、cache、removal audit 及 reports 七段。
- 每段記錄 current state、data、persistence、classification 與 evidence。
- 法律來源只提供目的限制及安全維護控制參考；實際 operator、目的、法律依據及生效版本保留人工法律審查。
- review 明列 `ANONYMOUS_DATA`、`LEGAL_COMPLIANCE_CONFIRMED`、`CACHE_SECURITY_APPROVED`、`HOSTED_TRANSFER_APPROVED` 等禁止宣稱事項。

### BUILD

- 新增 `docs/evidence/hg_lr_02_privacy_security_review.json`。
- 新增 `docs/HG_LR_02_PRIVACY_SECURITY_REVIEW.md`。
- 新增 `tests/test_hg_lr_02_privacy_security_review.py`。
- 更新 README 與 Human Gate 索引；未改寫 frozen packet、HG-LR-01 evidence 或 runtime surfaces。

### TEST

- HG-LR-02 + HG-LR-01 + frozen packet targeted pytest：20 passed。
- 既有法律檢索隱私相關 pytest：55 passed。
- Full pytest：283 passed。
- Python `compileall`：PASS。
- `pyflakes tests/test_hg_lr_02_privacy_security_review.py`：PASS。
- `node --check app/static/app.js`：PASS。
- Node 前端行為測試：19 passed。
- JSON parse：PASS。
- Runtime review token scan：0 references。
- `git diff --check`：PASS（只有既存 LF→CRLF warning）。
- Review SHA-256：`d7c4686b68f618a80bf72d94e1daee84c163f47f4bdd4c89b1a448af196b6bc4`。
- Packet SHA-256：`469e2f56c93f0b4b57a93094793a6c40ae7d66b730591c612b5399a461a44acd`，未漂移。
- HG-LR-01 review SHA-256：`dc912a580351fbf4b71a4a77a5e9229338095733f188479bfe3191952ec1fce5`，未漂移。

### 已確認阻擋項

- `P01`：cache title 與 canonical URL 保留公開裁判案號線索，與「不保存案號」的廣義文件敘述不一致。
- `P02`：caller-controlled invalid status value 會被插入 exception；未來若被 log 或顯示可能洩漏。
- `P03`：commit cache 是明文 JSON，沒有模組層 encryption、ACL、retention 或 verified deletion。
- `P04`：hosted provider 第一方政策允許記錄完整 query parameters 或 query text。
- `P05`：deterministic unkeyed SHA-256 不是匿名化證明，也不是簽章。
- `P06`：正式目的、retention、access、deletion 與 incident owner 未指定。

### DEPLOY

- `SKIPPED_WITH_REASON`：`HG-LR-02` 明確為 changes required，未授權外部查詢、正式 cache、runtime 或部署。

### MAINTAIN

- `SKIPPED_WITH_REASON`：修正 `P01`／`P02` 及完成儲存、provider、retention、incident 決策後，必須重建 evidence review 並由隱私／資安角色核准。

## 2026-10-15：最小可運行網頁閉環與 P02 修正

execution_mode: `SINGLE_EXECUTOR`
agent_mode: `SINGLE_AGENT_MODE`

### PLAN

- Input：使用者要求一路執行到可在本機網頁輸入案情，取得候選罪章、問句、提問方式與條陳。
- Gate：只允許本機合成案件驗證；外部 provider、正式 cache、正式案件與部署維持停用。
- Evidence：確認 `/api/cases`、Gate action、brief 與 DOCX routes 已存在，再以隔離暫存 SQLite 跑瀏覽器旅程。

### DESIGN

- 保留既有 Gate 1–5、候選非結論、`HUMAN_REVIEW_REQUIRED`、公司範本逐字題與八頁文件上限。
- 問句畫面新增獨立「提問方式」，依公司題、敘述題、單一事實題與證據追問題提供中立操作提示；不得把候選罪章當成已成立。
- 以 `data:,` favicon 消除瀏覽器自動 favicon 請求造成的 404 console error。
- `P02` 驗證錯誤改用穩定 error code 與欄位層級訊息，不回顯 caller-controlled value。

### BUILD

- 更新 `app/static/app.js`：顯示可讀的提問方式與人工確認邊界。
- 更新 `app/static/index.html`：加入內嵌空 favicon。
- 更新 `tests/test_frontend_api_errors.mjs`：鎖定提問方式、單一事實與候選非結論文字。
- 重建 `LR-HG-20261015-03`、`HG-LR-01-REVIEW-20261015-02` 與 `HG-LR-02-REVIEW-20261015-02` 證據鏈；沒有改變任何 Human Gate 核准狀態。

### TEST

- 本機瀏覽器合成竊盜案：首頁 HTTP 200；Gate 1 產生 12 筆結構化事實；候選顯示竊盜、侵占、搶奪／強盜／海盜；動產竊盜 child route 可選。
- 被害人題包：37 題；逐題作答後補登證明單案號，產生 205 字條陳；條陳 DOCX 35,897 bytes、筆錄 DOCX 38,818 bytes，筆錄由 LibreOffice 實際排版為 4 頁。
- 提問方式瀏覽器驗證：涉嫌人題包 39 題，畫面可見公司逐字題的中立提問方式。
- 瀏覽器 console error 0、request failure 0；375px、768px、1440px 均無水平溢位；複製內容以換行正規化後一致。
- 基礎可及性檢查：可見 controls 無未標籤項目、無重複 ID、存在 main/nav landmarks、第一個 Tab 焦點為「跳到主要內容」。未安裝 axe，完整 WCAG 2.2 AA 自動掃描為 `NOT_RUN`。
- 視覺回歸：沒有既有 baseline，狀態為 `INCONCLUSIVE`；人工檢視首頁、問句與輸出畫面未見阻斷操作的版面問題。
- Core Web Vitals：CLS 0.0095；headless run 未取得 LCP 與 INP，兩者為 `UNKNOWN`，不得宣稱完整達標。
- Full pytest：286 passed。
- Python `compileall`：PASS。
- JavaScript syntax：PASS。
- Node 前端行為測試：20 passed。
- `git diff --check`：PASS（只有既存 LF→CRLF warning）。
- Packet SHA-256：`5bfb369395f10bd74bb4e1ed7b43093d0e2cc9f8855ffebfca33cf069941db11`。
- HG-LR-01 review SHA-256：`3642b635f95056a7173335b5c32d20d2933209d470e0b8993059d6e1a845a435`。
- HG-LR-02 review SHA-256：`1dc4676a371966e8bdf5514372dc0aa24e9ad3859f1766d6828f6c45e7af23f0`。

### DEPLOY

- `SKIPPED_WITH_REASON`：未取得外部部署授權。本輪只證明本機 `127.0.0.1` 最小運行閉環。

### MAINTAIN

- `P01`、`P03`、`P04`、`P05`、`P06` 與 `HG-LR-01` 至 `HG-LR-05` 仍維持人工核准邊界；本機功能通過不等於外部法律檢索或法律正確性通過。

## 2026-10-15：首頁改為摘要單一輸入

execution_mode: `SINGLE_EXECUTOR`
agent_mode: `SINGLE_AGENT_MODE`

### PLAN

- Input：移除首頁的時間類型、發生／破獲時間及發生／破獲地點三個欄位，改由使用者寫入案情摘要。
- Gate：不得從一般敘述猜測時間或地點；後續 Gate 1 與條陳仍須有可人工修正的明確值。

### DESIGN

- 摘要欄位提供可直接照抄的「發生／破獲／查獲時間：」「發生／破獲／查獲地點：」「案情經過：」格式。
- 後端只讀取明示標籤；標籤缺漏時保存 `UNKNOWN`。
- 舊 API 傳入 `event_kind`、`event_time`、`location` 時仍優先採用，維持既有案件與整合相容性。
- Gate 1 人工修正「時／地」後，同步更新條陳使用的 intake 值。

### BUILD

- `app/static/index.html`：移除三個首頁欄位，增加摘要 placeholder 與提示。
- `app/workflow.py`：新增明示標籤解析、`UNKNOWN` fail-closed 與 Gate 1 修正同步。
- `tests/test_workflow.py`：新增摘要標籤、缺漏 `UNKNOWN`、舊欄位優先及 Gate 1 修正測試。
- 重建 `LR-HG-20261015-04`、`HG-LR-01-REVIEW-20261015-03`、`HG-LR-02-REVIEW-20261015-03` 證據鏈；Human Gate 狀態未變。

### TEST

- 摘要單一輸入 targeted pytest：33 passed。
- Browser QA：三個舊欄位 selector 均為 0；摘要 placeholder 與提示可見；空摘要由瀏覽器 required validation 阻擋。
- Browser QA：明示「發生時間」「發生地點」後，Gate 1 的時、地分別完整帶入，並產生竊盜、侵占、搶奪／強盜／海盜候選。
- 375px、768px、1440px 均 HTTP 200、無水平溢位；console error 0、request failure 0；可見 controls 無未標籤項目。
- 視覺回歸沒有既有 baseline，狀態為 `INCONCLUSIVE`。
- Full pytest：289 passed；Python `compileall`、JavaScript syntax、Node 前端行為測試 20 passed 及 `git diff --check` 均為 PASS。

### DEPLOY

- `SKIPPED_WITH_REASON`：未執行外部部署；本機服務依專案 `start.ps1` 重新啟動。

### MAINTAIN

- 若摘要未使用明示標籤，後續時間、地點保持 `UNKNOWN`，必須在 Gate 1 人工補正；不得以候選或其他上下文推測。

## 2026-10-27：財產罪橫向驗收—一般侵占第335條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### PLAN / DESIGN

- Input：依 queue 鎖定 `embezzlement_335_general`，比較 `theft_320_1_movable`、`embezzlement_336_1_public`、`embezzlement_336_2_business`、`embezzlement_337_lost_property`。
- Gate：只核准問句設計；runtime、部署、法律結論與個案 `CASE_HUMAN_GATE` 均不在授權範圍。
- Sol decision：`ACCEPT_WITH_MODIFICATIONS`；既有 `prior_lawful_custody`、`authorization_scope`、`post_acquisition_conduct` 改採引用與缺漏追問，單一答案不得產生 `ACTIVE`。

### BUILD / TEST

- 建立8個 role-aware concepts；exact重複為內部0、既有來源0。
- `tests/test_question_work_item_contract.py` 與 `tests/test_offense_linkage_poc.py`：15 passed。
- Full pytest：630 passed；Node前端：31 passed；JavaScript syntax：PASS；`GET /api/health`：HTTP 200。
- 合成20題LibreOffice排版：victim 2頁、suspect 4頁、transfer 3頁。
- 歸檔SHA-256：`6EE5032F154C6C0B0FD980987961BADE0A874DBED2F4E64CFEBF16C77E2AB7A4`；與來源逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未授權runtime接線或外部部署。
- `embezzlement_335_general` 已歸檔；下一鎖定 child route 為 `embezzlement_336_1_public`。

## 2026-10-27：財產罪橫向驗收—公務／公益侵占第336條第1項

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`embezzlement_336_1_public`；比較一般侵占、業務侵占、動產竊盜及侵占遺失物。
- 獨立審查：`ACCEPT_WITH_MODIFICATIONS`；C05只保留身分／任用／委託／職掌，C06拆分公務與公益nexus，C07移除既遂／未遂法律分類。
- 聚合邊界：單題不得 `ACTIVE` 或 `EXCLUDED`；多來源一致時最高仍為 `CANDIDATE_NEED_REVIEW`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed；Node前端：31 passed；JavaScript syntax：PASS；health：HTTP 200。
- exact重複：內部0、既有來源0；LibreOffice 20題：victim 2頁、suspect 4頁、transfer 3頁。
- 歸檔SHA-256：`D7149646B2FDB598DBE884F42A94A78790CB09F35C0CF196F7E6462BB48CC7C2`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、未取代個案 `CASE_HUMAN_GATE`。
- 下一鎖定 child route：`embezzlement_336_2_business`。

## 2026-10-27：財產罪橫向驗收—業務侵占第336條第2項

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`embezzlement_336_2_business`；比較一般侵占、公務公益侵占、動產竊盜及侵占遺失物。
- 工作單由336(1)模板轉換後清理殘留語意；C05限縮業務職務／任用／委託／職掌，C06限縮特定物與具體業務事項nexus，C07只記錄外部處置。
- 獨立審查規格結論：`ACCEPT_WITH_MODIFICATIONS_SPEC_LEVEL`；不得由職稱、帳款短少或單一處置升候選。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed；Node前端：31 passed；JavaScript syntax：PASS；health：HTTP 200。
- exact重複：內部0、既有來源0；LibreOffice 20題：victim 2頁、suspect 4頁、transfer 3頁。
- 歸檔SHA-256：`642430642FE1027F350962E1349C4F340239B97D925E2F97E7F4CB60B7EB0F31`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一鎖定 child route：`embezzlement_337_lost_property`。

## 2026-10-27：財產罪橫向驗收—侵占遺失物等離本人持有之物第337條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`embezzlement_337_lost_property`；比較一般侵占、公務／公益侵占、業務侵占及動產竊盜。
- C05確認取得時是否為遺失、漂流或其他離本人持有；C06另查原持有人可辨識性與回復脈絡；C07只記錄外部處置，不作既遂／未遂分類。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與民事替代方向均為 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed；Node前端：31 passed；JavaScript syntax：PASS；health：HTTP 200。
- exact重複：內部0、既有來源0；LibreOffice 20題：victim 2頁、suspect 4頁、transfer 3頁。
- 歸檔SHA-256：`411A2B5191C59DEFD655A0F59E011E0AC62C77A1A63152822EB3F31DFFF6F15E`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一鎖定 child route：`embezzlement_338_applicable`；先判定其程序性質，不直接建立犯罪構成要件題組。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：妨害公務橫向驗收—刑法第138條毀損隱匿公務掌管文書物品

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`obstruction_138_official_property`；第135至137及第139至141條其他妨害公務路線、第140條部分與第141條之1失效／排除路線分開處理。
- C02至C08分開確認公務掌管／委託掌管關係、文書圖畫或物品、毀棄／損壞／隱匿／致令不堪用行為、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true；內部 exact duplicate：0。
- 歸檔SHA-256：`4D7E80B97C478878A9277F535277A140F064B3439C0E2AB61A1E2317108E1DF5`；submission：`AA336FDE87E783C650606477C2B29DEAC782959A3E501F3ECD045BFF01CF8AC0`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 為 `obstruction_139_seal_seizure`。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：妨害公務橫向驗收—刑法第137條妨害依法舉行考試

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`obstruction_137_exam_fraud`；第135、136及第138至141條其他妨害公務路線、第140條部分與第141條之1失效／排除路線分開處理。
- C02至C08分開確認依法舉行考試、詐術／其他非法方法、不正確結果、未遂／既遂與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true；內部 exact duplicate：0。
- 歸檔SHA-256：`E8FB248232062F36F6C61305997335D3320E5AB5FF8C3263DB2A009C78E880CB`；submission：`354DB114EEF06FFB7E877426736148EAC61A856DE037AB94AEB713897E932A4E`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 為 `obstruction_138_official_property`。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：妨害公務橫向驗收—刑法第136條聚集三人以上妨害公務

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`obstruction_136_group`；第135條及第137至141條其他妨害公務路線、第140條部分與第141條之1失效／排除路線分開處理。
- C02至C08分開確認公共場所、三人以上聚集、第135條行為、在場助勢／首謀／下手實施角色、死亡或重傷結果與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true；內部 exact duplicate：0。
- 歸檔SHA-256：`46195C5E7B271AC581E8FE02E845C861B5795F184BD4556F9F3DC02F3CC54C31`；submission：`39585DF3589228349BFFB7C55F715F5DED11CB302F5BCA37BF3DB531067C82E8`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 為 `obstruction_137_exam_fraud`。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：妨害公務橫向驗收—刑法第135條對依法執行職務公務員施強暴脅迫

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`obstruction_135_violence_threat`；第136至141條其他妨害公務路線及第140條部分、第141條之1失效／排除路線分開處理。
- C02至C08分開確認依法執行職務、公務員身分、強暴脅迫、工具／危險物品、死亡或重傷結果、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true；內部 exact duplicate：0。
- 歸檔SHA-256：`7FF997A6783ACCE1461B4E167D50615CB4B000C6B3083D7A604B308333DA961C`；submission：`8A20DCD3E505C3D6000E78E4E329830E9CDBB1A4057F7860841CB048FC0D4D5E`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 為 `obstruction_136_group`。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第134條公務員假借職務犯一般罪加重

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_134_official_aggravation`；第129至133條其他瀆職、基本罪、定義與程序路線分開處理。
- C02至C08分開確認公務員身分、假借職務權力／機會／方法、章外故意犯罪、既有特別刑度、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true；內部 exact duplicate：0。
- 歸檔SHA-256：`86AB414536D4E54E1871077F12BE03D81BE779FC8D6DEC0373B7BCEEB3A2C8F7`；submission：`E989CE4F9340B1C237CC94E300C31E3CF67DA119287DAC55FB448C29FDB16854`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 parent route 為 `obstruction`，尚未選定 child route。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第133條郵電公務員開拆隱匿郵件電報

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_133_mail`；第129至132條及第134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認郵務／電報機關執行職務身分、郵件電報種類、開拆／隱匿／交付行為、對象流向、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true；內部 exact duplicate：0。
- 歸檔SHA-256：`3FB38B31C8A5BCDE8530A9A6180AD04CABB1D0F2588FECB3A0A5EB404E685898`；submission：`5028CBB72483BA679CE2B3847908ECC05F8352314EA5F152198CD6BC1FB0F4C7`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第132條洩漏國防以外公務秘密

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_132_nondefense_secret`；第129至131條及第133至134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認秘密資料是否依法應秘密、取得／持有／洩漏行為、洩漏對象、故意／過失、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true；內部 exact duplicate：0。
- 歸檔SHA-256：`12569968DD52E2CEF53D8D90E5D8E256E95983D4E001E705EA0E82132A78938B`；submission：`C5F09A9A021078F2017F4990416C5C3477FD0AB57C6EB4B83BF9C8EAFBB09FB2`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第129條違法徵收或抑留剋扣

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_129_illegal_collection`；第120至128條及第130至134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認公務員身分、職務款項物品、違法徵收／抑留／剋扣、明知狀態、未遂／既遂、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；archive_equal：true；內部 exact duplicate：0；全量測試待收尾執行。
- 歸檔SHA-256：`E0A5167DB01796D509493FCE0ED3F17668DC3BEFBCF6CFB2FEC19D8423BA29E0`；submission：`2D0545FCB4669958C7CD7E9B6E0402BDC42C831FFF56B699C3C13BC1EC7859CD`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第130條公務員廢弛職務釀成災害

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_130_disaster`；第129條及第131至134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認公務員身分、法定職務、廢弛職務、災害結果、因果關係、可預見性、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true；內部 exact duplicate：0。
- 歸檔SHA-256：`1A81EC8EE3B956A18DD8E2F3BEB2BC3E298EA6A17D6D65BAFE1C4F20B34000E4`；submission：`057B90C258286AE28CAA6F361BE78FBCE80B7BD9E49671688369FF06CD32B727`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第131條主管監督事務圖利

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_131_unlawful_benefit`；第129、130條及第132至134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認公務員主管／監督事務、法令違反、私人不法利益、利益結果、因果關係、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true；內部 exact duplicate：0。
- 歸檔SHA-256：`FBB35E991F46E959DE490B5D1401481572EDEA81103AA9B140C5CEF7A5AF0A10`；submission：`4299B407A19C8AF002D72E7F838F091B40E09F12E23DEF254E44529818C77677`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第128條明知不應受理訴訟而受理

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_128_unlawful_acceptance`；第120至127條及第129至134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認公務員身分、訴訟事件、法定受理要件、明知不應受理、實際受理行為、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；archive_equal：true；內部 exact duplicate：0；全量測試待收尾執行。
- 歸檔SHA-256：`7C7C11CBF7F852F0F6C073297B0D66970B6B76A4A0294AA0BB912467D262A4EC`；submission：`275D5FC465C334FA9D57EF1FA361D968AF0298E9B170BB994B651FC7DFF44808`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第127條違法執行或不執行刑罰

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_127_execution`；第120至126條及第128至134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認執行刑罰職務身分、違法執行／不執行／過失執行行為、刑罰內容與執行依據、執行狀態、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；archive_equal：true；內部 exact duplicate：0；全量測試待收尾執行。
- 歸檔SHA-256：`5A827094ECC8FB2A478CCD86DBBF44BE7D0B4933E3C753A980C93FFD88AAA2F5`；submission：`DD0C276062822F876397797C418A2A82CE9DA8E03BD87D8176BB993A10409B26`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第126條職務上凌虐人犯

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_126_abuse_detainee`；第120至125條及第127至134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認管收解送拘禁職務身分、凌虐行為、死亡或重傷結果、因果關係、可預見性、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；archive_equal：true；內部 exact duplicate：0；全量測試待收尾執行。
- 歸檔SHA-256：`3B0B8287BB70CEB59837302CDBB5EF3EBB5C940771788ABB53BDB45C6A4064FE`；submission：`F8B3B8473C535A9E6493232AA313F67A45FD3CC7537351A035CB5B55A0305461`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第125條追訴處罰職務濫權

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_125_abuse_prosecution`；第120至124條及第126至134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認追訴處罰職務身分、濫權逮捕羈押／取供／錯誤追訴行為、死亡或重傷結果、因果關係、可預見性、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；archive_equal：true；內部 exact duplicate：0；全量測試待收尾執行。
- 歸檔SHA-256：`4D88451630DD597AFB5039B17A714A9DD87CEDD4398DCA189BC862690FB1979B`；submission：`40EC502774F3A792699FB340CD666451D0733DC199053650366356D29D006DFF`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第124條枉法裁判或仲裁

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_124_unlawful_judgment`；第120至123條及第125至134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認司法身分、裁判或仲裁行為、法令依據、明知違法、個別角色、結果因果與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；archive_equal：true；內部 exact duplicate：0；全量測試待收尾執行。
- 歸檔SHA-256：`E30FE8942F6AB22FAB60C15672D92420ED5BCC6E04BEE13ABD2AB58F0419AB67`；submission：`599A80AC49F5B910CE2378E88857AED85AAA2AB58D99AD31537FCBF635B91443`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第123條準公務員預先受賄後履行

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_123_advance_bribery`；第120至122條及第124至134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認預先尚未具身分、預先要求／期約／收受利益、後來取得身分、後續履行、個別角色、利益流向與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；archive_equal：true；內部 exact duplicate：0；全量測試待收尾執行。
- 歸檔SHA-256：`4ACFE021D801912421929DF9A8B6A7E2D773175B9AA6EE52172361849277942B`；submission：`E4E10FFD28EFB924D22A3795C1E19F9319AAA5E196A896C6DE93AA67C213DBFA`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第122條違背職務受賄

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_122_bribery_breach`；第120、121、123至134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認公務員或仲裁人身分、要求／期約／收受／行求交付不正利益、違背職務、個別角色、利益流向與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；archive_equal：true；內部 exact duplicate：0；全量測試待收尾執行。
- 歸檔SHA-256：`0C7DF03D4A9DF1DE3B79439890FE101FA669DDDFCDEB73D800EA3CF44C33A26F`；submission：`6AC9F343984135F284CA4228672771CEE48BE07D437C1D07F70B581DB2B11CCF`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第121條職務行為受賄

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_121_bribery_duty`；第120條、第122至134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認公務員或仲裁人身分、受賄行為、職務上行為、個別角色、利益流向與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；archive_equal：true；內部 exact duplicate：0；全量測試待收尾執行。
- 歸檔SHA-256：`4781176611954206ED68B06B78441E4AC75D8FC4395AF0F7A454AE676B3793C7`；submission：`CB4650367272A3E64F371CD8F8323D6A3E118E78A68C437B025218165666DC6D`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：瀆職罪章橫向驗收—刑法第120條公務員委棄守地

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`duty_120_abandon_post`；第121至134條其他瀆職、加重、定義與程序路線分開處理。
- C02至C08分開確認公務員身分、守地職責、委棄守地行為、守地範圍、個別角色、結果因果與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；archive_equal：true；內部 exact duplicate：0；全量測試待收尾執行。
- 歸檔SHA-256：`1A53063DEB0E51BDC407E6BD26F2A81AC8E5C7FED396A81C6CE13961042FF9FB`；submission：`998837ADC9B9C3AC5039242F2A52346074A9A53CB82CB556D287C6EEE69E1AE6`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第118條公然侮辱外國國旗國章

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`state_security_118_foreign_symbol`；第100至117條及第115之1、116、119條路線分開處理。
- C02至C08分開確認侮辱意圖、公然行為、公然性、外國旗章客體、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。

### TEST / ARCHIVE

- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true；內部 exact duplicate：0。
- 歸檔SHA-256：`4CEF3A07A8AADA51215396D7A42A77C527D23EB99C09270541B8C99C7D07A509`；submission：`41852F27F55BC78F6C550039AD4947EC75D21C63930955F4E8548D9CAB832692`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代 `CASE_HUMAN_GATE`；下一個 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第117條違背局外中立命令

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

- 目標：`state_security_117_neutrality`；第100至116、118條及第102、107、115之1、119條路線分開處理。
- C02至C08分開確認外國交戰期間、政府局外中立命令、具體違背命令行為、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- 契約與 linkage：15 passed；archive_equal：true；本輪全量測試待收尾執行。
- 歸檔SHA-256：`0735EFBA2B1F63F2BCCFAFB76A93B520DE13E753E61AF1D5D486C3F751DFB316`；submission：`799D46C08C2DF093660AA94B79089478B47268C41FBD6463234B882841556AE8`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳暫停、未取代 `CASE_HUMAN_GATE`；下一 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第115條毀損隱匿對外權利證據

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

- 目標：`state_security_115_foreign_right_evidence`；第100至114條及第115之1、116、119條路線分開處理。
- C02至C08分開確認我國對外權利證據客體、偽造／變造／毀棄／隱匿行為、個別角色、結果與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- 契約與 linkage：15 passed；archive_equal：true；本輪全量測試待收尾執行。
- 歸檔SHA-256：`1B616647C2A29C6A232220B8D1E5A33BEFD7ADA5C911515D2B628D654666E9B3`；submission：`67BDA93F44B19697B9759662EB4ACE6A455DB7308BD35B46DC9B517383330E9D`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳暫停、未取代 `CASE_HUMAN_GATE`；下一 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第114條違背外交事務委任

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

- 目標：`state_security_114_breach_mandate`；第100至113條及第115、102、107、115之1、119條路線分開處理。
- C02至C08分開確認政府委任、外交事務、委任內容、違背行為、損害結果、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- 契約與 linkage：15 passed；archive_equal：true；本輪全量測試待收尾執行。
- 歸檔SHA-256：`1B102CDC3082E1BAEE31D669613B4B918246FDCBE2BA1DD730FEB5C94BA8FE97`；submission：`6B3BA11A255EEEBA7BB0CE8056F0262EDD8BEE64CCB08D95A30F1FFCEB5A9864`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳暫停、未取代 `CASE_HUMAN_GATE`；下一 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第113條未授權私與外國政府約定

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

- 目標：`state_security_113_foreign_agreement`；第100至112條及第114、115、102、107、115之1、119條路線分開處理。
- C02至C08分開確認依法應授權事項、未獲授權、外國政府／派遣人、約定內容、損害風險與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- 契約與 linkage：15 passed；archive_equal：true；本輪全量測試待收尾執行。
- 歸檔SHA-256：`442A576BD7B5B9FEEDB616EC2DAB74B858CBA06E271F36D59E3B955627B9DDD6`；submission：`0801F6824638C89B8F16613776307C1E2BE259FF23897524A12D2A9807938565`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳暫停、未取代 `CASE_HUMAN_GATE`；下一 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第112條侵入軍事處所

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

- 目標：`state_security_112_military_site`；第100至111條及第102、107、115之1、119條路線分開處理。
- C02至C08分開確認刺探／收集國防秘密目的、未受允准、軍事處所、進入／留滯行為、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- 契約與 linkage：15 passed；archive_equal：true；本輪全量測試待收尾執行。
- 歸檔SHA-256：`1D5FE42701C9D31FEFE044F30DB8AA6B5B419D9BA55A6313F08B41D41F4EB298`；submission：`0C650A97954DCC0AE35209F2F64014010D91F7E4A3B83A9C9BC7C3D854866F05`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳暫停、未取代 `CASE_HUMAN_GATE`；下一 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第111條刺探收集國防秘密

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

- 目標：`state_security_111_collect_secret`；第100至110條及第112、102、107、115之1、119條路線分開處理。
- C02至C08分開確認刺探／收集行為、國防秘密客體、行為進度、個別角色、對象與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- 契約與 linkage：15 passed；archive_equal：true；本輪全量測試待收尾執行。
- 歸檔SHA-256：`0A399937B7108F706BC1EF9FAE924E9A9B3CF5B75098287896B4A34F2A96794D`；submission：`254164A783BA1C09CD8599E988047153FE7F3F5B90C6116AB070C562731B6A67`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳暫停、未取代 `CASE_HUMAN_GATE`；下一 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第110條公務員過失洩漏國防秘密

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

- 目標：`state_security_110_negligent_secret`；第100至109條及第111、112、102、107、115之1、119條路線分開處理。
- C02至C08分開確認公務員身分、職務上知悉／持有、國防秘密、過失洩漏／交付、對象與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- 契約與 linkage：15 passed；archive_equal：true；本輪全量測試待收尾執行。
- 歸檔SHA-256：`7D8247E37319CDE70754C6F13F38E06FFD42262B30AA22827DA26B262E9CC3DB`；submission：`C700B58EE9D3613DB5535F24878F028472342B016F2A5F7D2C2FF702BCDCAF81`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳暫停、未取代 `CASE_HUMAN_GATE`；下一 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第109條洩漏交付國防秘密

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

- 目標：`state_security_109_defense_secret`；第100至108條及第110至112、102、107、115之1、119條路線分開處理。
- C02至C08分開確認國防秘密客體、洩漏／交付行為、對象、行為進度、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- 契約與 linkage：15 passed；archive_equal：true；本輪全量測試待收尾執行。
- 歸檔SHA-256：`F295907C473225B2C2A4FE87D12CCEA21C1E10FD380B1510F6430D87F10DF469`；submission：`10762FF2357EC6958BFB07E1EABC1F251FF789E7399E8C5F6A7C7FC9A3924B38`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳暫停、未取代 `CASE_HUMAN_GATE`；下一 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第108條戰時不履行軍需契約

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

- 目標：`state_security_108_military_supply`；第100至106條及第102、107、115之1、116、119條路線分開處理。
- C02至C08分開確認開戰期間、軍需供給契約、故意／過失、不履行或不完全履行、個別角色與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true。
- 歸檔SHA-256：`DF8E450E90C427CD559F0AA02AB6AF18CDCAC7A33C94F66A19CA07007A5ADD1E`；submission：`94832DE431268A3E089735E3B3F898AFB65024997D38830C69324669B3BD9309`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳暫停、未取代 `CASE_HUMAN_GATE`；下一 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第106條供敵軍事利益或害我國軍事利益

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

- 目標：`state_security_106_military_advantage`；第100、101、103至105條及第102、107、115之1、119條路線分開處理。
- C02至C08分開確認戰時／將戰期間、敵軍事利益或我國軍事不利益、具體行為進度、個別角色、結果與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true。
- 歸檔SHA-256：`42CBCB93D66BEC5340135C826F42ECD63AF396BB7F939E8E9BA982D823EA546C`；submission：`36279321E4F48D20768C584AAC8F87970D7C3719B6604FAE9E67BECA0F0C077D`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳暫停、未取代 `CASE_HUMAN_GATE`；下一 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第105條為敵軍服役或械抗我國

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

- 目標：`state_security_105_enemy_service`；第100、101、103、104、106條及第102、107、115之1、119條路線分開處理。
- C02至C08分開確認國民身分、敵軍服役／械抗行為、行為進度、個別角色、對象／結果、聯絡脈絡與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true。
- 歸檔SHA-256：`8FB7467E7B1EF9842E92472D690F3C321428DB187D562D3CE74AE26371DA0FF0`；submission：`9C9DFBD2FF571D42037B2E848F78F1E578BA67F3D619E890A34680282C46CCD4`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳暫停、未取代 `CASE_HUMAN_GATE`；下一 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第104條通謀外國使我國領域屬於他國

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

- 目標：`state_security_104_territory`；第100、101、103、105條及第102、107、115之1、119條路線分開處理。
- C02至C08分開確認通謀對象、領域移轉目的、行為進度、個別角色、目標／結果、聯絡脈絡與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true。
- 歸檔SHA-256：`84836285280D49D59485DCF341E56F01910F60BEED826C23928C2DD0E5B2AB8B`；submission：`E0C2DB5C3310ECEA456E7980DF5B96AA02D575F716AFF1AD3F8BABDD8E7F7C4D`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳暫停、未取代 `CASE_HUMAN_GATE`；下一 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第103條通謀外國使開戰

execution_mode: `REVIEWED_PIPELINE`; agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`; triggers: `S3`、`S4`

- 目標：`state_security_103_start_war`；第100、101、104、105條及第102、107、115之1、119條路線分開處理。
- C02至C08分開確認通謀對象、使開戰目的、行為進度、個別角色、目標／結果、聯絡脈絡與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- 契約與 linkage：15 passed；Full pytest：630 passed；archive_equal：true。
- 歸檔SHA-256：`C299EA6824879003F3FF1343739396BE5C33426D3568602E30D1F2E33FF0DE0A`；submission：`4303FC4653630E58BA381072DEA149E5D3CD96A3DCCE58CAEDE9B8230429C819`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳暫停、未取代 `CASE_HUMAN_GATE`；下一 child route 尚未選定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第101條暴動內亂

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`state_security_101_riot`；第100條、第103至105條及第102、107、115之1、119條路線分開處理。
- C02至C08分開確認暴動內亂目的、強暴或脅迫、行為進度、個別角色、目標／結果、聯絡脈絡與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- `UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`；本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed；archive_equal：true。
- 歸檔SHA-256：`B499EA1D9AE4A9174B6137421F7FB0857BB1B046155A9BBDE548FE5A943761BA`；submission SHA-256：`14D3E022C7A82BE3E4C69122EF2B4DD609A041247F6DA02149DBA39709345E94`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；仍須由 controller 鎖定，不可整章展開。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：國家安全罪章橫向驗收—刑法第100條內亂

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`state_security_100_insurrection`；第101條暴動內亂、第103至105條外患及第102、107、115之1、119條減免／加重／定義／程序路線分開處理。
- C02至C08分開確認法定目的、強暴或脅迫、行為進度、個別角色、目標／結果、聯絡脈絡與證據來源；單題不產生 `ACTIVE` 或 `EXCLUDED`。
- `UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`；本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed；archive_equal：true。
- 歸檔SHA-256：`3DC8F6BD6D8F309FAE4C518777EA266DBE010CC06601D3F932323710D91697E8`；submission SHA-256：`D480F3AAE2A0A6D0B86EC661113C18582EA032976ACFA52B4CA3DA14AC63FA2E`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 為 `state_security_101_riot`，仍須由 controller 鎖定；不可整章展開。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：毒品危害防制條例橫向驗收—持有毒品或專供製造施用器具第11條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`drugs_11_possession`；第4至8條、第10條及第9條加重邊界分開處理，未混入同一工作單元。
- C02至C05分別處理持有／管領、毒品類別、純質淨重／門檻、專供製造施用器具目的與來源證據；各題保留 `CASE_HUMAN_GATE`。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；archive_equal：true。
- 歸檔SHA-256：`42307E94EC95B3E396E15813BF34882A6039B916B8CE8BC050A7457B176B800C`；submission SHA-256：`8570F6D6D34C93A63E9868CC877F8A7D135EEAF58422C5989CA0B42D4A46CEF7`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 parent route 為 `state_security`，必須先由 controller 鎖定單一 child route；不可整章展開。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：毒品危害防制條例橫向驗收—持有毒品或專供製造施用器具第11條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

- 目標：`drugs_11_possession`；第4至10條及第9條加重路線未混入本單一路線。
- C02至C05分開確認持有／實力支配、毒品品項／級別、純質淨重／數量門檻、器具用途、持有來源及證據；敏感內容維持 `CASE_HUMAN_GATE`，單題不產生 `ACTIVE` 或法律結論。
- 契約與 offense linkage：15 passed；archive_equal：`True`；歸檔SHA-256：`42307E94EC95B3E396E15813BF34882A6039B916B8CE8BC050A7457B176B800C`；submission SHA-256：`8570F6D6D34C93A63E9868CC877F8A7D135EEAF58422C5989CA0B42D4A46CEF7`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停；`UNKNOWN`／`CONFLICT` 維持 `NEED_REVIEW`。

## 2026-10-27：毒品危害防制條例橫向驗收—施用第一級或第二級毒品第10條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

- 目標：`drugs_10_use`；第4至9、11條及其他持有／交易路線未混入本單一路線。
- C02至C05分開確認施用行為、時間／地點／方法、毒品品項／級別、採尿／鑑驗與可回查證據；敏感內容維持 `CASE_HUMAN_GATE`，單題不產生 `ACTIVE` 或法律結論。
- 契約與 offense linkage：15 passed；archive_equal：`True`；歸檔SHA-256：`AB76DF8B9696BC5018BAD78FF16441C23AC4C14B6378CCB4AF7E4466C6F2FD44`；submission SHA-256：`D28F4A807320E9DB9076697F6D28F39D2D7D1D2716E19FFD07C574EBBE781E1F`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停；`UNKNOWN`／`CONFLICT` 維持 `NEED_REVIEW`。

## 2026-10-27：毒品危害防制條例第9條加重邊界決定

execution_mode: `REVIEWED_PIPELINE`

- `drugs_9_aggravation`：`route_kind=aggravation`，以第6至8條基礎行為或法定混合毒品行為為前提，不建立獨立 offense-core 題組。
- 未成年人、孕婦、混合毒品等加重事實及行為人認識保留 `HUMAN_REVIEW_REQUIRED`，於基礎路線完成後另行核對。
- `SKIPPED_WITH_REASON`：未將加重路線複製成獨立候選；`UNKNOWN`／`CONFLICT` 維持 `NEED_REVIEW`。

## 2026-10-27：毒品危害防制條例橫向驗收—轉讓毒品第8條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

- 目標：`drugs_8_transfer`；第4至7、10至11條及第9條加重路線未混入本單一路線。
- C02至C05分開確認轉讓／交付、毒品品項／級別、受讓人、交付經過、未遂既遂及證據；敏感內容維持 `CASE_HUMAN_GATE`，單題不產生 `ACTIVE` 或法律結論。
- 契約與 offense linkage：15 passed；Full pytest：630 passed；archive_equal：`True`。
- 歸檔SHA-256：`939AA1548A2070E3BF16796E8979D172523A61E3A182DDB269DD8FE26803484A`；submission SHA-256：`DCC727DEBA01646B37AF6A367E205BFA9CD2460823AC907D1225B67EF6468277`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停；`UNKNOWN`／`CONFLICT` 維持 `NEED_REVIEW`。

## 2026-10-27：毒品危害防制條例橫向驗收—引誘他人施用毒品第7條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

- 目標：`drugs_7_induce_use`；第4至6、8至11條及第9條加重路線未混入本單一路線。
- C02至C05分開確認引誘行為與內容、他人施用、毒品品項／級別、未遂既遂及證據；敏感內容維持 `CASE_HUMAN_GATE`，單題不產生 `ACTIVE` 或法律結論。
- 契約與 offense linkage：15 passed；Full pytest：630 passed；archive_equal：`True`。
- 歸檔SHA-256：`4B51E6015CF9C4A5E25A2B2744779E73228270D0582BB4F6D5CD2EA7697ECC48`；submission SHA-256：`D73443DB49612DA10911D560794D024D282CE7A64FFC6FF750E516F9E9F7F742`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停；`UNKNOWN`／`CONFLICT` 維持 `NEED_REVIEW`。

## 2026-10-27：毒品危害防制條例橫向驗收—以強暴脅迫等方法使人施用毒品第6條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

- 目標：`drugs_6_force_use`；第4、5、7至11條及第9條加重路線未混入本單一路線。
- C02至C05分開確認強暴／脅迫／欺瞞方法、他人施用、毒品品項／級別、死亡／重傷結果、因果及證據；敏感內容維持 `CASE_HUMAN_GATE`，單題不產生 `ACTIVE` 或法律結論。
- 契約與 offense linkage：15 passed；Full pytest：630 passed；archive_equal：`True`。
- 歸檔SHA-256：`B21875721A5791C5710F6DED6774FBC17F300C25DFF913E1A1BE6A259225CC93`；submission SHA-256：`8DB3DB5C6A67866795BA4A1C96D06C86FD7C736E82D1192C7A55CD7CEB352BB6`。
- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停；`UNKNOWN`／`CONFLICT` 維持 `NEED_REVIEW`。

## 2026-10-27：毒品危害防制條例橫向驗收—意圖販賣而持有毒品第5條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`drugs_5_possession_intent_sale`；第4、6至11條及第9條加重路線未混入本單一路線。
- C02至C05分開確認持有／實力支配、毒品品項／級別、販賣意圖客觀指標、數量／純質淨重、未遂既遂及證據；敏感內容維持最小必要詢問與 `CASE_HUMAN_GATE`。
- 所有單題不產生 `ACTIVE` 或法律結論；`UNKNOWN`、`CONFLICT` 與其他毒品路線維持 `NEED_REVIEW`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`490D888676ED9EDCA5399B4D7F273DCCAF0953F9F92AA694FD55AA94B7D2B04B`。
- submission SHA-256：`3B6BB9F0DFB27134571CCC5382D4C863FEBE8518598E8FC291C3FDA745BF98F1`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；持有、施用、轉讓與加重需逐一保留分流。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：毒品危害防制條例橫向驗收—製造運輸販賣毒品第4條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`drugs_4_manufacture_transport_sale`；第5至11條及第9條加重路線未混入本單一路線。
- C02至C05分開確認製造／運輸／販賣行為、毒品品項／級別、交易／運送／製造流程、角色、未遂既遂及證據；敏感內容維持最小必要詢問與 `CASE_HUMAN_GATE`。
- 所有單題不產生 `ACTIVE` 或法律結論；`UNKNOWN`、`CONFLICT` 與其他毒品路線維持 `NEED_REVIEW`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`35BDC8D6038E49EA297524BE508104E6C9D3595BD8A54ACB8D82FF8BA5CE87F5`。
- submission SHA-256：`CE827800BA17F8E8D8705AB98C21E72524E060187AF058CB809C29DCA5704E4E`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；毒品級別、交易與角色需逐一保留分流。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：公共危險橫向驗收—交通事故致人死傷逃逸第185條之4

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`public_danger_185_4_hit_and_run`；第185條之3酒毒駕及其他公共危險路線未混入本單一路線。
- C02至C05分開確認駕駛動力交通工具、事故、死傷結果、知悉事故、逃逸行為、過失減免及證據；所有單題不產生 `ACTIVE` 或法律結論。
- `UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`；`CASE_HUMAN_GATE` 仍為 `REQUIRED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`EC5279C9B56FD84994038BE5C8F4BF2184E4480ACD49CF612C79249FA522CA98`。
- submission SHA-256：`B741C4A44C6E72AAEF656ED2A0B2A0A72FF02F9AA0113459EACFD7C2D8D65AB5`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 parent route：`drugs`，仍須由 controller 逐一選定 child route。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：公共危險橫向驗收—酒毒駕駛動力交通工具第185條之3

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`public_danger_185_3_impaired_driving`；第185條之4交通事故逃逸及其他公共危險路線未混入本單一路線。
- C02至C05分開確認駕駛動力交通工具、酒精／毒品影響、不能安全駕駛、死亡／重傷結果、因果、可預見性與前案狀態；所有單題不產生 `ACTIVE` 或法律結論。
- `UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`；`CASE_HUMAN_GATE` 仍為 `REQUIRED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`E61764202758A508A30709003A4342B7174C066DAC98ED23DC4A756BD2E5DC1F`。
- submission SHA-256：`0FA630A64094787144298756B546C210FACEB812DE1357362DF3C73F0FABB487`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；第185條之4事故逃逸另行製作。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：跟蹤騷擾章分類／保護／審理程序邊界決定

execution_mode: `REVIEWED_PIPELINE`

- `stalking_3_definition`：`route_kind=classification`，只處理法定跟騷行為定義與適用分類。
- `stalking_4_17_protection`、`stalking_20_21_procedure`：`route_kind=procedure`，只處理書面告誡、保護令、審理不公開與羈押特別程序。
- 上述路線均保留 `HUMAN_REVIEW_REQUIRED`，不進犯罪構成要件題組；`UNKNOWN`／`CONFLICT` 不得反推第18或19條成立。
- `SKIPPED_WITH_REASON`：依 crosswalk route_kind 邊界，未將分類、保護令或審理程序混入 offense loop。
- 下一個 parent route：`public_danger`，仍須由 controller 逐一選定 child route。

## 2026-10-27：跟蹤騷擾橫向驗收—違反跟蹤騷擾保護令第19條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`stalking_19_protection_order`；第3條定義、第4至17條保護令、第18條基礎犯罪及第20至21條程序未混入本單一路線。
- C02至C05分開確認保護令有效性、送達／知悉、命令範圍、具體違反行為、程序脈絡及證據；敏感內容維持最小必要詢問與 `CASE_HUMAN_GATE`。
- 所有單題不產生 `ACTIVE` 或法律結論；`UNKNOWN`、`CONFLICT` 與其他跟騷路線維持 `NEED_REVIEW`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`EA4DACA1E68DF240C73654DB06EED58020983A7FB720117DC1766D2B317F1EB3`。
- submission SHA-256：`9405D5093773E22F1570B923B765EC28090B572DB7E9A70E58815AC5BC2D52D9`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；定義、保護令與審理程序另行處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：跟蹤騷擾橫向驗收—實行跟蹤騷擾及攜帶危險物加重第18條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`stalking_18_offense`；第3條定義、第4至17條保護令、第19至21條保護令犯罪／程序未混入本單一路線。
- C02至C05分開確認跟蹤騷擾法定態樣、反覆持續、違反意願、畏怖與日常生活影響、危險物品及證據；敏感內容維持最小必要詢問與 `CASE_HUMAN_GATE`。
- 所有單題不產生 `ACTIVE` 或法律結論；`UNKNOWN`、`CONFLICT` 與其他跟騷路線維持 `NEED_REVIEW`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`E05BF9DB5F7A84FDC0F6BC98B0BE83091E3B1BF5F9CBEAAED93DD195A97D047C`。
- submission SHA-256：`EC7778EFC98F8D3B855CA1688AE7451E006805B290F332AEBF1B11CD44290737`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；第19條保護令犯罪與定義／程序路線另行處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：性騷擾章分類／保護／行政邊界決定

execution_mode: `REVIEWED_PIPELINE`

- `sexual_harassment_2_scope`：`route_kind=classification`，只處理性騷擾定義、權勢分類及與性別平等工作／教育法的適用分流。
- `sexual_harassment_7_13_prevention`、`sexual_harassment_14_17_complaint`：`route_kind=procedure`，只處理防治、保護、申訴與調查流程。
- `sexual_harassment_26_30_administrative`：`route_kind=administrative`，只處理行政義務與裁罰事實。
- 上述路線均保留 `HUMAN_REVIEW_REQUIRED`，不進犯罪構成要件題組；`UNKNOWN`／`CONFLICT` 不得反推第25條成立。
- `SKIPPED_WITH_REASON`：依 crosswalk route_kind 邊界，未將分類、保護、申訴或行政責任混入 offense loop。
- 下一個 parent route：`stalking`，仍須由 controller 逐一選定 child route。

## 2026-10-27：敏感案件橫向驗收—乘人不及抗拒之性騷擾觸摸罪第25條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`sexual_harassment_25_unwanted_touch`；第2條分類、第7至17條保護／申訴程序及第26至30條行政路線未混入本單一路線。
- C02至C05分開確認性騷擾意圖、被害人不及抗拒情境、親吻／擁抱／觸摸方式、權勢關係、被害人反應與證據；敏感內容維持最小必要詢問與 `CASE_HUMAN_GATE`。
- 所有單題不產生 `ACTIVE` 或法律結論；`UNKNOWN`、`CONFLICT` 與其他性別事件路線維持 `NEED_REVIEW`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`283A0BDB9EB75011434EFCB2404C4B80EB1498D113FF49DBFC82A07289645871`。
- submission SHA-256：`EF8E3E614E72FCCA1AC41820E69B2F2E4E22CBD3EBB65C1FEAEB349555130895`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；性騷擾行政、保護與申訴程序另行處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：妨害電腦使用章第363條程序邊界決定

execution_mode: `REVIEWED_PIPELINE`

- `computer_363_complaint`：`route_kind=procedure`，只處理第358至360條部分罪名的告訴權人、告訴意思與提出情形，不建立犯罪構成要件題組。
- `SKIPPED_WITH_REASON`：依 crosswalk route_kind 邊界，未將告訴條件混入犯罪候選問句；程序問句須另建流程工作流。
- 電腦章可製作 offense／aggravation 路線已完成邊界整理；下一個 parent route 為 `sexual_harassment`，仍須由 controller 逐一選定 child route。

## 2026-10-27：財產罪橫向驗收—製作供電腦犯罪之程式第362條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`computer_362_malware`；第358至361、363條及其他電腦犯罪相鄰／加重／程序路線未混入本單一路線。
- C02至C05分開確認程式內容、製作行為、供犯罪使用意圖、製作人與資料來源及損害風險；所有單題不產生 `ACTIVE` 或法律結論。
- `UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`；`CASE_HUMAN_GATE` 仍為 `REQUIRED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`EC94C54070F4AFA0388DDD1A0FDA002155BF6EA2C3DD5CA3341CF0D10263D4E6`。
- submission SHA-256：`1C027987CEF6EF973E3D7329A4701C5E211BEBE2A40D945791907FD1DB244A14`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；由 controller 依佇列鎖定下一路線。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：妨害電腦使用章第361條加重邊界決定

execution_mode: `REVIEWED_PIPELINE`

- `computer_361_public_agency`：`route_kind=aggravation`，以第358至360條基礎行為及公務機關標的為前提，不建立獨立 offense-core 題組。
- 加重事由保留 `HUMAN_REVIEW_REQUIRED`，於基礎路線完成個案 `CASE_HUMAN_GATE` 後另行核對；runtime、crosswalk 與法律結論均未自動改寫。
- `SKIPPED_WITH_REASON`：依 crosswalk route_kind 邊界，未將加重路線當成可獨立候選罪名複製。
- 下一個可進入 offense-core 的 child route：`computer_362_malware`。

## 2026-10-27：財產罪橫向驗收—無故干擾他人電腦或相關設備第360條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`computer_360_interference`；第358、359、361至363條及其他電腦犯罪相鄰／加重／程序路線未混入本單一路線。
- C02至C05分開確認電腦程式／電磁方式、設備對象、干擾方法、授權範圍與損害風險；所有單題不產生 `ACTIVE` 或法律結論。
- `UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`；`CASE_HUMAN_GATE` 仍為 `REQUIRED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`2516B15DE69FAA250697791466BDCFA92B261397B4824464A321752B112E75CB`。
- submission SHA-256：`52012830BD9C7882733FE018A84D6855E4C3B6BF12CABA1BF539E593F505F062`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；由 controller 依佇列鎖定下一路線。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—無故取得刪除或變更電磁紀錄第359條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`computer_359_data_change`；第358、360至363條及其他電腦犯罪相鄰／加重／程序路線未混入本單一路線。
- C02至C05分開確認電磁紀錄對象、取得／刪除／變更方法、設備關聯、權限與損害風險；所有單題不產生 `ACTIVE` 或法律結論。
- `UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`；`CASE_HUMAN_GATE` 仍為 `REQUIRED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`F1B0D6CF40DB8AB00965303A486E952333A53790170872CCF44FC4F9FBCC3200`。
- submission SHA-256：`217401FE0DAAA3603BF8E0A393D06F082C157A7A3073875544632FBF6B4F23D5`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；由 controller 依佇列鎖定下一路線。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—無故入侵他人電腦或相關設備第358條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`computer_358_intrusion`；第359至363條及其他電腦犯罪相鄰／加重／程序路線未混入本單一路線。
- C02至C05分開確認設備對象、入侵方法、帳號／密碼、授權範圍、無故狀態與損害風險；所有單題不產生 `ACTIVE` 或法律結論。
- `UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`；`CASE_HUMAN_GATE` 仍為 `REQUIRED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`9C8279D26F5369009B1FB08280C161961AEFC3DE7BB070EE0F8592B78A5D55AA`。
- submission SHA-256：`C0E1C7368B9831915641ABD70A8E0747CD748BE7FE24C2BE98A029A6997771B2`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；由 controller 依佇列鎖定下一路線。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：偽造文書章 collateral／definition 邊界決定

execution_mode: `REVIEWED_PIPELINE`

- `forgery_219_confiscation`：`route_kind=collateral`，僅處理偽造印章、印文或署押與本章行為的沒收關聯；不建立 offense-core 構成要件題組。
- `forgery_220_document_definition`：`route_kind=definition`，僅處理文書／電磁紀錄準文書的範圍定義；不建立獨立定罪候選題組。
- 兩路線均保留 `HUMAN_REVIEW_REQUIRED`，並由對應犯罪路線在個案 `CASE_HUMAN_GATE` 中引用；runtime、crosswalk 與法律結論均未自動改寫。
- `SKIPPED_WITH_REASON`：依 `docs/OFFENSE_QUESTION_WORK_QUEUE.md` 第1、2、5節及 crosswalk route_kind 邊界，未把 collateral／definition 混入 offense loop。
- 下一個可進入 offense-core 的 parent route：`computer`，仍須由 controller 鎖定 child route。

## 2026-10-27：財產罪橫向驗收—偽造盜用公印或公印文第218條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`forgery_218_official_seal`；第210至217、219至220條及程序路線保留為相鄰／另案處理，未混入本單一路線。
- C02至C05分開確認公印／公印文、公署或機關、來源、形成／使用方式、公署／機關關聯與損害風險；所有單題不產生 `ACTIVE` 或法律結論。
- `UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`；`CASE_HUMAN_GATE` 仍為 `REQUIRED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`2764AD022E10EF9810A7FFB885477E54244A2BA21AB0233217060993B47E105B`。
- submission SHA-256：`0E70861D4FA25BFDFEE8590EEB297F851B32A2D8E20BC29E88321DD0951EA467`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route `forgery_219_confiscation` 為 collateral 路線，需另行邊界處理，不自動納入犯罪構成要件題組。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—偽造盜用印章印文或署押第217條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`forgery_217_seal_signature`；第210至216、218至220條及程序路線保留為相鄰／另案處理，未混入本單一路線。
- C02至C05分開確認印章、印文或署押種類、權利人、授權範圍、形成／使用方式、授權關聯與損害風險；所有單題不產生 `ACTIVE` 或法律結論。
- `UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`；`CASE_HUMAN_GATE` 仍為 `REQUIRED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`117982BA471DBBF4E9C0705219AE380AE84ADBD70CB2D85368562961CEC98439`。
- submission SHA-256：`6ACCC2890C931D6BDDE386EEBC31695F36C6248512E87BC7604AE23C55EB42CF`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；由 controller 依佇列鎖定下一路線。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—業務上文書不實登載第215條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`forgery_215_business_false_entry`；第210至214、216至220條及程序路線保留為相鄰／另案處理，未混入本單一路線。
- C02至C05分開確認業務身分、業務上文書、不實登載內容、業務關聯與損害風險；所有單題不產生 `ACTIVE` 或法律結論。
- `UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`；`CASE_HUMAN_GATE` 仍為 `REQUIRED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed。
- archive_equal：`True`；歸檔SHA-256：`D02E23C01F63F273A531EB2A18DE3AF42D23D65D9FC55D79EA2A6F731A402FF8`。
- submission SHA-256：`D5C5D9A19E709285ED20C54AB74A1222C3E970FA7D0EA74947B727768BE49B2A`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；由 controller 依佇列鎖定下一路線。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-28：財產罪橫向驗收—行使偽造變造或登載不實文書第216條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`forgery_216_use_document`；第210至215條基礎文書、印章、沒收與文書定義路線分開處理。
- C02確認行使文書來源與使用狀態，C03確認文書是否置於可發生內容效用的狀態；C04-C05分開保留對來源／不實內容的認識、使用關聯及證據來源。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`DC3FA32F5DAFCB60A8E3CF8AC769D9D1B44EC0DFA828D5BCB5427FD864828091`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；第217、218條印章、第219條沒收及第220條定義路線仍須分別處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-28：財產罪橫向驗收—使公務員登載不實第214條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`forgery_214_cause_official_false_entry`；第210至213條及行使、印章、沒收與文書定義路線分開處理。
- C02確認向公務員提出不實事項，C03確認使公務員將不實事項登載於職務上掌管公文書；C04-C05分開保留損害風險、提出與登載因果及證據來源。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`2300D7DEAC95D3BBB85590082BEB87D4BB6B14FF49047D0FB5DC15FBF0BD0FD0`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；其餘偽造、行使、印章、沒收與定義路線仍須分別處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-28：財產罪橫向驗收—公務員登載不實第213條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`forgery_213_official_false_entry`；第210、211、212、214條及行使、印章、沒收與文書定義路線分開處理。
- C02確認公務員身分、職務及公文書掌管，C03確認明知不實而登載；C04-C05分開保留損害風險、職務權限、行為與風險關聯及證據來源。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`53CAAFB018D19591DABBF5381D23EE8D2D1618DCFE780E66BA1CD9C27CA56122`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；第214條及其行使、印章、沒收與定義路線仍須分別處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-28：財產罪橫向驗收—偽造變造特種文書第212條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`forgery_212_certificate`；第210、211、213、214條及行使、印章、沒收與文書定義路線分開處理。
- C02確認護照、旅券、免許證、特許證或其他法定相類證書的偽造變造，C03確認損害風險；C04-C05分開保留文件種類、製作名義、權限、行為與風險關聯及證據來源。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`8B37DAE0FDFE69D189DCB4DB85CB64C2F0F1374BF52A99DF4FF1777E45BF4BDB`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；第213、214條及其行使、印章、沒收與定義路線仍須分別處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-28：財產罪橫向驗收—偽造變造公文書第211條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`forgery_211_public_document`；第210、212、213、214條及行使、印章、沒收與文書定義路線分開處理。
- C02確認公文書偽造變造，C03確認足以生損害於公眾或他人的風險；C04-C05分開保留製作機關、名義、內容、權限、行為與風險關聯及證據來源。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`0D8F6C4D7CDBD94A5FD28D4EE828D3D43D1F1F4C423BE970650097C9B0062343`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；第212、213、214條及其行使、印章、沒收與定義路線仍須分別處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—偽造變造私文書第210條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`forgery_210_private_document`；第211、212、213、214條及行使、印章、沒收與文書定義路線分開處理。
- C02確認私文書偽造變造，C03確認足以生損害於公眾或他人的風險；C04-C05分開保留製作名義、內容、權限、行為與風險關聯及證據來源。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`FB29E45415FAF50CD885B047A1625888F3AC0E26C45D36E9179B3C004A7ADEBD`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；第211、212、213、214條及其行使、印章、沒收與定義路線仍須分別處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—損害信用第313條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`defamation_313_credit`；第309、310、311、312條及第314條告訴條件分開處理。
- C02確認散布流言或施用詐術，C03確認他人信用受損；C04-C05分開保留傳播工具、損害程度、因果關係及證據來源。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`A7D8C60E9EFDA204A77E2453AD52059934BC1D939AE95E1AE4F30F2BAEF24E04`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；第311條例外與第314條程序仍須分別處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—侮辱或誹謗已死之人第312條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`defamation_312_deceased`；第309、310、311、313條及第314條告訴條件分開處理。
- C02確認對象為已死之人，C03確認公然侮辱或誹謗內容；C04-C05分開保留傳播、表意內容、死者名譽影響及證據來源。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`BA6C70502022B9BA20096C5A1AC4F457BB94CB9593164473C88F48C566647190`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；第313條信用、第311條例外與第314條程序仍須分別處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—誹謗第310條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`defamation_310_defamation`；第309條公然侮辱、第311條善意言論、第312條死者、第313條信用及第314條告訴條件分開處理。
- C02確認指摘或傳述具體事項，C03確認散布於眾及散布方式；C04-C05分開保留名譽損害、真實性、公共利益、私德範圍及證據來源。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`4ECD4E0138B5A7507B6125633EEC641D9F4DAB2FE9B267C0E57A373A507E658B`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；第312、313條及第311條例外、第314條程序仍須分別處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—公然侮辱第309條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`defamation_309_public_insult`；第310條誹謗、第311條善意言論、第312條死者、第313條信用及第314條告訴條件分開處理。
- C02確認言論內容與被害人，C03確認公然性與表意脈絡；C04-C05分開保留一般人可合理忍受範圍、言論價值及證據來源，並記錄第309條憲法限縮狀態。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`82F7E2C259B711F5D03448D64E8D64EB5BF77C8E2B3E73916635513113C19B48`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；第310、312、313條及第311條例外、第314條程序仍須分別處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—恐嚇取財或得利第346條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`intimidation_346_property`；第305條恐嚇危害安全、詐術損害、一般物毀損、傷害及程序路線維持相鄰比較，不混入候選。
- C02確認恐嚇內容與被害人／財物關係，C03確認財物交付或不法利益，C04確認不法所有意圖；C05另保留財產流向及既遂／未遂資料。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`E17A1714856D8968D17C01825768020F7187726E9AAE514AB3F9C603557C7686`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；恐嚇取財路線已完成本輪 child route 審查。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—恐嚇危害安全第305條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`intimidation_305_safety`；恐嚇取財第346條、詐術損害、傷害、一般物毀損及程序路線維持相鄰比較，不混入候選。
- C02確認恐嚇內容與傳達對象，C03確認傳達方式及對象；C04-C05分開保留安全危害、行為與危害關聯及證據來源。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`A9DA8375F5FB037D1CC3B7745940C81494CFB0C3B1DC2BF0B43EE1F7E265B1BD`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；`intimidation_346_property` 後續另行處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—詐術使人處分財產致損害第355條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`damage_355_fraud`；文書毀損、一般物毀損、建築物毀損及第357條程序路線維持相鄰比較，不混入候選。
- C02確認損害意圖與財產處分關係，C03確認詐術及財產處分行為；C04-C05分開保留財產損害、因果關係及證據來源。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`92AAE4B7F4A6FA544C92EFB6F1725BCB29914A32E036D7745E99150213DB7D95`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；第357條程序路線仍依 work queue 邊界另行處理。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—一般物毀損第354條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`damage_354_property`；文書毀損、建築物毀損、詐術損害及第357條程序路線維持相鄰比較，不混入候選。
- C02確認他人之物及所有／持有狀態，C03確認毀棄、損壞或致令不堪用的具體行為；C04-C05分開保留損害結果、行為與損害關聯及證據來源。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：待本輪全量驗證；Node前端與 JavaScript syntax 沿用既有證據。
- exact重複：內部0、既有來源0；歸檔SHA-256：`0E7512D003676C2506E25E6DA2702ECC8A5AFAE68D010FBBA98104F481868FB0`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 鎖定為 `damage_355_fraud`，仍須由 controller 選取後逐一路由驗收。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—毀壞建築物礦坑船艦第353條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`damage_353_building`；分開設計建築物、礦坑或船艦客體、毀壞或不堪使用行為、死亡／重傷結果、可預見性與因果關聯。
- 文書毀損、一般物毀損、詐術損害、損害債權及第357條程序路線未混入本題組。
- 單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- archive SHA-256：`AEEF1A96AC6111408B2BF4D4D3CFF02F9DBD86D72C779365F8B8415FDFBE7669`；與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route：由 controller 依鎖定 queue 選取；目前尚未自動前進。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—毀損他人文書第352條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`damage_352_document`；分開設計文書身分、毀棄損壞或不堪使用行為、足以生損害於公眾或他人的風險、關聯與證據來源。
- 一般物毀損、建築物毀損、詐術損害、損害債權及第357條程序路線未混入本題組。
- 單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- archive SHA-256：`62244333E6BDDB74A05C11D3720638B4F08C3F0FF73FEB0B89251F742FF9114B`；與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route：由 controller 依鎖定 queue 選取；目前尚未自動前進。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—凌虐或妨害未成年人身心發育第286條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`injury_286_child_abuse`；分開設計未成年人年齡身分、凌虐或妨害身心發育行為、營利意圖、死亡／重傷結果、因果關聯與證據來源。
- 普通傷害、重傷害、過失傷害、聚眾鬥毆及第287條程序路線未混入本題組。
- 單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- archive SHA-256：`A43D8C1AA2963C5E66F3E6A6B6559E269C453DAFF99A9D3862508FF3615FBC0E`；與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route：由 controller 依鎖定 queue 選取；目前尚未自動前進。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—過失傷害第284條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`injury_284_negligent`；分開設計注意義務與可預見性、違反行為、不作為或替代措施、傷害／重傷結果、因果關聯與證據來源。
- 普通傷害、重傷害、義憤、身分加重、聚眾鬥毆、兒少保護及第287條程序路線未混入本題組。
- 單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- archive SHA-256：`B64F8F87368126F249B90CCDE5AE20CAC64E20B1726D00E789FBF1F22F03554E`；與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route：由 controller 依鎖定 queue 選取；目前尚未自動前進。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—聚眾鬥毆在場助勢第283條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`injury_283_group_fight`；分開設計聚眾鬥毆事件、在場位置、助勢角色、死亡／重傷結果、因果關聯與證據來源。
- 普通傷害、重傷害、義憤、身分加重、過失傷害、兒少保護及第287條程序路線未混入本題組。
- 單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- archive SHA-256：`BC5D0BE996507368FB5B12F9B179FBDBA067E75DF13B166DDF1073E6D9AB1A71`；與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route：由 controller 依鎖定 queue 選取；目前尚未自動前進。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—受囑託承諾傷害或加工自傷第282條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`injury_282_requested_self_harm`；分開設計囑託、承諾、教唆或幫助態樣、本人意思形成、死亡／重傷結果、因果關聯與證據來源。
- 普通傷害、重傷害、義憤、身分加重、過失傷害、兒少保護及第287條程序路線未混入本題組。
- 單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁；archive SHA-256：`1D1AC580E9A2DEE2C86EDD65772B9EAE27C35546E3C8DCAF42A7D4152B35BAAF`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route：`injury_283_group_fight`。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—對直系血親尊親屬施強暴未成傷第281條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`injury_281_violence_ancestor`；分開設計施強暴行為、被害人直系血親尊親屬身分、未造成傷害結果、身分證據與事件關聯。
- 普通傷害、重傷害、義憤、過失傷害、兒少保護及第287條程序路線未混入本題組。
- 單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁；archive SHA-256：`4BBA4E6C85CD2D7A5BE01037A5B71631D98E1781676E9A50DD9DC44684D54AE0`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route：`injury_282_requested_self_harm`。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—對直系血親尊親屬傷害加重第280條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`injury_280_ancestor`；分開設計第277／278條基礎傷害、被害人直系血親尊親屬身分、身分證據與基礎行為關聯。
- 普通傷害、重傷害、義憤、過失傷害、兒少保護及第287條程序路線未混入本題組。
- 單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁；archive SHA-256：`82C2B18667CD171182FF8E3D3ED37D44BBEA1B96A12973C1AC06E2CA50FCE8C8`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route：`injury_281_violence_ancestor`。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—當場激於義憤傷害第279條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`injury_279_righteous_indignation`；分開設計第277／278條基礎行為、當場性、激於義憤事件脈絡、死亡結果、關聯與證據來源。
- 普通傷害、重傷害、身分加重、過失傷害、兒少保護及第287條程序路線未混入本題組。
- 單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁；archive SHA-256：`2D564A69A421E1381C9F312FEB52010DB04F9D93718E79CF3C1BB16108B89723`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route：`injury_280_ancestor`，屬身分加重路線，須與基礎行為分開審核。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—重傷害第278條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`injury_278_serious`；分開設計重傷行為、重傷結果與因果、死亡結果、未遂／既遂與證據來源。
- 普通傷害、義憤、身分加重、過失傷害、兒少保護及第287條程序路線未混入本題組。
- 單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁；archive SHA-256：`A2635A963EE560A627A561B48A9B8D0FF35E31C45F2FFAF9D56B0F9C3DD515CC`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route：`injury_279_righteous_indignation`。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—普通傷害及結果加重第277條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`injury_277_general`；分開設計傷害行為、傷害結果與因果、死亡／重傷結果、進度與證據來源。
- 重傷、義憤、身分加重、過失傷害、兒少保護及第287條程序路線未混入本題組。
- 單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁；archive SHA-256：`25DB54D5452CD899DEFE924C2FB14262F1AD7370B5B65BAA18CA0468839E6AA0`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route：`injury_278_serious`。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—加重重利第344條之1

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`fraud_344_1_aggravated_usury`；以第344條重利基礎行為、加重方法、重利結果、方法關聯、進度與證據來源分開設計。
- 強暴、脅迫、恐嚇、侵入住宅、傷害、毀損、監控或相類方法只作外部事實整理，不由單一方法名稱直接產生法律結論。
- 單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁；archive SHA-256：`45B601485DDBF5969AEF13224FE0CBECF6DAF452DA640C417699986D7062642A`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；fraud parent 的 substantive child routes 已完成本輪列示範圍，343仍為程序分流。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—重利第344條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`fraud_344_usury`；分開設計急迫／輕率／無經驗／難以求助處境、貸與、顯不相當重利、借貸相關費用、交易脈絡、進度與證據來源。
- 詐欺、侵占、背信與加重重利只作相鄰比較；第343條程序路線未混入犯罪構成要件題組。
- 單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁；archive SHA-256：`4EC2D21FB275073F1F2289A4088ED0FA6F9765C4E20915B7027D371B9C677F92`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 為 `fraud_344_1_aggravated_usury`，仍須逐一路由審核。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—背信第342條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`fraud_342_breach_of_trust`；分開設計為他人處理事務關係、任務界線、違背行為、利益／損害目的、損害結果、進度與證據來源。
- 詐欺、侵占、竊盜與重利只作相鄰比較；第343條程序路線未混入犯罪構成要件題組。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；exact重複：內部0、既有來源0。
- LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁；archive與工作單SHA-256一致：`B35F380B91E4486C963F17FCE91C74F26FD7AE58787FECD52DAC1E8935FB8C63`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 crosswalk child route 是程序路線 `fraud_343_property_family_rules`，不進犯罪構成要件製作 loop。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—乘機詐欺第341條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`fraud_341_exploitation`；以客觀脆弱處境、利用關聯、財產處分、意圖、進度與證據來源分開設計八個 concepts。
- 第339條一般詐欺、第339條之1至之3只作相鄰比較；不混入設備、電腦、背信、重利或程序路線。
- C02不由年齡、認知描述或單一說法直接產生ACTIVE；C03另確認利用與財產處分的外部因果脈絡。獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁。
- exact重複：內部0、既有來源0；archive與工作單SHA-256一致：`C57994B67CB7BFDC6753E8BAB2EE80FF4B0125C23500F4E6349E31787E1CC89A`。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 controller 鎖定 child route：`fraud_342_breach_of_trust`。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—一般詐欺第339條

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`fraud_339_general`；設備、電腦、加重、乘機、背信、重利及第343條程序路線未納入。
- 8 concepts 分開確認詐術、錯誤、財產處分、損害流向、不法所有意圖、行為進度與證據來源；不以不履約、付款或損害單獨推定詐欺。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與未列入 scope 的相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed；Node前端：31 passed；JavaScript syntax：PASS。
- exact重複：內部0、既有來源0；LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁。
- `/api/health`：HTTP 200。
- 歸檔SHA-256：`192C5D75860732C03B40F0E576461260E4C7E689E13DCB71D2C64316FAC05034`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；設備／電腦／加重等 route 必須逐一由 controller 鎖定，不批次展開。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—收費設備詐欺第339條之1

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`fraud_339_1_charge_device`；一般詐欺、電腦詐欺、加重詐欺、乘機詐欺、背信、重利及第343條程序路線未混入。
- C02與C03分開確認收費設備不正操作及取得財物或不法利益；其餘概念保留結果、流向、意圖、進度與證據來源的人工審核邊界。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed；Node前端：31 passed；JavaScript syntax：PASS。
- exact重複：內部0、既有來源0；LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁。
- 歸檔SHA-256：`5C804989A49803C5071FEA2D5A62EBC244433725FAA0B23E0F2FD163F8743422`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；電腦、加重、乘機、背信、重利及程序路線必須逐一由 controller 鎖定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—電腦詐欺第339條之3

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`fraud_339_3_computer`；一般詐欺、收費設備、自動付款設備、加重詐欺、乘機詐欺、背信、重利及第343條程序路線未混入。
- C02與C03分開確認輸入虛偽資料或不正指令及取得財物或不法利益；其餘概念保留系統影響、流向、意圖、進度與證據來源的人工審核邊界。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed；Node前端：31 passed；JavaScript syntax：PASS。
- exact重複：內部0、既有來源0；LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁。
- `/api/health`：HTTP 200。
- 歸檔SHA-256：`4E2BF050E961EAA5AFF854DADD913502DE50C0FCA744FA502615843C987CF531`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；加重、乘機、背信、重利及程序路線必須逐一由 controller 鎖定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—加重詐欺第339條之4

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`fraud_339_4_aggravated`；一般詐欺及第339條之1至之3、乘機詐欺、背信、重利與第343條程序路線分開處理。
- C02確認第339條之4列舉加重態樣，C03另確認第339條基礎詐欺行為；加重態樣不能取代基礎行為。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed；Node前端：31 passed；JavaScript syntax：PASS。
- exact重複：內部0、既有來源0；LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁。
- 歸檔SHA-256：`17A029B78682F6271EDC98269C505F434C2DC6665058D7BAFD8546045A76ED73`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；乘機、背信、重利及程序路線必須逐一由 controller 鎖定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

## 2026-10-27：財產罪橫向驗收—自動付款設備詐欺第339條之2

execution_mode: `REVIEWED_PIPELINE`
agent_mode: `SINGLE_AGENT_MODE / independent model identity UNVERIFIED`
triggers: `S3`、`S4`

### DESIGN / REVIEW

- 目標：`fraud_339_2_payment_device`；一般詐欺、收費設備詐欺、電腦詐欺、加重詐欺、乘機詐欺、背信、重利及第343條程序路線未混入。
- C02與C03分開確認自動付款設備不正操作及取得財物或不法利益；其餘概念保留結果、流向、意圖、進度與證據來源的人工審核邊界。
- 所有單題不產生 `ACTIVE` 或 `EXCLUDED`；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。本 route 未使用獨立 Sol 工具面，保留 `UNVERIFIED`。

### TEST / ARCHIVE

- 契約與 offense linkage：15 passed；Full pytest：630 passed；Node前端：31 passed；JavaScript syntax：PASS。
- exact重複：內部0、既有來源0；LibreOffice 20題：victim 2頁、suspect 3頁、transfer 3頁。
- `/api/health`：HTTP 200。
- 歸檔SHA-256：`0B97EE3F02CC09F5F6A09DE16B271C4CFC7EE2D5667E9643FDD9645FE0329DDF`，與工作單逐位元一致。

### DEPLOY / MAINTAIN

- `SKIPPED_WITH_REASON`：未修改runtime、未部署、條陳格式設定仍暫停、未取代個案 `CASE_HUMAN_GATE`。
- 下一個 child route 尚未選定；電腦、加重、乘機、背信、重利及程序路線必須逐一由 controller 鎖定。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`
