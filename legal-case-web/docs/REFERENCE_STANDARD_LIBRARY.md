# Reference Standard Library

本文件作為已核准過的 `theft_320_1_movable` iteration 2 標準的存檔與索引。僅作為治理證據，不代表 runtime 生效，亦不代表下一個子路由已自動接續。

## 2026-10-26 theft_320_1_movable iteration 4 完整歸檔

```yaml
archive_id: QRA-TH320-1-MOV-20261026-01
archive_path: docs/evidence/question_route_archives/theft_320_1_movable-iteration-4-20261026.txt
archive_file_sha256: 9BCB4A012C2557504ACEAFBBAE2C9EA412877E26B0183E046B82C709DE7087A6
submission_sha256: 21807B231A1868BE9AA5565904471CE8A9C2DD1B5EE0B74A40CFE59EA30A6FA7
ruleset_file_sha256: DAF06F74D278165A436FDA028133EFC989A289A14660FEB4066B9BD8678DBB16
route_review_gate: PASS
ruleset_acceptance_scope: QUESTION_DESIGN_ONLY
runtime_ruleset_status: UNCHANGED_RUNTIME
case_human_gate: REQUIRED
user_final_acceptance: PENDING
```

完整內容不在本索引重貼；以 manifest 與 archive file hash 驗證可回復副本。此 PASS 不代表法律結論、runtime 自動接線、部署或實際個案 Human Gate。

---

## 2026-10-26 aggravated_theft_321 iteration 0 完整歸檔

```yaml
archive_id: QRA-AGT321-20261026-01
archive_path: docs/evidence/question_route_archives/aggravated_theft_321-iteration-0-20261026.txt
archive_file_sha256: 6B960B1224AF42B4683892F4600EC05F10AE42703BCA76E7ACDC712088FB2743
submission_sha256: 17DC2C8975944A33B7B74AF9D2BB414AC4A07BD03D031AAABEA650B926D665CD
route_review_gate: PASS
ruleset_acceptance_scope: QUESTION_DESIGN_ONLY
runtime_ruleset_status: UNCHANGED_RUNTIME
case_human_gate: REQUIRED
user_final_acceptance: PENDING
```

本索引不重貼完整問句；以 manifest 與 archive SHA-256 驗證可回復副本。下一 locked target 是 `embezzlement_335_general`，尚未在 active slot 生成。

---

## 2026-10-14 theft_320_1_movable iteration 2

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

### 獨立審查決策

- R1：`ACCEPT_WITH_MODIFICATIONS`；`questions/theft.md` 實際存在，E2E timeout 隔離重跑通過，其餘結構缺口納入修正。
- R2：`ACCEPT`；角色實體化、trigger、mapping、dedupe 與聚合契約均需修正。
- R3：`ACCEPT_WITH_MODIFICATIONS`；先合法持有可提高侵占候選，但返還、拒還或處分等必要事實未齊時，聚合結果維持 `NEED_REVIEW`。
- R4～R6：`ACCEPT`；同意範圍、witness 知識邊界及 fail-closed 校準均納入修正。

### 驗證

- 問句契約、question logic 與 RCQ loader：47 passed。
- E2E套件：2 passed，文件下載測試於整組執行時 timeout；該測試隔離重跑為 1 passed。合計 50 個唯一測試已有通過證據，但不是同一次整組全綠。
- 法務部官方刑法頁面於 2026-10-14 回查成功；本紀錄不取代行為時法與人工法律審查。
- Runtime、題庫接線及下一罪章均未獲授權，也未修改。

### 設計決策

- 建立 8 個 `theft_320_1_movable` 標準，依序涵蓋自由敘述、原持有、同意、先合法持有、遺失狀態、突然力量、暴力脅迫及抗拒能力。
- 使用 canonical exact child route IDs，移除 fraud、damage 及所有 parent／alias route ID。
- 將暴力脅迫與抗拒能力拆成兩個單一事實，避免一題同時回答手段及程度。
- Transfer 的移送來源、既有筆錄及刑事訴訟法第95條權利告知獨立為程序題，不作為犯罪構成要件。

### 驗證

- `tests/test_question_work_item_contract.py`：5 passed。
- 問句 contract、question logic、RCQ loader、E2E：46 passed。
- Markdown相對連結：PASS。
- `git diff --check`：PASS。
- 法律 effects、語意去重、行為時法及接線仍需 Human Gate；runtime未修改。

---

### 獨立審查補強

- 決策：`ACCEPT_WITH_MODIFICATIONS`；題數計算矛盾屬 systemic rule defect，其餘 route、條號、schema 及問句缺陷由新 iteration 修正。
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
- 文件修正完成不等於候選 ruleset 已通過；`theft_320_1_movable`校準與 Human Gate仍為 `NOT_RUN`。

### 影響範圍

- `QUESTION_DESIGN_AND_USE.md`
- `AI_EXECUTION_PROTOCOL.md`
- `OFFENSE_QUESTION_WORK_QUEUE.md`
- `README.md`
- Runtime 程式、題庫與資料 schema：本輪未修改。

---

## 保留且不得改名

- `CRIMINAL_OFFENSE_ROLE_CORE_QUESTIONS_ALL.md`、`RCQ_Human REVIEW_WORKSHEET.md`、`SEMANTIC_TEST_SET_REVIEW_WORKSHEET.md`、`LIFECYCLE_RECORD.md`

### 合併與刪除映射

此文件僅用於保留已核准過的參考標準，不涉及刪除或覆蓋其他文件。

### BUILD

- Output：保留一份參考標準 Markdown（本文件）。
- Gate：未修改 runtime邏輯、資料 schema、法律題庫內容、資料庫或部署設定。

### TEST

- `MARKDOWN_LINKS_OK`：PASS。
- `NO_STALE_REFERENCES`：PASS；本文件除外。
- 目標測試首次結果：40 passed、1 failed；唯一失敗為文件下載等待逾時。
- 同一 E2E 案例重跑：1 passed。
- 完整 `pytest`：153 passed。
- Node 前端行為測試：15 passed。
- `node --check app/static/app.js`：PASS。
- `pyflakes app tests`：PASS。
- `data/*.json`解析：5 files PASS。

### Sol Review Decision

- execution_mode：`REVIEWED_PIPELINE`
- routing_triggers：`H2`、`S3`
- runtime_reported_model：`UNVERIFIED`
- R1：`ACCEPT`；保留五份單一責任 canonical 文件。
- R2：`ACCEPT`；保留兩份 RCQ 固定路徑及生命週期紀錄。
- R3：`ACCEPT_WITH_MODIFICATIONS`；保留語意測試人工工作表，其餘逐檔整併後刪除。
- R4：`ACCEPT`；以 runtime code／tests 說明目前行為，法律完整性維持未宣稱。
- R5：`ACCEPT`；以完整檔名、bytes 及 SHA-256留存刪除證據。
- final_status：`COMPLETE / REVIEWED_PIPELINE_UNVERIFIED`

---

## 2026-10-27：`embezzlement_335_general` 問句設計參考標準

- 標準：8個 concepts；一般侵占與竊盜、公務公益侵占、業務侵占、侵占遺失物分開比較。
- 去重：既有 `prior_lawful_custody`、`authorization_scope`、`post_acquisition_conduct` 只引用並於缺漏時追問。
- 效果：單題不產生 `ACTIVE`；`UNKNOWN`、`CONFLICT` 與民事替代方向均為 `NEED_REVIEW`。
- Scope expansion：交付前不實說明只標記 `ROUTE_SCOPE_EXPANSION_REQUIRED`，不在本 route 建立詐欺候選。
- 歸檔：`docs/evidence/question_route_archives/embezzlement_335_general-iteration-0-20261027.txt`，SHA-256 `6EE5032F154C6C0B0FD980987961BADE0A874DBED2F4E64CFEBF16C77E2AB7A4`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---
## 2026-10-27：`obstruction_138_official_property` 問句設計參考標準

- C02確認公務員職務上掌管或委託第三人掌管關係；C03確認文書、圖畫或物品標的；C04確認毀棄、損壞、隱匿或致令不堪用行為；C05區分實行、指示、協助或其他角色；C06至C08補證據來源。
- 第135至137及第139至141條其他妨害公務路線分開；第140條部分與第141條之1維持失效／排除邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/obstruction_138_official_property-iteration-0-20261027.txt`，SHA-256 `4D7E80B97C478878A9277F535277A140F064B3439C0E2AB61A1E2317108E1DF5`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---
## 2026-10-27：`obstruction_137_exam_fraud` 問句設計參考標準

- C02確認考試法規範之考試與相關身分；C03確認詐術或其他非法方法；C04確認使考試發生不正確結果；C05區分實行、教唆、協助或其他角色；C06確認未遂／既遂進度；C07至C08補證據來源。
- 第135、136及第138至141條其他妨害公務路線分開；第140條部分與第141條之1維持失效／排除邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/obstruction_137_exam_fraud-iteration-0-20261027.txt`，SHA-256 `E8FB248232062F36F6C61305997335D3320E5AB5FF8C3263DB2A009C78E880CB`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---
## 2026-10-27：`obstruction_136_group` 問句設計參考標準

- C02確認公共場所或公眾得出入場所與依法執行職務公務員；C03確認三人以上聚集及第135條行為；C04確認死亡或重傷結果與因果關係；C05確認在場助勢、首謀、下手實施、指示或協助角色；C06至C08補證據來源。
- 第135條及第137至141條其他妨害公務路線分開；第140條部分與第141條之1維持失效／排除邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/obstruction_136_group-iteration-0-20261027.txt`，SHA-256 `46195C5E7B271AC581E8FE02E845C861B5795F184BD4556F9F3DC02F3CC54C31`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---
## 2026-10-27：`obstruction_135_violence_threat` 問句設計參考標準

- C02確認公務員是否依法執行職務；C03確認強暴或脅迫行為；C04確認死亡或重傷結果與因果關係；C05確認個別實行、指示、協助或在場角色；C06確認動力交通工具、兇器或危險物品等加重態樣；C07至C08補證據來源。
- 第136至141條其他妨害公務路線分開；第140條部分與第141條之1維持失效／排除邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/obstruction_135_violence_threat-iteration-0-20261027.txt`，SHA-256 `7FF997A6783ACCE1461B4E167D50615CB4B000C6B3083D7A604B308333DA961C`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---
## 2026-10-27：`duty_134_official_aggravation` 問句設計參考標準

- C02確認公務員身分與行為時職務；C03確認假借職務權力、機會或方法；C04確認章外故意犯罪與既有特別刑度；C05逐人確認實行、指示、協助或僅在場角色；C06至C08補證據來源。
- 第129至133條其他瀆職與第134條加重規定維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`，不以加重規定取代章外基本罪確認。
- 歸檔：`docs/evidence/question_route_archives/duty_134_official_aggravation-iteration-0-20261027.txt`，SHA-256 `86AB414536D4E54E1871077F12BE03D81BE779FC8D6DEC0373B7BCEEB3A2C8F7`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---
## 2026-10-27：`duty_133_mail` 問句設計參考標準

- C02確認郵務／電報機關執行職務身分與郵件電報來源；C03確認郵件或電報種類及開拆／隱匿行為；C04確認交付對象與流向；C05逐人確認開拆、隱匿、交付、指示或協助角色；C06至C08補證據來源。
- 第129至132條及第134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_133_mail-iteration-0-20261027.txt`，SHA-256 `3FB38B31C8A5BCDE8530A9A6180AD04CABB1D0F2588FECB3A0A5EB404E685898`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---
## 2026-10-27：`duty_132_nondefense_secret` 問句設計參考標準

- C02確認依法應秘密的資料與身分／職務來源；C03確認取得、持有或洩漏行為；C04確認洩漏對象與資料流向；C05逐人確認取得、持有、洩漏、指示或協助角色；C06確認故意／過失與知悉來源；C07至C08補證據來源。
- 第129至131條及第133至134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_132_nondefense_secret-iteration-0-20261027.txt`，SHA-256 `12569968DD52E2CEF53D8D90E5D8E256E95983D4E001E705EA0E82132A78938B`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---
## 2026-10-27：`duty_131_unlawful_benefit` 問句設計參考標準

- C02確認公務員主管／監督事務與職權範圍；C03確認具體違背法令與行為時間；C04確認直接或間接私人不法利益；C05逐人確認主管、執行、指示或協助角色；C06確認利益結果與因果關係；C07至C08補證據來源。
- 第129、130條及第132至134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_131_unlawful_benefit-iteration-0-20261027.txt`，SHA-256 `FBB35E991F46E959DE490B5D1401481572EDEA81103AA9B140C5CEF7A5AF0A10`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---
## 2026-10-27：`duty_130_disaster` 問句設計參考標準

- C02確認公務員身分與法定職務；C03確認具體廢弛職務行為與時間；C04確認災害結果；C05逐人確認廢弛職務、怠於執行、指示或協助；C06確認因果關係與可預見性；C07至C08補證據來源。
- 第129條及第131至134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_130_disaster-iteration-0-20261027.txt`，SHA-256 `1A81EC8EE3B956A18DD8E2F3BEB2BC3E298EA6A17D6D65BAFE1C4F20B34000E4`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---
## 2026-10-27：`duty_129_illegal_collection` 問句設計參考標準

- C02確認公務員身分與職務上款項物品；C03確認明知不應徵收或應發給而抑留剋扣；C04確認款項物品來源、法定義務、明知及未遂／既遂；C05逐人確認徵收、抑留、剋扣、指示或協助；C06至C08補證據來源。
- 第120至128條及第130至134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_129_illegal_collection-iteration-0-20261027.txt`，SHA-256 `E0A5167DB01796D509493FCE0ED3F17668DC3BEFBCF6CFB2FEC19D8423BA29E0`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`duty_128_unlawful_acceptance` 問句設計參考標準

- C02確認公務員身分與具體訴訟職務；C03確認訴訟事件與實際受理行為；C04確認法定受理要件與明知不應受理；C05逐人確認承辦、受理、指示或協助角色；C06至C08補證據來源。
- 第120至127條及第129至134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_128_unlawful_acceptance-iteration-0-20261027.txt`，SHA-256 `7C7C11CBF7F852F0F6C073297B0D66970B6B76A4A0294AA0BB912467D262A4EC`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`duty_127_execution` 問句設計參考標準

- C02確認執行刑罰職務之公務員身分與法定權限；C03確認違法執行、不執行或過失執行；C04確認刑罰內容、執行依據與執行狀態；C05逐人確認執行、停止、錯誤執行、指示或協助角色；C06至C08補證據來源。
- 第120至126條及第128至134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_127_execution-iteration-0-20261027.txt`，SHA-256 `5A827094ECC8FB2A478CCD86DBBF44BE7D0B4933E3C753A980C93FFD88AAA2F5`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`duty_126_abuse_detainee` 問句設計參考標準

- C02確認管收、解送或拘禁人犯職務之公務員身分與權限；C03確認對人犯施以凌虐的方式、時間與場所；C04確認死亡／重傷結果、因果關係與可預見性；C05逐人確認角色；C06至C08補證據來源。
- 第120至125條及第127至134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_126_abuse_detainee-iteration-0-20261027.txt`，SHA-256 `3B0B8287BB70CEB59837302CDBB5EF3EBB5C940771788ABB53BDB45C6A4064FE`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`duty_125_abuse_prosecution` 問句設計參考標準

- C02確認追訴或處罰犯罪職務之公務員身分與法定權限；C03確認濫權逮捕羈押、取供強暴脅迫、故意錯誤追訴等行為；C04確認死亡／重傷結果、因果關係與可預見性；C05逐人確認角色；C06至C08補證據來源。
- 第120至124條及第126至134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_125_abuse_prosecution-iteration-0-20261027.txt`，SHA-256 `4D88451630DD597AFB5039B17A714A9DD87CEDD4398DCA189BC862690FB1979B`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`duty_124_unlawful_judgment` 問句設計參考標準

- C02確認審判職務公務員或仲裁人身分與權限；C03確認裁判／仲裁行為與法令依據；C04確認明知違法；C05逐人確認承辦、合議、仲裁、指示或協助角色；C06至C08補結果因果與證據來源。
- 第120至123條及第125至134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_124_unlawful_judgment-iteration-0-20261027.txt`，SHA-256 `E30FE8942F6AB22FAB60C15672D92420ED5BCC6E04BEE13ABD2AB58F0419AB67`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`duty_123_advance_bribery` 問句設計參考標準

- C02確認預先要求或收受利益時尚未具公務員／仲裁人身分，以及後來取得身分；C03確認預先利益行為；C04確認後續履行；C05逐人確認角色；C06至C08補利益流向與證據來源。
- 第120至122條及第124至134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_123_advance_bribery-iteration-0-20261027.txt`，SHA-256 `4ACFE021D801912421929DF9A8B6A7E2D773175B9AA6EE52172361849277942B`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`duty_122_bribery_breach` 問句設計參考標準

- C02確認公務員或仲裁人身分與職務關聯；C03確認要求、期約、收受、行求或交付不正利益；C04確認是否實際違背職務；C05逐人確認角色；C06至C08補利益流向與證據來源。
- 第120、121、123至134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_122_bribery_breach-iteration-0-20261027.txt`，SHA-256 `0C7DF03D4A9DF1DE3B79439890FE101FA669DDDFCDEB73D800EA3CF44C33A26F`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`duty_121_bribery_duty` 問句設計參考標準

- C02確認公務員或仲裁人身分與職務關聯；C03確認要求、期約、收受或交付賄賂；C04確認對應職務上行為；C05逐人確認要求、期約、收受、交付、介紹或僅在場；C06至C08補利益流向與證據來源。
- 第120條、第122至134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_121_bribery_duty-iteration-0-20261027.txt`，SHA-256 `4781176611954206ED68B06B78441E4AC75D8FC4395AF0F7A454AE676B3793C7`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`duty_120_abandon_post` 問句設計參考標準

- C02確認公務員身分、受任職責與守地任務；C03確認離開、放棄或不履行守地職責；C04確認守地及職務範圍；C05逐人確認值勤、離開、指示、協助或僅在場；C06至C08補結果、因果與證據來源。
- 第121至134條其他瀆職、加重、定義及程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/duty_120_abandon_post-iteration-0-20261027.txt`，SHA-256 `1A53063DEB0E51BDC407E6BD26F2A81AC8E5C7FED396A81C6CE13961042FF9FB`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_118_foreign_symbol` 問句設計參考標準

- C02確認侮辱外國國旗／國章意圖；C03確認公然損壞、除去或污辱等行為；C04確認不特定或多數人得共見共聞的情境；C05逐人確認實際角色；C06確認外國旗章客體；C07至C08補證據來源。
- 第100至117、115之1、116、119條及減免／加重／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_118_foreign_symbol-iteration-0-20261027.txt`，SHA-256 `4CEF3A07A8AADA51215396D7A42A77C527D23EB99C09270541B8C99C7D07A509`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`drugs_11_possession` 敏感案件問句設計參考標準

- C02分開確認實際持有／管領與來源脈絡；C03確認毒品類別；C04確認純質淨重、法定門檻及量測依據；C05確認器具用途、持有期間與證據來源，不以單一持有陳述推定全部構成要件。
- 第4至8條、第10條與第9條加重路線維持獨立；單題、重量、器具、來源或單一說法不得單獨升為 `ACTIVE`。
- `UNKNOWN`、`CONFLICT`、既遂／未遂法律分類及未列入 scope 的相鄰路線均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/drugs_11_possession-iteration-0-20261027.txt`，SHA-256 `42307E94EC95B3E396E15813BF34882A6039B916B8CE8BC050A7457B176B800C`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`state_security_117_neutrality` 問句設計參考標準

- C02確認外國交戰期間；C03確認政府局外中立命令；C04確認違背命令的具體行為、時間與對象；C05逐人確認角色；C06至C08補證據來源。
- 第100至116、118條及減免／加重／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_117_neutrality-iteration-0-20261027.txt`，SHA-256 `0735EFBA2B1F63F2BCCFAFB76A93B520DE13E753E61AF1D5D486C3F751DFB316`；runtime未改、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_115_foreign_right_evidence` 問句設計參考標準

- C02確認我國對外權利之文書、圖畫或證據客體；C03確認偽造、變造、毀棄或隱匿行為；C04至C05分開確認角色與結果；C06至C08補證據來源。
- 第100至114、115之1、116、119條及減免／加重／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_115_foreign_right_evidence-iteration-0-20261027.txt`，SHA-256 `1B616647C2A29C6A232220B8D1E5A33BEFD7ADA5C911515D2B628D654666E9B3`；runtime未改、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_114_breach_mandate` 問句設計參考標準

- C02確認政府委任及外交事務範圍；C03確認委任內容；C04確認違背行為、損害結果與因果；C05逐人確認角色；C06至C08補證據來源。
- 第100至113、115條及減免／加重／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_114_breach_mandate-iteration-0-20261027.txt`，SHA-256 `1B102CDC3082E1BAEE31D669613B4B918246FDCBE2BA1DD730FEB5C94BA8FE97`；runtime未改、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_113_foreign_agreement` 問句設計參考標準

- C02確認依法應授權事項；C03確認未獲授權與約定對象；C04確認約定內容、時間與損害風險；C05逐人確認角色；C06至C08補結果與證據來源。
- 第100至112、114、115條及減免／加重／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_113_foreign_agreement-iteration-0-20261027.txt`，SHA-256 `442A576BD7B5B9FEEDB616EC2DAB74B858CBA06E271F36D59E3B955627B9DDD6`；runtime未改、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_112_military_site` 問句設計參考標準

- C02確認刺探／收集國防秘密目的；C03確認未受允准；C04確認要塞、軍港、軍艦等軍事處所之進入／留滯；C05逐人確認角色；C06至C08補結果與證據來源。
- 第100至111條及減免／加重／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_112_military_site-iteration-0-20261027.txt`，SHA-256 `1D5FE42701C9D31FEFE044F30DB8AA6B5B419D9BA55A6313F08B41D41F4EB298`；runtime未改、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_111_collect_secret` 問句設計參考標準

- C02確認刺探／收集行為及對象；C03確認國防秘密客體；C04區分著手、預備、陰謀／聯絡；C05逐人確認角色；C06至C08補結果、聯絡與證據來源。
- 第100至110、112條及減免／加重／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_111_collect_secret-iteration-0-20261027.txt`，SHA-256 `0A399937B7108F706BC1EF9FAE924E9A9B3CF5B75098287896B4A34F2A96794D`；runtime未改、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_110_negligent_secret` 問句設計參考標準

- C02確認公務員身分及職務上知悉／持有；C03確認國防秘密客體；C04確認過失洩漏／交付與對象；C05逐人確認角色；C06至C08補結果、聯絡與證據來源。
- 第100至109、111、112條及減免／加重／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_110_negligent_secret-iteration-0-20261027.txt`，SHA-256 `7D8247E37319CDE70754C6F13F38E06FFD42262B30AA22827DA26B262E9CC3DB`；runtime未改、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_109_defense_secret` 問句設計參考標準

- C02確認國防應秘密之文書、圖畫、消息或物品；C03確認洩漏／交付行為及對象；C04區分著手、預備、陰謀／聯絡；C05逐人確認角色；C06至C08補結果、聯絡與證據來源。
- 第100至108、110至112條及減免／加重／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_109_defense_secret-iteration-0-20261027.txt`，SHA-256 `F295907C473225B2C2A4FE87D12CCEA21C1E10FD380B1510F6430D87F10DF469`；runtime未改、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_108_military_supply` 問句設計參考標準

- C02確認開戰／將開戰期間；C03確認軍需供給契約；C04區分故意、過失、不履行與不完全履行；C05逐人確認角色；C06至C08補結果、聯絡與證據來源。
- 第100至107、109條及減免／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_108_military_supply-iteration-0-20261027.txt`，SHA-256 `DF8E450E90C427CD559F0AA02AB6AF18CDCAC7A33C94F66A19CA07007A5ADD1E`；runtime未改、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_106_military_advantage` 問句設計參考標準

- C02確認戰時／將戰期間與敵軍事利益或我國軍事不利益；C03確認具體行為；C04區分著手、預備、陰謀／聯絡；C05逐人確認角色；C06至C08補結果、聯絡與證據來源。
- 第100至105條及減免／加重／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_106_military_advantage-iteration-0-20261027.txt`，SHA-256 `42CBCB93D66BEC5340135C826F42ECD63AF396BB7F939E8E9BA982D823EA546C`；runtime未改、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_105_enemy_service` 問句設計參考標準

- C02確認國民身分與敵軍／敵國對象；C03確認服役或械抗行為；C04區分著手、預備、陰謀／聯絡；C05逐人確認角色；C06至C08補對象／結果、聯絡與證據來源。
- 第100、101、103、104、106條及減免／加重／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_105_enemy_service-iteration-0-20261027.txt`，SHA-256 `8FB7467E7B1EF9842E92472D690F3C321428DB187D562D3CE74AE26371DA0FF0`；runtime未改、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_104_territory` 問句設計參考標準

- C02確認通謀外國及使我國領域屬於他國之目的；C03確認具體行為與對象；C04區分著手、預備、陰謀／聯絡；C05逐人確認角色；C06至C08補目標／結果、聯絡與證據來源。
- 第100、101、103、105條及減免／加重／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_104_territory-iteration-0-20261027.txt`，SHA-256 `84836285280D49D59485DCF341E56F01910F60BEED826C23928C2DD0E5B2AB8B`；runtime未改、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_103_start_war` 問句設計參考標準

- C02確認通謀外國及使開戰目的；C03確認具體行為與對象；C04區分著手、預備、陰謀／聯絡；C05逐人確認角色；C06至C08補目標／結果、聯絡與證據來源。
- 第100、101、104、105條及減免／加重／定義／程序路線維持邊界；`UNKNOWN`、`CONFLICT` 與相鄰路線維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/state_security_103_start_war-iteration-0-20261027.txt`，SHA-256 `C299EA6824879003F3FF1343739396BE5C33426D3568602E30D1F2E33FF0DE0A`；runtime未改、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`state_security_101_riot` 問句設計參考標準

- C02確認第101條暴動內亂目的；C03確認強暴或脅迫；C04區分著手、預備、陰謀／聯絡；C05逐人確認首謀、指揮、實行與協助角色；C06至C08補目標／結果、聯絡資料與證據來源。
- 第100條、第103至105條及第102、107、115之1、119條維持相鄰或邊界路線；政治表意、集會、通聯、人數或結果不得單獨升為 `ACTIVE`。
- `UNKNOWN`、`CONFLICT`、未列入 scope 的相鄰路線及行為時法均維持 `NEED_REVIEW` 或 `UNKNOWN`。
- 歸檔：`docs/evidence/question_route_archives/state_security_101_riot-iteration-0-20261027.txt`，SHA-256 `B499EA1D9AE4A9174B6137421F7FB0857BB1B046155A9BBDE548FE5A943761BA`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`state_security_100_insurrection` 問句設計參考標準

- C02確認第100條法定目的；C03確認強暴或脅迫；C04區分著手、預備、陰謀／聯絡；C05逐人確認首謀、指揮、實行與協助角色；C06至C08補目標／結果、聯絡資料與證據來源。
- 第101條、第103至105條及第102、107、115之1、119條維持相鄰或邊界路線；政治表意、集會、通聯、人數或結果不得單獨升為 `ACTIVE`。
- `UNKNOWN`、`CONFLICT`、未列入 scope 的相鄰路線及行為時法均維持 `NEED_REVIEW` 或 `UNKNOWN`。
- 歸檔：`docs/evidence/question_route_archives/state_security_100_insurrection-iteration-0-20261027.txt`，SHA-256 `3DC8F6BD6D8F309FAE4C518777EA266DBE010CC06601D3F932323710D91697E8`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`drugs_11_possession` 敏感案件問句設計參考標準

- C02只確認持有／實力支配、來源與毒品品項；查扣或接觸不單獨等同持有成立。
- C03、C04分開確認級別、純質淨重／數量門檻、專供製造施用器具用途與持有期間；不得以器具存在或數量單獨補推法定要件。
- C05確認持有支配、品項／數量與器具用途證據的關聯；單一查扣、供述或鑑驗均不得單獨升為 `ACTIVE`。
- 第4至10條及第9條加重另建 route；`UNKNOWN`／`CONFLICT` 均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/drugs_11_possession-iteration-0-20261027.txt`，SHA-256 `42307E94EC95B3E396E15813BF34882A6039B916B8CE8BC050A7457B176B800C`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`drugs_10_use` 敏感案件問句設計參考標準

- C02只確認施用行為、時間、地點與方法；持有、接觸或檢測陽性不單獨等同施用。
- C03、C04分開確認毒品品項／級別與採尿／鑑驗、就醫或其他可回查資料；不得以單一檢測替代行為時間線。
- C05確認施用行為、品項與鑑驗證據的關聯；單一檢驗、供述或現場紀錄均不得單獨升為 `ACTIVE`。
- 歸檔：`docs/evidence/question_route_archives/drugs_10_use-iteration-0-20261027.txt`，SHA-256 `AB76DF8B9696BC5018BAD78FF16441C23AC4C14B6378CCB4AF7E4466C6F2FD44`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`drugs_9_aggravation` 加重邊界

- `route_kind=aggravation`，只確認第6至8條基礎行為、未成年人／孕婦／混合毒品等加重事實及認識，不單獨產生犯罪候選。
- 加重事由與基礎行為分開核對；`UNKNOWN`／`CONFLICT` 維持 `NEED_REVIEW`，需經 `CASE_HUMAN_GATE`。

---

## 2026-10-27：`drugs_8_transfer` 敏感案件問句設計參考標準

- C02只確認轉讓／交付行為與受讓人；接觸、持有或共同使用不單獨等同轉讓。
- C03、C04分開確認毒品品項／級別、交付經過與未遂既遂；不得以受讓人說法或物品存在單獨推定交付。
- C05確認轉讓行為、受讓人與毒品品項證據的關聯；單一交付、供述或檢驗均不得單獨升為 `ACTIVE`。
- 第4至7、10至11條及第9條加重另建 route；`UNKNOWN`／`CONFLICT` 均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/drugs_8_transfer-iteration-0-20261027.txt`，SHA-256 `939AA1548A2070E3BF16796E8979D172523A61E3A182DDB269DD8FE26803484A`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`drugs_4_manufacture_transport_sale` 敏感案件問句設計參考標準

- C02只確認毒品品項／級別與來源資料；物品外觀、稱呼或單一鑑驗結果不單獨等同法定分類。
- C03、C04分開確認製造、運輸、販賣、交易角色與流程；不得由持有、包裝、通聯或金流單獨推定販賣或製造。
- C05確認行為、品項、流程與未遂／既遂資料的關聯；單一查扣、訊息或供述均不得單獨升為 `ACTIVE`。
- 第5至11條及第9條加重另建 route；`UNKNOWN`／`CONFLICT` 均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/drugs_4_manufacture_transport_sale-iteration-0-20261027.txt`，SHA-256 `35BDC8D6038E49EA297524BE508104E6C9D3595BD8A54ACB8D82FF8BA5CE87F5`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；敏感案件不得由AI取代人工安全與法律審核。

---

## 2026-10-27：`drugs_7_induce_use` 敏感案件問句設計參考標準

- C02只確認引誘行為與內容；訊息、利益或交付存在不單獨等同引誘。
- C03、C04分開確認他人施用、毒品品項／級別與未遂既遂；不得以他人施用結果回推引誘內容或主觀意圖。
- C05確認引誘內容、他人施用與毒品品項證據的關聯；單一訊息、供述或檢驗均不得單獨升為 `ACTIVE`。
- 第4至6、8至11條及第9條加重另建 route；`UNKNOWN`／`CONFLICT` 均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/drugs_7_induce_use-iteration-0-20261027.txt`，SHA-256 `4B51E6015CF9C4A5E25A2B2744779E73228270D0582BB4F6D5CD2EA7697ECC48`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`drugs_6_force_use` 敏感案件問句設計參考標準

- C02只確認強暴、脅迫、欺瞞或其他非法方法；被害人施用或毒品存在不單獨等同方法成立。
- C03、C04分開確認他人施用、毒品品項／級別、死亡／重傷結果與因果；不得以結果補推方法或主觀故意。
- C05確認非法方法、施用與結果／因果的關聯；單一供述、檢驗或就醫紀錄均不得單獨升為 `ACTIVE`。
- 歸檔：`docs/evidence/question_route_archives/drugs_6_force_use-iteration-0-20261027.txt`，SHA-256 `B21875721A5791C5710F6DED6774FBC17F300C25DFF913E1A1BE6A259225CC93`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`drugs_5_possession_intent_sale` 敏感案件問句設計參考標準

- C02只確認毒品品項／級別、來源與持有／實力支配；查扣或單一持有狀態不單獨等同販賣意圖。
- C03、C04分開確認數量／純質淨重、分裝、聯絡、金流、交易準備及其他客觀指標；不得以包裝、通聯或金流單獨推定意圖。
- C05確認持有支配、品項與販賣意圖客觀指標的關聯；單一查扣、供述或交易傳聞均不得單獨升為 `ACTIVE`。
- 第4、6至11條及第9條加重另建 route；`UNKNOWN`／`CONFLICT` 均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/drugs_5_possession_intent_sale-iteration-0-20261027.txt`，SHA-256 `490D888676ED9EDCA5399B4D7F273DCCAF0953F9F92AA694FD55AA94B7D2B04B`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；敏感案件不得由AI取代人工安全與法律審核。

---

## 2026-10-27：`public_danger_185_4_hit_and_run` 問句設計參考標準

- C02只確認交通事故、駕駛動力交通工具與死傷結果；事故存在不等同知悉或逃逸。
- C03、C04分開確認知悉事故／死傷、停留／救護與離開現場方式，並另核對駕駛人對事故有無過失的減免脈絡。
- C05確認事故、死傷、知悉與離開現場的關聯；單一監視器片段、離開行為或結果均不得單獨升為 `ACTIVE`。
- 第185條之3酒毒駕另建 route；`UNKNOWN`／`CONFLICT` 均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/public_danger_185_4_hit_and_run-iteration-0-20261027.txt`，SHA-256 `EC5279C9B56FD84994038BE5C8F4BF2184E4480ACD49CF612C79249FA522CA98`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`forgery_215_business_false_entry` 問句設計參考標準

- C02只確認行為人是否具有業務身分及該業務與文書製作的關聯；職稱或單一說法不足以直接成立。
- C03、C04分開確認業務上文書範圍與不實登載內容；不得以文書存在或後續使用替代登載事實。
- C05確認不實登載與具體損害風險的關聯；損害結果、動機或證據存在均不得單獨升為 `ACTIVE`。
- `UNKNOWN`、`CONFLICT`、未列入 scope 的相鄰路線均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/forgery_215_business_false_entry-iteration-0-20261027.txt`，SHA-256 `D02E23C01F63F273A531EB2A18DE3AF42D23D65D9FC55D79EA2A6F731A402FF8`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`sexual_harassment_25_unwanted_touch` 敏感案件問句設計參考標準

- C02只確認具體互動與意圖脈絡；不以身體接觸、衣著、關係或事後反應單獨推定性騷擾意圖。
- C03、C04分開確認被害人當時不及抗拒情境、具體親吻／擁抱／觸摸方式及權勢關係；避免重複或誘導詢問。
- C05確認行為、被害人反應與可核對證據的關聯；單一說法、情緒反應或紀錄存在均不得單獨升為 `ACTIVE`。
- 第2條分類與第7至17條保護／申訴程序不混入本 offense route；`UNKNOWN`／`CONFLICT` 均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/sexual_harassment_25_unwanted_touch-iteration-0-20261027.txt`，SHA-256 `283A0BDB9EB75011434EFCB2404C4B80EB1498D113FF49DBFC82A07289645871`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；敏感案件不得由AI取代人工安全與法律審核。

---

## 2026-10-27：`public_danger_185_3_impaired_driving` 問句設計參考標準

- C02只確認駕駛動力交通工具與酒精／毒品影響資料；飲酒、用藥或檢測數值不單獨等同不能安全駕駛。
- C03、C04分開確認不能安全駕駛、死亡／重傷結果、因果與可預見性；不得以事故結果補推駕駛狀態或因果。
- C05確認十年內再犯與前案確定狀態；前科傳聞、單一紀錄或動機均不得單獨升為 `ACTIVE`。
- 第185條之4事故逃逸另建 route；`UNKNOWN`／`CONFLICT` 均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/public_danger_185_3_impaired_driving-iteration-0-20261027.txt`，SHA-256 `E61764202758A508A30709003A4342B7174C066DAC98ED23DC4A756BD2E5DC1F`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：跟蹤騷擾章非 offense 路線邊界

- 第3條是 `classification`，第4至17條及第20至21條是 `procedure`。
- 這些路線不單獨產生犯罪候選；定義、保護令、審理與羈押程序和第18、19條犯罪路線分開，均需 `CASE_HUMAN_GATE`。

---

## 2026-10-27：`stalking_19_protection_order` 敏感案件問句設計參考標準

- C02只確認有效保護令的核發、內容與效力；存在聲請、告誡或傳聞不等同有效命令。
- C03、C04分開確認送達／知悉、禁止接近／查閱／治療處遇命令範圍及具體違反行為；不得以被害人主張替代命令文件或知悉證據。
- C05確認保護令內容、知悉與具體行為的關聯；單一聯絡、接近或程序紀錄均不得單獨升為 `ACTIVE`。
- 第3條定義、第4至17條保護令及第20至21條程序不混入本 route；`UNKNOWN`／`CONFLICT` 均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/stalking_19_protection_order-iteration-0-20261027.txt`，SHA-256 `EA4DACA1E68DF240C73654DB06EED58020983A7FB720117DC1766D2B317F1EB3`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；敏感案件不得由AI取代人工安全與法律審核。

---

## 2026-10-27：`stalking_18_offense` 敏感案件問句設計參考標準

- C02只確認法定跟蹤騷擾行為態樣與事件時間線；聯絡頻率、關係或主觀恐懼不得單獨推定法定構成。
- C03、C04分開確認反覆／持續、違反意願、畏怖及日常生活影響，並另核對危險物品與告訴程序脈絡。
- C05確認行為、被害人影響與可核對證據的關聯；單一訊息、接近或情緒反應均不得單獨升為 `ACTIVE`。
- 第3條定義、第4至17條保護令及第19至21條程序／犯罪路線不混入本 route；`UNKNOWN`／`CONFLICT` 均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/stalking_18_offense-iteration-0-20261027.txt`，SHA-256 `E05BF9DB5F7A84FDC0F6BC98B0BE83091E3B1BF5F9CBEAAED93DD195A97D047C`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；敏感案件不得由AI取代人工安全與法律審核。

---

## 2026-10-27：性騷擾章非 offense 路線邊界

- 第2條是 `classification`，第7至13條及第14至17條是 `procedure`，第26至30條是 `administrative`。
- 這些路線不單獨產生犯罪候選；保護、申訴、調查、行政責任與第25條犯罪路線分開，均需 `CASE_HUMAN_GATE`。

---

## 2026-10-27：`computer_363_complaint` 程序邊界

- `route_kind=procedure`，只保留告訴權人、告訴意思、提出時間與程序效果，不單獨產生犯罪候選。
- 程序問句另建流程工作流；`UNKNOWN`／`CONFLICT` 維持 `NEED_REVIEW`，不反推第358至360條構成要件。

---

## 2026-10-27：`computer_362_malware` 問句設計參考標準

- C02只確認程式內容、來源與製作行為；程式存在、下載或具破壞性外觀不等同供犯罪使用。
- C03、C04分開確認製作人、製作／取得／交付方式與供自己或他人犯罪使用意圖；不得由程式用途推定主觀意圖。
- C05確認程式製作與具體損害風險的關聯；損害主張、程式功能或動機均不得單獨升為 `ACTIVE`。
- `UNKNOWN`、`CONFLICT`、未列入 scope 的相鄰路線均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/computer_362_malware-iteration-0-20261027.txt`，SHA-256 `EC94C54070F4AFA0388DDD1A0FDA002155BF6EA2C3DD5CA3341CF0D10263D4E6`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`computer_361_public_agency` 加重邊界

- `route_kind=aggravation`，只確認基礎第358至360條行為與公務機關標的，不單獨產生犯罪候選。
- 加重事由與基礎行為分開核對；`UNKNOWN`／`CONFLICT` 維持 `NEED_REVIEW`，需經 `CASE_HUMAN_GATE`。

---

## 2026-10-27：`computer_360_interference` 問句設計參考標準

- C02只確認電腦程式或其他電磁方式與設備對象；程式存在、流量異常或設備故障不等同干擾行為。
- C03、C04分開確認實際干擾方法與授權範圍；不得以設備受影響或事後推測補推無故狀態。
- C05確認干擾行為與具體損害風險的關聯；故障紀錄、損害主張或動機均不得單獨升為 `ACTIVE`。
- `UNKNOWN`、`CONFLICT`、未列入 scope 的相鄰路線均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/computer_360_interference-iteration-0-20261027.txt`，SHA-256 `2516B15DE69FAA250697791466BDCFA92B261397B4824464A321752B112E75CB`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`computer_359_data_change` 問句設計參考標準

- C02只確認被涉及的電磁紀錄與設備對象；存在帳號或設備不等同取得、刪除或變更行為。
- C03、C04分開確認實際操作方式、紀錄狀態變化與權限範圍；不得由登入、權限或結果單獨補推無故行為。
- C05確認操作與具體損害風險的關聯；紀錄差異、損害主張或動機均不得單獨升為 `ACTIVE`。
- `UNKNOWN`、`CONFLICT`、未列入 scope 的相鄰路線均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/computer_359_data_change-iteration-0-20261027.txt`，SHA-256 `F1B0D6CF40DB8AB00965303A486E952333A53790170872CCF44FC4F9FBCC3200`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`computer_358_intrusion` 問句設計參考標準

- C02只確認電腦／相關設備對象與帳號、密碼、保護措施或漏洞脈絡；設備名稱或登入結果不等同無故入侵。
- C03、C04分開確認實際入侵方法與授權範圍；不得以無法登入、持有帳號或事後推測補推無故狀態。
- C05確認入侵行為與具體損害風險的關聯；紀錄存在、損害主張或動機均不得單獨升為 `ACTIVE`。
- `UNKNOWN`、`CONFLICT`、未列入 scope 的相鄰路線均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/computer_358_intrusion-iteration-0-20261027.txt`，SHA-256 `9C8279D26F5369009B1FB08280C161961AEFC3DE7BB070EE0F8592B78A5D55AA`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：偽造文書章 collateral／definition 邊界

- `forgery_219_confiscation` 是 `collateral`，只保留偽造物與本章行為之關聯，不能單獨產生犯罪候選。
- `forgery_220_document_definition` 是 `definition`，只保留文書及電磁紀錄準文書的載體、意思表示及法律用途範圍，不能單獨產生犯罪候選。
- 兩者不進 offense-core 題組；個案引用仍須經 `CASE_HUMAN_GATE`，`UNKNOWN`／`CONFLICT` 維持 `NEED_REVIEW`。

---

## 2026-10-27：`forgery_218_official_seal` 問句設計參考標準

- C02只確認公印或公印文、公署／機關及來源；公務機關名稱或外觀相似不足以單獨確認法定公印性質。
- C03、C04分開確認形成／使用方式與公署／機關關聯；不得由單一印記或持有狀態補推偽造、盜用或權限。
- C05確認行為與具體損害風險的關聯；損害主張、動機或證據存在均不得單獨升為 `ACTIVE`。
- `UNKNOWN`、`CONFLICT`、未列入 scope 的相鄰路線均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/forgery_218_official_seal-iteration-0-20261027.txt`，SHA-256 `2764AD022E10EF9810A7FFB885477E54244A2BA21AB0233217060993B47E105B`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`forgery_217_seal_signature` 問句設計參考標準

- C02只確認印章、印文或署押的種類、權利人與來源；物件存在不等同偽造或盜用。
- C03、C04分開確認授權範圍、形成／使用方式及具體行為；不得以單一簽名、印記或使用結果補推來源。
- C05確認行為與具體損害風險的關聯；損害主張、動機或證據存在均不得單獨升為 `ACTIVE`。
- `UNKNOWN`、`CONFLICT`、未列入 scope 的相鄰路線均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/forgery_217_seal_signature-iteration-0-20261027.txt`，SHA-256 `117982BA471DBBF4E9C0705219AE380AE84ADBD70CB2D85368562961CEC98439`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`damage_354_property` 問句設計參考標準

- C02只確認他人之物、所有／持有狀態與可核對資料；C03只確認毀棄、損壞或致令不堪用的具體行為，不以物品名稱或外觀直接代替要件。
- C04、C05分開確認損害結果、損害程度、行為與損害的關聯及證據來源；不得由單一損壞描述補推因果或法律成立。
- 單題、物品權利狀態、毀損外觀、損害估價及後續修復均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/damage_354_property-iteration-0-20261027.txt`，SHA-256 `0E7512D003676C2506E25E6DA2702ECC8A5AFAE68D010FBBA98104F481868FB0`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-28：`forgery_216_use_document` 問句設計參考標準

- C02只確認行使文書的來源與類型；C03只確認是否置於可發生內容效用的狀態，不以持有或展示直接代替行使。
- C04確認對文書來源或不實內容的認識，C05確認使用行為、文書效用與證據來源的關聯。
- 單題、文書來源、使用行為及主觀認識均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/forgery_216_use_document-iteration-0-20261027.txt`，SHA-256 `DC3FA32F5DAFCB60A8E3CF8AC769D9D1B44EC0DFA828D5BCB5427FD864828091`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-28：`forgery_214_cause_official_false_entry` 問句設計參考標準

- C02只確認提出不實事項的內容、提出人及承辦公務員關係；C03只確認是否因此促成職務上公文書登載，不以提出陳述直接等同登載結果。
- C04確認足以生損害於公眾或他人的風險，C05確認提出、受理、登載與損害風險的因果資料。
- 單題、不實陳述、登載結果及損害風險均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/forgery_214_cause_official_false_entry-iteration-0-20261027.txt`，SHA-256 `2300D7DEAC95D3BBB85590082BEB87D4BB6B14FF49047D0FB5DC15FBF0BD0FD0`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-28：`forgery_213_official_false_entry` 問句設計參考標準

- C02只確認公務員身分、職務上掌管及公文書；C03只確認明知不實而登載的具體行為，不以公務員身分直接代替不實登載。
- C04確認足以生損害於公眾或他人的風險，C05確認職務權限、登載行為與損害風險的關聯及證據來源。
- 單題、公務員身分、不實內容及損害風險均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/forgery_213_official_false_entry-iteration-0-20261027.txt`，SHA-256 `53CAAFB018D19591DABBF5381D23EE8D2D1618DCFE780E66BA1CD9C27CA56122`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-28：`forgery_212_certificate` 問句設計參考標準

- C02只確認特種文書種類及偽造／變造事實；C03只確認足以生損害於公眾或他人的具體風險，不以證件外觀直接代替偽造。
- C04確認文件種類、製作名義及權限，C05確認偽造變造行為與損害風險的關聯及證據來源。
- 單題、證件外觀、文件種類及損害風險均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/forgery_212_certificate-iteration-0-20261027.txt`，SHA-256 `8B37DAE0FDFE69D189DCB4DB85CB64C2F0F1374BF52A99DF4FF1777E45BF4BDB`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-28：`forgery_211_public_document` 問句設計參考標準

- C02只確認公文書的製作機關、偽造或變造事實；C03只確認足以生損害於公眾或他人的具體風險，不以公文書外觀直接代替偽造。
- C04確認公文書製作機關、名義、內容及權限，C05確認偽造變造行為與損害風險的關聯及證據來源。
- 單題、公文書外觀、製作權限及損害風險均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/forgery_211_public_document-iteration-0-20261027.txt`，SHA-256 `0D8F6C4D7CDBD94A5FD28D4EE828D3D43D1F1F4C423BE970650097C9B0062343`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`forgery_210_private_document` 問句設計參考標準

- C02只確認私文書的製作、偽造或變造事實；C03只確認足以生損害於公眾或他人的具體風險，不以文件存在直接代替偽造。
- C04確認文書製作名義、內容及權限，C05確認偽造變造行為與損害風險的關聯及證據來源。
- 單題、文書外觀、製作名義及損害風險均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/forgery_210_private_document-iteration-0-20261027.txt`，SHA-256 `FB29E45415FAF50CD885B047A1625888F3AC0E26C45D36E9179B3C004A7ADEBD`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`defamation_313_credit` 問句設計參考標準

- C02只確認流言或詐術的具體內容；C03只確認信用受損的客觀事實與對象，不以負面評價直接代替信用損害。
- C04確認廣播、電視、電子通訊、網際網路或其他傳播工具態樣，C05確認損害程度、因果關係及證據來源。
- 單題、流言／詐術、信用受損及傳播工具均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/defamation_313_credit-iteration-0-20261027.txt`，SHA-256 `A7D8C60E9EFDA204A77E2453AD52059934BC1D939AE95E1AE4F30F2BAEF24E04`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`defamation_312_deceased` 問句設計參考標準

- C02只確認對象死亡身分及可核對資料；C03只確認公然侮辱或誹謗的具體內容，不以對象死亡直接推定犯罪成立。
- C04確認傳播情形與表意脈絡，C05確認死者名譽受損、內容及證據來源；不得由單一轉述或情緒反應補推要件。
- 單題、死者身分、侮辱／誹謗內容及傳播均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/defamation_312_deceased-iteration-0-20261027.txt`，SHA-256 `BA6C70502022B9BA20096C5A1AC4F457BB94CB9593164473C88F48C566647190`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`defamation_310_defamation` 問句設計參考標準

- C02只確認指摘或傳述的具體事項；C03只確認散布於眾、文字圖畫或其他傳播方式，不以「有人聽到」直接代替散布要件。
- C04確認名譽是否受損，C05確認真實性、公共利益、私德範圍及相當理由確信為真實的資料；不得由單一真實主張直接推定阻卻成立。
- 單題、具體指摘、散布範圍及真實性資料均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/defamation_310_defamation-iteration-0-20261027.txt`，SHA-256 `4ECD4E0138B5A7507B6125633EEC641D9F4DAB2FE9B267C0E57A373A507E658B`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`defamation_309_public_insult` 問句設計參考標準

- C02只確認具體言論、被害人及貶損內容；C03只確認公然性、傳播範圍與表意脈絡，不以主觀感受直接代替公然性。
- C04確認是否逾越一般人可合理忍受範圍，C05確認公共事務、文學藝術、學術專業等言論價值及第309條憲法限縮脈絡。
- 單題、侮辱用語、公然發表及名譽影響均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/defamation_309_public_insult-iteration-0-20261027.txt`，SHA-256 `82F7E2C259B711F5D03448D64E8D64EB5BF77C8E2B3E73916635513113C19B48`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`intimidation_346_property` 問句設計參考標準

- C02只確認恐嚇內容、被害人與財物關係；C03只確認使人交付財物或取得不法利益的具體行為，不以財物流向直接代替恐嚇要件。
- C04確認不法所有意圖，C05分開確認財產流向、既遂／未遂與證據來源；不得由單一交付或利益結果直接推定法律成立。
- 單題、恐嚇文字、交付結果、不法意圖及財產流向均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/intimidation_346_property-iteration-0-20261027.txt`，SHA-256 `E17A1714856D8968D17C01825768020F7187726E9AAE514AB3F9C603557C7686`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`intimidation_305_safety` 問句設計參考標準

- C02只確認恐嚇內容、告知事項、傳達對象及可核對資料；C03只確認實際傳達方式與時間，不以主觀感受或單一威脅說法直接成立。
- C04、C05分開確認安全危害的具體事實、時間、行為與危害關聯及證據來源；不得由恐懼感受直接補推法律效果。
- 單題、威脅文字、傳達紀錄及安全危害均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/intimidation_305_safety-iteration-0-20261027.txt`，SHA-256 `A9DA8375F5FB037D1CC3B7745940C81494CFB0C3B1DC2BF0B43EE1F7E265B1BD`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`damage_355_fraud` 問句設計參考標準

- C02只確認損害意圖、財產處分人及關係；C03只確認詐術如何使本人或第三人為財產處分，不以財產移轉或損害結果倒推詐術。
- C04、C05分開確認財產損害、金額、財產流向、行為與損害的關聯及證據來源；不得由單一說法補推因果或法律成立。
- 單題、損害意圖、詐術說法、財產處分及損害金額均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/damage_355_fraud-iteration-0-20261027.txt`，SHA-256 `92AAE4B7F4A6FA544C92EFB6F1725BCB29914A32E036D7745E99150213DB7D95`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---
## 2026-10-27：`damage_353_building` 問句設計參考標準

- C02只確認建築物、礦坑或船艦的客體與權利狀態；C03另確認毀壞或致令不堪使用的具體行為。
- 死亡或重傷結果、可預見性與行為因果分開追問；不由客體名稱、破損外觀或結果直接推論。
- 文書毀損、一般物毀損、詐術損害、損害債權與第357條程序為比較或分流路由；`UNKNOWN`、`CONFLICT` 全部保留 `NEED_REVIEW`。
- 單題、客體身分、毀壞行為或結果均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/damage_353_building-iteration-0-20261027.txt`，SHA-256 `AEEF1A96AC6111408B2BF4D4D3CFF02F9DBD86D72C779365F8B8415FDFBE7669`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---
## 2026-10-27：`damage_352_document` 問句設計參考標準

- C02只確認文書是否屬他人所有、持有或受保護的具體資料；C03另確認毀棄、損壞或致令文書不堪使用的具體行為。
- 足以生損害於公眾或他人的風險與行為關聯分開追問；不由文書名稱、破損外觀或事後主張直接推論。
- 一般物毀損、建築物毀損、詐術損害、損害債權與第357條程序為比較或分流路由；`UNKNOWN`、`CONFLICT` 全部保留 `NEED_REVIEW`。
- 單題、文書身分、毀損行為或損害風險均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/damage_352_document-iteration-0-20261027.txt`，SHA-256 `62244333E6BDDB74A05C11D3720638B4F08C3F0FF73FEB0B89251F742FF9114B`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---
## 2026-10-27：`injury_286_child_abuse` 問句設計參考標準

- C02只確認被害人未滿十八歲及年齡分層、身分與可核對資料；C03另確認凌虐或妨害身心健全發育的具體行為與期間。
- 營利意圖、死亡或重傷結果與行為因果分開追問；不由單一照顧關係、傷勢或結果直接推論。
- 普通傷害、重傷害、過失傷害、聚眾鬥毆與第287條程序為比較或分流路由；`UNKNOWN`、`CONFLICT` 全部保留 `NEED_REVIEW`。
- 單題、年齡身分、凌虐行為、營利或結果均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/injury_286_child_abuse-iteration-0-20261027.txt`，SHA-256 `A43D8C1AA2963C5E66F3E6A6B6559E269C453DAFF99A9D3862508FF3615FBC0E`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---
## 2026-10-27：`injury_284_negligent` 問句設計參考標準

- C02只確認注意義務來源、風險、可預見性與行為時情境；C03另確認違反注意義務的具體行為、不作為與替代措施。
- 傷害或重傷結果與過失行為因果分開追問；不由單一規則、結果、傷勢或事後說法直接推論。
- 普通傷害、重傷害、聚眾鬥毆、義憤、身分加重與第287條程序為比較或分流路由；`UNKNOWN`、`CONFLICT` 全部保留 `NEED_REVIEW`。
- 單題、注意義務、違反行為或結果均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/injury_284_negligent-iteration-0-20261027.txt`，SHA-256 `B64F8F87368126F249B90CCDE5AE20CAC64E20B1726D00E789FBF1F22F03554E`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---
## 2026-10-27：`injury_283_group_fight` 問句設計參考標準

- C02只確認聚眾鬥毆事件的參與人數、時間、地點與衝突行為；C03另確認在場位置與具體助勢或鼓動行為。
- 死亡或重傷結果與行為因果分開追問；不由單一在場、影像、傷勢或結果直接推論。
- 普通傷害、重傷害、義憤、身分加重、過失傷害與第287條程序為比較或分流路由；`UNKNOWN`、`CONFLICT` 全部保留 `NEED_REVIEW`。
- 單題、在場、助勢或結果均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/injury_283_group_fight-iteration-0-20261027.txt`，SHA-256 `BC5D0BE996507368FB5B12F9B179FBDBA067E75DF13B166DDF1073E6D9AB1A71`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---
## 2026-10-27：`injury_282_requested_self_harm` 問句設計參考標準

- C02只確認囑託、承諾、教唆或幫助傷害／自傷的具體態樣；C03另確認本人意思形成與外部資料。
- 死亡或重傷結果與行為因果分開追問；不由單一說法、關係或結果直接推論。
- 普通傷害、重傷害、義憤、身分加重、過失傷害與第287條程序為比較或分流路由；`UNKNOWN`、`CONFLICT` 全部保留 `NEED_REVIEW`。
- 單題、囑託、承諾、教唆、幫助或結果均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/injury_282_requested_self_harm-iteration-0-20261027.txt`，SHA-256 `1D1AC580E9A2DEE2C86EDD65772B9EAE27C35546E3C8DCAF42A7D4152B35BAAF`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`fraud_341_exploitation` 問句設計參考標準

- C02只問未滿十八歲、知慮淺薄、辨識能力顯有不足或相類情形的客觀資料，不替受訪者下診斷或法律結論。
- C03只問利用前項處境與財物或利益處分的外部時間、對話及因果脈絡；C04至C07分別處理處分、意圖、進度與證據。
- 第339條一般詐欺及第339條之1至之3為比較路由，不因設備、支付或電腦名詞單獨改變候選；`UNKNOWN`、`CONFLICT` 全部保留 `NEED_REVIEW`。
- 單題、年齡、理解能力、交付或事後流向均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/fraud_341_exploitation-iteration-0-20261027.txt`，SHA-256 `C57994B67CB7BFDC6753E8BAB2EE80FF4B0125C23500F4E6349E31787E1CC89A`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`injury_281_violence_ancestor` 問句設計參考標準

- C02只確認施強暴行為的時間、方式、對象與外部資料；C03另確認被害人為直系血親尊親屬的身分資料。
- 未造成傷害結果與身分關聯分開追問；沒有傷害結果不等於身分加重路由當然成立。
- 普通傷害、重傷害、義憤、過失傷害、兒少保護與第287條程序為比較或分流路由；`UNKNOWN`、`CONFLICT` 全部保留 `NEED_REVIEW`。
- 單題、家庭關係、強暴描述或未受傷均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/injury_281_violence_ancestor-iteration-0-20261027.txt`，SHA-256 `4BBA4E6C85CD2D7A5BE01037A5B71631D98E1781676E9A50DD9DC44684D54AE0`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`injury_280_ancestor` 問句設計參考標準

- C02只確認第277／278條基礎傷害行為；C03另確認被害人為直系血親尊親屬的身分資料。
- 身分證據、基礎行為與身分加重的關聯分開追問；稱謂、同住、家庭衝突或單一說法均不足以直接產生法律結論。
- 普通傷害、重傷害、義憤、過失傷害、兒少保護與第287條程序為比較或分流路由；`UNKNOWN`、`CONFLICT` 全部保留 `NEED_REVIEW`。
- 單題、身分、傷勢或家庭關係均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/injury_280_ancestor-iteration-0-20261027.txt`，SHA-256 `82C2B18667CD171182FF8E3D3ED37D44BBEA1B96A12973C1AC06E2CA50FCE8C8`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`injury_279_righteous_indignation` 問句設計參考標準

- C02只確認第277／278條基礎傷害行為；C03另確認當場性與激於義憤的事件脈絡，避免把衝突或情緒描述直接當成法律要件。
- 死亡結果、基礎行為關聯與證據來源分開追問；`UNKNOWN`、`CONFLICT` 全部保留 `NEED_REVIEW`。
- 普通傷害、重傷害、身分加重、過失傷害、兒少保護與第287條程序為比較或分流路由。
- 單題、衝突情緒、現場描述或死亡結果均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/injury_279_righteous_indignation-iteration-0-20261027.txt`，SHA-256 `2D564A69A421E1381C9F312FEB52010DB04F9D93718E79CF3C1BB16108B89723`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`injury_278_serious` 問句設計參考標準

- C02只確認造成重傷的具體行為、時間、部位與方式；C03另確認重傷結果、醫療／功能資料與行為間的外部因果脈絡。
- 死亡結果及未遂／既遂另列資料軸，不由單一診斷、照片、傷勢描述或單一說法直接推論。
- 普通傷害、義憤、身分加重、過失傷害、兒少保護與第287條程序為比較或分流路由；`UNKNOWN`、`CONFLICT` 全部保留 `NEED_REVIEW`。
- 單題、傷勢、醫療或結果均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/injury_278_serious-iteration-0-20261027.txt`，SHA-256 `A2635A963EE560A627A561B48A9B8D0FF35E31C45F2FFAF9D56B0F9C3DD515CC`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`injury_277_general` 問句設計參考標準

- C02只確認傷害身體或健康的具體行為、時間、部位與方式；C03另確認傷害結果、醫療資料與行為間的外部因果脈絡。
- 死亡或重傷結果另列資料軸，不由單一診斷、照片、傷勢描述或單一說法直接推論。
- 重傷、義憤、身分加重、過失傷害、兒少保護與第287條程序為比較或分流路由；`UNKNOWN`、`CONFLICT` 全部保留 `NEED_REVIEW`。
- 單題、傷勢、醫療或結果均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/injury_277_general-iteration-0-20261027.txt`，SHA-256 `25DB54D5452CD899DEFE924C2FB14262F1AD7370B5B65BAA18CA0468839E6AA0`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`fraud_344_1_aggravated_usury` 問句設計參考標準

- C02先確認第344條重利基礎行為；C03只問強暴、脅迫、恐嚇、侵入住宅、傷害、毀損、監控或相類方法的外部事實與來源。
- C04至C07分別保留重利結果、加重方法關聯、進度與證據的人工作業邊界；方法存在不等於路由成立。
- 一般重利、背信、詐欺與侵占為比較路由；`UNKNOWN`、`CONFLICT` 與未列入 scope 的方向全部保留 `NEED_REVIEW`。
- 單題、方法名稱、利息或付款均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/fraud_344_1_aggravated_usury-iteration-0-20261027.txt`，SHA-256 `45B601485DDBF5969AEF13224FE0CBECF6DAF452DA640C417699986D7062642A`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`fraud_344_usury` 問句設計參考標準

- C02只確認借款相對人的急迫、輕率、無經驗或難以求助處境的外部資料，不由身分、收入或單一敘述直接推論。
- C03至C05分別處理貸與內容、原本與利息／利益是否顯不相當、手續費等借貸相關費用；計算方式與付款紀錄分開追問。
- 詐欺、侵占、背信與加重重利為比較路由；`UNKNOWN`、`CONFLICT` 與未列入 scope 的方向全部保留 `NEED_REVIEW`。
- 單題、金額、利率或付款均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/fraud_344_usury-iteration-0-20261027.txt`，SHA-256 `4EC2D21FB275073F1F2289A4088ED0FA6F9765C4E20915B7027D371B9C677F92`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`fraud_342_breach_of_trust` 問句設計參考標準

- C02只確認為他人處理事務的委任、任用、契約或實際職務關係；職稱、信任稱呼或單一文件不足以直接認定。
- C03只確認任務內容、權限界線與違背行為的時間及外部資料；C04至C07分別保留利益／損害目的、損害結果、進度與證據的人工作業邊界。
- 詐欺、侵占、竊盜與重利為比較路由；`UNKNOWN`、`CONFLICT` 及未列入 scope 的方向全部保留 `NEED_REVIEW`。
- 單題、職稱、金額或損害主張均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/fraud_342_breach_of_trust-iteration-0-20261027.txt`，SHA-256 `B35F380B91E4486C963F17FCE91C74F26FD7AE58787FECD52DAC1E8935FB8C63`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`fraud_339_general` 問句設計參考標準

- 8 concepts 分開處理詐術、相對人錯誤、財產處分、損害流向、不法所有意圖、行為進度與證據來源。
- 不履約、付款、金額短少或單一不實說法均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- `UNKNOWN`、`CONFLICT`、既遂／未遂法律分類及未列入 scope 的設備／電腦／加重／背信／重利路線均保留人工審核邊界。
- 歸檔：`docs/evidence/question_route_archives/fraud_339_general-iteration-0-20261027.txt`，SHA-256 `192C5D75860732C03B40F0E576461260E4C7E689E13DCB71D2C64316FAC05034`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`fraud_339_4_aggravated` 問句設計參考標準

- C02確認第339條之4列舉加重態樣，C03另確認第339條基礎詐欺行為；不得以三人以上、公開傳播、身分冒用或不實影音單獨推定基礎詐欺成立。
- 其餘概念維持損害、流向、行為時意圖、進度與證據來源的分層追問；所有單題最高只到 `CANDIDATE_NEED_REVIEW`。
- `UNKNOWN`、`CONFLICT`、既遂／未遂法律分類及未列入 scope 的相鄰路線均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/fraud_339_4_aggravated-iteration-0-20261027.txt`，SHA-256 `17A029B78682F6271EDC98269C505F434C2DC6665058D7BAFD8546045A76ED73`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`fraud_339_3_computer` 問句設計參考標準

- C02確認輸入虛偽資料或不正指令，C03另確認系統影響後取得財物或不法利益；不得以單一紀錄差異反推全部要件。
- 其餘概念維持系統影響、財產流向、行為時意圖、行為進度與證據來源的分層追問；帳務差額或單一說法不得單獨升為 `ACTIVE`。
- `UNKNOWN`、`CONFLICT`、既遂／未遂法律分類及未列入 scope 的相鄰路線均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/fraud_339_3_computer-iteration-0-20261027.txt`，SHA-256 `4E2BF050E961EAA5AFF854DADD913502DE50C0FCA744FA502615843C987CF531`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`fraud_339_2_payment_device` 問句設計參考標準

- C02確認自動付款設備不正操作，C03另確認取得財物或不法利益；不得以付款結果反推操作方法。
- 其餘概念維持財產流向、行為時意圖、行為進度與證據來源的分層追問；帳務差額或單一說法不得單獨升為 `ACTIVE`。
- `UNKNOWN`、`CONFLICT`、既遂／未遂法律分類及未列入 scope 的相鄰路線均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/fraud_339_2_payment_device-iteration-0-20261027.txt`，SHA-256 `0B97EE3F02CC09F5F6A09DE16B271C4CFC7EE2D5667E9643FDD9645FE0329DDF`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`fraud_339_1_charge_device` 問句設計參考標準

- C02確認收費設備不正操作，C03另確認取得財物或不法利益；不得以付款結果反推操作方法。
- 其餘概念維持財產流向、行為時意圖、行為進度與證據來源的分層追問；不履約、帳務差額或單一說法不得單獨升為 `ACTIVE`。
- `UNKNOWN`、`CONFLICT`、既遂／未遂法律分類及未列入 scope 的相鄰路線均維持 `NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/fraud_339_1_charge_device-iteration-0-20261027.txt`，SHA-256 `5C804989A49803C5071FEA2D5A62EBC244433725FAA0B23E0F2FD163F8743422`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`embezzlement_337_lost_property` 問句設計參考標準

- C05只確認取得時是否為遺失、漂流或其他離本人持有；C06另查原持有人可辨識性、聯絡與回復脈絡，兩者不得以同一答案混代。
- C03、C04、C07引用既有欄位，完整時不共同出題，缺漏或衝突才追問；不得由「拾得」或未返還直接推定不法所有意圖。
- 單題、物品來源、原持有人可辨識性及後續處置均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/embezzlement_337_lost_property-iteration-0-20261027.txt`，SHA-256 `411A2B5191C59DEFD655A0F59E011E0AC62C77A1A63152822EB3F31DFFF6F15E`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED；獨立 Sol 工具面不可用，身份維持 `UNVERIFIED`。

---

## 2026-10-27：`embezzlement_336_2_business` 問句設計參考標準

- C05只處理業務職務、任用／委託、工作內容及實際職掌。
- C06只處理特定物與具體業務事項的持有關聯，不以抽象工作機會或職稱代替。
- C03、C04、C07引用既有欄位，完整時不共同出題，缺漏或衝突才追問；不得靜默覆蓋既有資料。
- 單題、業務身分、帳款短少及後續處置均不得單獨升為 `ACTIVE`；最高只到 `CANDIDATE_NEED_REVIEW`。
- 歸檔：`docs/evidence/question_route_archives/embezzlement_336_2_business-iteration-0-20261027.txt`，SHA-256 `642430642FE1027F350962E1349C4F340239B97D925E2F97E7F4CB60B7EB0F31`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。

---

## 2026-10-27：`embezzlement_336_1_public` 問句設計參考標準

- C05只處理行為時身分、任用／委託依據、法定職權及實際職掌。
- C06以互斥答案分開具體公務 nexus 與具體公益 nexus；公益泛稱、組織名稱或政府資金不足以單獨滿足。
- C03、C04、C07引用既有欄位，完整時不共同出題，缺漏或衝突才追問；不得靜默覆蓋既有資料。
- 單題、公務員身分、公有財產、帳款短少及後續處置均不得單獨升為 `ACTIVE`。
- 歸檔：`docs/evidence/question_route_archives/embezzlement_336_1_public-iteration-0-20261027.txt`，SHA-256 `D7149646B2FDB598DBE884F42A94A78790CB09F35C0CF196F7E6462BB48CC7C2`。
- 邊界：`QUESTION_DESIGN_ONLY`；runtime未改、法律結論為false、`CASE_HUMAN_GATE`仍為REQUIRED。
