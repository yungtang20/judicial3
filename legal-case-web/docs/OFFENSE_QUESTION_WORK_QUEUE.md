# 罪章問句製作工作佇列

```yaml
document_status: ACTIVE_WORK_QUEUE
runtime_enabled: false
review_status: CODEX_REVIEW_REQUIRED
source_of_truth:
  - data/question_bank.json
  - data/legal_route_crosswalk.json
law_identity_index: docs/LAW_REGISTRY.md
current_target: NONE_SELECTED
current_parent_route: obstruction
queue_status: READY_FOR_CONTROLLER_AUTO_SELECTION
last_archived_target: obstruction_138_official_property
next_locked_target: obstruction_139_seal_seizure
active_question_ruleset: UNCHANGED_RUNTIME
candidate_question_ruleset: question-rules-v2-draft
candidate_ruleset_status: QUESTION_DESIGN_ACCEPTED
candidate_ruleset_acceptance_scope: QUESTION_DESIGN_ONLY
runtime_ruleset_status: UNCHANGED_RUNTIME
route_auto_advance: true
runtime_auto_advance: false
user_review_mode: FINAL_BATCH_ONLY
active_work_item: docs/QUESTION_WORK_ITEM.md
```

## 1. 這份文件回答什麼

本文件只管理其他 AI 需要處理的 runtime route 與工作狀態，不維護法規版本或自然語言命令。法規身分與版本線索查 [LAW_REGISTRY.md](LAW_REGISTRY.md)；新增／更新法規查 [LAW_LIFECYCLE.md](LAW_LIFECYCLE.md)。`question_bank.json` 目前有 44 個 parent routes；其中 substantive 或 mixed routes 才能進入罪章問句製作，procedural／protective routes 只能建立程序或保護流程問句，不得冒充犯罪構成要件題組。

這份佇列不代表各 route 已完成法律核對。使用者核准整體製作範圍後，由 controller 依表列順序一次選定一個 `target_child_route_id`；執行 AI 不能自行選擇或批次生成。Codex 完成該 route 審核、歸檔且無 blocker 後，controller 才可選取下一個。使用者只審核整批最終成果。

## 2. 單次工作的選取規則

1. `current_target` 為 `NONE_SELECTED` 時，任何 AI 都不得開始產生問句。
2. 每次只能選一個 parent route。
3. `SPLIT_REQUIRED` 不得直接製作整章問卷。先讀取 crosswalk，再一次選一個 offense／aggravation child route。
4. `PARTIAL_SCOPE` 也不得推定整章已涵蓋。只處理 crosswalk 明列的 child route。
5. `PROCEDURAL_ONLY` 與 `PROTECTIVE_UMBRELLA` 不進入罪章問句製作 loop。
6. 完成一個工作單元後，狀態只能變成 `READY_FOR_REVIEW`，由 Codex 審核。
7. Codex 審核通過並完成歸檔後，由 controller 依鎖定 queue 指定下一個工作單元，不需逐 route 請使用者核准。
8. 禁止從本表第一列開始自動跑到最後一列。
9. 收到新增／更新法規命令時，不得直接改本佇列；先完成法規生命週期的查重、分類與 Human Gate。
10. 問法、角色、相鄰路由或回答效果發生 `SYSTEMIC_RULE_DEFECT` 時，停止全佇列；不得把同一錯誤複製到下一罪章。
11. 規則修改後，以同一基準 child route 重新從 iteration 0 校準，不計入單一罪章兩輪內容修正上限；但同一 defect 只允許一次規則修正及一次重新校準。
12. 基準 route 未通過 Codex「下一罪章准入 Gate」前，`next_route` 固定為 `NOT_AUTHORIZED`。
13. 只有總範圍變更、官方來源無法確認、同一系統性缺陷重試失敗、需要 runtime／crosswalk 寫入或不可逆操作時，才中途請使用者決定。

## 3. 已有垂直切片，先審核而非重做

目前 `app/questions.py` 已有財物取走情境的中性事實問句及回答映射，涉及下列 routes：

| route_id | 現況 | 下一步 |
|---|---|---|
| `theft` | 已有受控 runtime vertical slice；crosswalk 為 `PARTIAL_SCOPE` | 先審核既有問句與 child route 覆蓋，不得整套重做 |
| `embezzlement` | 已有受控 runtime vertical slice；crosswalk 為 `PARTIAL_SCOPE` | 先審核既有問句與 child route 覆蓋，不得整套重做 |
| `robbery` | 已有財物取走區分映射；parent route 為 `SPLIT_REQUIRED` | 先拆搶奪、強盜等 child routes，再審核共用區分事實 |

`aggravated_theft` 沒有因與 theft 相鄰就自動完成。它仍須按 child route 及加重事由另行製作與審核。

## 4. Substantive／mixed 罪章製作佇列

下表列出 40 個可進入法律路由分析的 parent routes。順序沿用目前 `question_bank.json`，不是案件量或法律重要性的排名。

| queue_no | route_id | 顯示名稱 | route_type | crosswalk_status | child routes | 初始工作狀態 | 必要動作 |
|---:|---|---|---|---|---:|---|---|
| 1 | `theft` | 竊盜 | substantive | `PARTIAL_SCOPE` | 4 | `ARCHIVED_REVIEW_PASS` | 基準 child route 已完成 Codex review 並存入受控 archive；其餘 child routes 仍須逐一處理 |
| 2 | `aggravated_theft` | 加重竊盜 | substantive | `PARTIAL_SCOPE` | 1 | `ARCHIVED_REVIEW_PASS` | `aggravated_theft_321` 已完成 Codex review 並存入受控 archive |
| 3 | `embezzlement` | 侵占 | substantive | `PARTIAL_SCOPE` | 5 | `PROCEDURAL_ROUTE_SEPARATE_WORKFLOW` | `embezzlement_335_general`、`embezzlement_336_1_public`、`embezzlement_336_2_business`、`embezzlement_337_lost_property` 已歸檔；下一鎖定 `embezzlement_338_applicable` 為程序路線，須另行處理，不進犯罪構成要件題組 |
| 4 | `fraud` | 詐欺 | substantive | `SPLIT_REQUIRED` | 10 | `SUBSTANTIVE_CHILD_ROUTES_PROCESSED_WITH_PROCEDURAL_REMAINING` | `fraud_339_general`、`fraud_339_1_charge_device`、`fraud_339_2_payment_device`、`fraud_339_3_computer`、`fraud_339_4_aggravated`、`fraud_341_exploitation`、`fraud_342_breach_of_trust`、`fraud_344_usury`、`fraud_344_1_aggravated_usury` 已歸檔；`fraud_343_property_family_rules` 為程序分流，尚未建立程序工作單 |
| 5 | `injury` | 傷害 | substantive | `SPLIT_REQUIRED` | 10 | `READY_FOR_CONTROLLER_AUTO_SELECTION` | `injury_277_general` 至 `injury_286_child_abuse` 已歸檔；下一鎖定 `injury_287_complaint` 為程序路線，須另行處理 |
| 6 | `damage` | 毀損 | substantive | `PARTIAL_SCOPE` | 6 | `READY_FOR_CONTROLLER_AUTO_SELECTION` | `damage_352_document`、`damage_353_building`、`damage_354_property`、`damage_355_fraud` 已歸檔；第357條程序路線另行保留 |
| 7 | `intimidation` | 恐嚇／妨害自由 | substantive | `SPLIT_REQUIRED` | 2 | `READY_FOR_CONTROLLER_AUTO_SELECTION` | `intimidation_305_safety`、`intimidation_346_property` 已歸檔 |
| 8 | `defamation` | 妨害名譽 | substantive | `SPLIT_REQUIRED` | 6 | `READY_FOR_CONTROLLER_AUTO_SELECTION` | `defamation_309_public_insult`、`defamation_310_defamation`、`defamation_312_deceased`、`defamation_313_credit` 已歸檔；第311條例外與第314條程序分開 |
| 9 | `forgery` | 偽造文書 | substantive | `SPLIT_REQUIRED` | 11 | `READY_FOR_CONTROLLER_AUTO_SELECTION` | `forgery_210_private_document` 至 `forgery_218_official_seal` 已歸檔（含補列 `forgery_215_business_false_entry`）；第219條 collateral 與第220條 definition 已留下邊界紀錄、不進 offense-core；下一個可製作 parent route 為 `computer` |
| 10 | `computer` | 妨害電腦使用 | substantive | `SPLIT_REQUIRED` | 6 | `READY_FOR_CONTROLLER_AUTO_SELECTION` | `computer_358_intrusion`、`computer_359_data_change`、`computer_360_interference`、`computer_362_malware` 已歸檔；第361條 aggravation 與第363條 procedure 已留下邊界紀錄；下一個 parent route 為 `sexual_harassment` |
| 11 | `sexual_harassment` | 性騷擾 | mixed | `SPLIT_REQUIRED` | 5 | `READY_FOR_CONTROLLER_AUTO_SELECTION` | offense route `sexual_harassment_25_unwanted_touch` 已歸檔；第2條 classification、第7至17條 procedure、第26至30條 administrative 已留下邊界紀錄；下一個 parent route 為 `stalking` |
| 12 | `stalking` | 跟蹤騷擾／違反保護令 | mixed | `PARTIAL_SCOPE` | 5 | `READY_FOR_CONTROLLER_AUTO_SELECTION` | offense routes `stalking_18_offense`、`stalking_19_protection_order` 已歸檔；第3、4至17、20至21條分類／保護／程序已留下邊界紀錄；下一個 parent route 為 `public_danger` |
| 13 | `public_danger` | 公共危險／酒駕 | substantive | `PARTIAL_SCOPE` | 2 | `READY_FOR_CONTROLLER_AUTO_SELECTION` | `public_danger_185_3_impaired_driving`、`public_danger_185_4_hit_and_run` 已歸檔；下一個 parent route 為 `drugs`，不宣稱公共危險章完整 |
| 14 | `drugs` | 毒品案件 | substantive | `SPLIT_REQUIRED` | 8 | `READY_FOR_CONTROLLER_AUTO_SELECTION` | `drugs_4_manufacture_transport_sale` 至 `drugs_8_transfer`、`drugs_10_use`、`drugs_11_possession` 已歸檔；第9條 aggravation 已保留邊界；下一個 parent route 為 `state_security` |
| 15 | `state_security` | 內亂／外患／妨害國交 | substantive | `SPLIT_REQUIRED` | 21 | `READY_FOR_CONTROLLER_AUTO_SELECTION` | `state_security_100_insurrection` 至 `state_security_118_foreign_symbol` 已依 child route 逐一歸檔；第102、107、115之1、116、119 等邊界路線分開處理；下一個 parent route 為 `duty` |
| 16 | `duty` | 瀆職 | substantive | `SPLIT_REQUIRED` | 15 | `READY_FOR_CONTROLLER_AUTO_SELECTION` | `duty_120_abandon_post` 至 `duty_134_official_aggravation` 已歸檔；瀆職罪章 child routes 已完成，下一個 parent route 為 `obstruction` |
| 17 | `obstruction` | 妨害公務 | substantive | `SPLIT_REQUIRED` | 7 | `READY_FOR_CONTROLLER_AUTO_SELECTION` | `obstruction_135_violence_threat` 至 `obstruction_138_official_property` 已歸檔；下一鎖定 `obstruction_139_seal_seizure`；第140條部分與第141條之1維持失效／排除邊界 |
| 18 | `judicial_integrity` | 妨害司法公正 | substantive | `SPLIT_REQUIRED` | 3 | `CHILD_SELECTION_REQUIRED` | 依現行 child route 分開；不得使用失效或未生效規範 |
| 19 | `voting` | 妨害投票 | substantive | `SPLIT_REQUIRED` | 7 | `CHILD_SELECTION_REQUIRED` | 賄選、強暴脅迫、投票秘密及其他 child route 分開 |
| 20 | `disorder` | 妨害秩序 | substantive | `SPLIT_REQUIRED` | 12 | `CHILD_SELECTION_REQUIRED` | 聚眾、公然聚集、結社等不同 child route 分開 |
| 21 | `escape` | 脫逃／藏匿人犯 | substantive | `SPLIT_REQUIRED` | 5 | `CHILD_SELECTION_REQUIRED` | 脫逃、縱放、便利脫逃及藏匿人犯分開 |
| 22 | `evidence` | 湮滅證據 | substantive | `SPLIT_REQUIRED` | 3 | `CHILD_SELECTION_REQUIRED` | 證據行為、親屬減免等 child route 分開 |
| 23 | `accusation` | 偽證／誣告 | substantive | `SPLIT_REQUIRED` | 5 | `CHILD_SELECTION_REQUIRED` | 偽證、虛偽鑑定／通譯、誣告及自白減免分開 |
| 24 | `currency` | 偽造貨幣 | substantive | `SPLIT_REQUIRED` | 6 | `CHILD_SELECTION_REQUIRED` | 製造、行使、收集、器械及減免 child route 分開 |
| 25 | `securities` | 偽造有價證券 | substantive | `SPLIT_REQUIRED` | 6 | `CHILD_SELECTION_REQUIRED` | 有價證券、郵票／印花、行使及器械等 child route 分開 |
| 26 | `weights_measures` | 偽造度量衡 | substantive | `SPLIT_REQUIRED` | 4 | `CHILD_SELECTION_REQUIRED` | 偽造變造、販賣使用及沒收等 child route 分開 |
| 27 | `sexual` | 妨害性自主 | substantive | `SPLIT_REQUIRED` | 12 | `CHILD_SELECTION_REQUIRED` | 各犯罪、年齡、手段、身分及結果不得共用問卷；敏感性審查先行 |
| 28 | `obscenity` | 妨害風化 | substantive | `SPLIT_REQUIRED` | 3 | `CHILD_SELECTION_REQUIRED` | 依營利媒介、場所或其他 child route 分開 |
| 29 | `marriage` | 妨害婚姻及家庭 | substantive | `SPLIT_REQUIRED` | 8 | `CHILD_SELECTION_REQUIRED` | 重婚、和誘、略誘、收受被誘人等 child route 分開 |
| 30 | `graves_religion` | 褻瀆祀典／侵害墳墓屍體 | substantive | `SPLIT_REQUIRED` | 5 | `CHILD_SELECTION_REQUIRED` | 祭祀、墳墓、屍體／遺骨等 child route 分開 |
| 31 | `agriculture_commerce` | 妨害農工商 | substantive | `SPLIT_REQUIRED` | 5 | `CHILD_SELECTION_REQUIRED` | 農工商商品、標記、秘密或其他 child route 分開 |
| 32 | `opium` | 鴉片 | substantive | `SPLIT_REQUIRED` | 10 | `CHILD_SELECTION_REQUIRED` | 刑法章內路由與毒品特別法競合先查證，再逐 child route 製作 |
| 33 | `gambling` | 賭博 | substantive | `SPLIT_REQUIRED` | 4 | `CHILD_SELECTION_REQUIRED` | 一般賭博、營利場所、聚眾等 child route 分開 |
| 34 | `homicide` | 殺人／過失致死 | substantive | `SPLIT_REQUIRED` | 7 | `CHILD_SELECTION_REQUIRED` | 故意、義憤、母殺嬰、加工自殺及過失致死等 child route 分開 |
| 35 | `abortion` | 墮胎 | substantive | `SPLIT_REQUIRED` | 5 | `CHILD_SELECTION_REQUIRED` | 孕婦自行、他人加工、未得同意及結果加重等 child route 分開 |
| 36 | `abandonment` | 遺棄 | substantive | `SPLIT_REQUIRED` | 4 | `CHILD_SELECTION_REQUIRED` | 一般遺棄、依法令契約義務及結果加重等 child route 分開 |
| 37 | `liberty` | 妨害自由 | substantive | `SPLIT_REQUIRED` | 15 | `CHILD_SELECTION_REQUIRED` | 私行拘禁、強制、恐嚇、擄人勒贖等不同 child route 分開 |
| 38 | `privacy` | 妨害秘密／性隱私 | substantive | `SPLIT_REQUIRED` | 16 | `CHILD_SELECTION_REQUIRED` | 通訊、秘密、電磁紀錄、性影像及程序 child route 分開；敏感性審查先行 |
| 39 | `robbery` | 搶奪／強盜／海盜 | substantive | `SPLIT_REQUIRED` | 8 | `EXISTING_REVIEW_REQUIRED` | 財物取走共用區分題先審核，再分搶奪、強盜、準強盜、海盜等 child route |
| 40 | `trafficking` | 人口販運 | mixed | `SPLIT_REQUIRED` | 13 | `CHILD_SELECTION_REQUIRED` | 犯罪、被害人保護、鑑別與程序不得合併；敏感性審查先行 |

## 5. 不得當作罪章題組的程序／保護路由

下列 4 個 parent routes 仍需流程或保護性問句，但不進入「構成要件罪章問句」製作佇列。

| route_id | 顯示名稱 | route_type | crosswalk_status | child routes | 處理方式 |
|---|---|---|---|---:|---|
| `juvenile` | 少年事件 | procedural | `PROCEDURAL_ONLY` | 4 | 另建少年程序與權利保障流程，不製作定罪題組 |
| `domestic_violence` | 家庭暴力／違反保護令 | protective | `PROTECTIVE_UMBRELLA` | 5 | 先處理安全、保護令與轉介；犯罪路由回到對應 substantive route |
| `child_protection` | 兒少保護／性剝削 | protective | `PROTECTIVE_UMBRELLA` | 5 | 先處理兒少安全與保護程序；犯罪路由分別建模 |
| `gender_equality` | 職場／校園性別事件 | procedural | `PROCEDURAL_ONLY` | 6 | 另建通報、調查與程序問句，不作犯罪成立判斷 |

## 6. 每次交付的識別欄位

外部 AI 開始工作前，必須由人工填入：

```yaml
queue_no: <1-40>
target_route_id: <parent route id>
target_child_route_id: <crosswalk child route id; SPLIT_REQUIRED 時必填>
target_role: [victim, suspect, transfer, witness_review_only]
iteration: 0
allowed_output: WORK_ITEM_FILE_ONLY
allowed_write_path: docs/QUESTION_WORK_ITEM.md
ruleset_version: question-rules-v2-draft
ruleset_status: CALIBRATION_REQUIRED
designer_role: TW_CRIMINAL_INTERVIEW_QUESTION_DESIGN_EXPERT
target_interview_role: [victim, suspect, transfer, witness_review_only]
route_scope: <由 canonical 規則與 Codex reviewer 鎖定的 primary／comparison／alternative allowlist>
```

缺少 `target_child_route_id` 且 parent route 為 `SPLIT_REQUIRED` 時，AI 必須輸出 `CHILD_SELECTION_REQUIRED` 並停止。

完整問句、矩陣、案例及自我檢核只寫入 [QUESTION_WORK_ITEM.md](QUESTION_WORK_ITEM.md)。聊天不得重貼全文。工作檔尚未完成審核或未留下 SHA-256 與 Gate 決定時，不得覆蓋成下一個 route。

下一位 AI 接手時，以工作檔的 `resume_from_section` 為唯一開始點。若 `current_blockers` 非空，先處理或回報 blocker，不得重做前段、跳過審核或移動 `current_target`。

## 7. 狀態定義

| 狀態 | 意義 |
|---|---|
| `CHILD_SELECTION_REQUIRED` | 必須先由 crosswalk 選定 child route |
| `READY_FOR_CHILD_SELECTION` | 範圍較窄，但仍須確認要處理的 child route |
| `EXISTING_REVIEW_REQUIRED` | 已有部分 runtime 或審查內容，先審核缺口，不得重做 |
| `DESIGN_DRAFT` | 外部 AI 已產出待審查設計稿 |
| `READY_FOR_REVIEW` | 格式與自我檢查完成，等待 Codex 審核 |
| `CHANGES_REQUESTED` | Codex 指定有界線修正 |
| `BLOCKED_BY_RULESET` | 共通問法、角色、相鄰路由或回答效果有系統性缺陷，全佇列停止 |
| `INVALIDATED_BY_RULESET_CHANGE` | 舊產出依已失效規則生成，不能沿用為審查通過證據 |
| `BLOCKED_NEEDS_HUMAN_DECISION` | 同一規則缺陷重新校準仍失敗，不得再自動修改 |
| `REVIEW_PASS` | Codex 審核通過；仍不等於法律完整或 runtime 接線 |
| `BLOCKED` | 來源、範圍、文件衝突或兩次修正後仍無法安全完成 |

## 8. 佇列完成條件

單一工作單元只有在以下證據齊全時，才能由 Codex reviewer 將狀態改為 `REVIEW_PASS`：

- route 與 child route 範圍清楚。
- 官方法源與行為時法狀態可回查，或明確保留 `UNKNOWN`。
- 中性事實及相鄰路由矩陣完成。
- 每題有 `fact_target`、`distinction_axis`、`legal_targets` 及逐路由回答效果。
- victim、suspect、transfer 與 witness_review_only 已依知識範圍分別設計，不是只換稱謂。
- 題數、公司題保留、exact／semantic 重複、誘導與敏感性審查完成。
- UNKNOWN、衝突及基準案例均只產生保守候選狀態。
- 修正 loop 不超過兩次。
- `runtime_enabled` 仍為 `false`。
- 個案 `CASE_HUMAN_GATE` 未被自動化取代。

基準路由另須通過 [QUESTION_DESIGN_AND_USE.md](QUESTION_DESIGN_AND_USE.md) 第 12 節的下一罪章准入 Gate。規則集通過且產物歸檔後，由 controller 依已鎖定 queue 自動選取下一個 child route；執行 AI 不得自行前進。

`question-rules-v2-draft` 在 Gate 通過前不是 active ruleset，不得用來移動 `current_target`、建立下一罪章正式工作單或宣稱 runtime 已採用。

40 個 parent routes 全部完成也不代表法律體系完整。crosswalk 的 child routes、特別法、行為時法及個案競合仍須個別審查。
