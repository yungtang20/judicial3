# Gate 1 事實契約與下游傳遞修正報告（LEGAL-GATE1-FACT-CONTRACT-008）

- 日期：2026-10-29
- 基準 commit：`c155633`（`feat(gate1): typed fact contract, contradiction links, and crash fix`）
- 專案：`legal-case-web`
- 五案法律標註狀態：**PENDING_HUMAN_REVIEW**。本報告不宣稱候選罪名正確，也不宣稱任何法律要件成立。

---

## 1. 結論摘要

| 項目 | 結果 |
| --- | --- |
| `analyze_gate1` 產生 typed facts（五案皆可執行） | PASS |
| `UNKNOWN` 保留（Gate 1 → `update_gate1` → `candidate_offenses` → `build_questions`） | PASS |
| 當事人否認與外部證據分開保存、可追溯 | PASS（僅 D 有此情境） |
| `create_case` → `candidate_offenses` 收到同一組 facts | PASS |
| `analyze_candidates` → `candidate_offenses` 收到 Gate 1 facts | PASS（修正前 FAIL） |
| `update_gate1` 移除事實後衍生狀態同步 | PASS（修正前 FAIL） |
| `approve_gate1` → `set_offenses` → `build_questions` → `mark_known_questions` 收到 facts | PASS |
| 五案候選罪名正確率 | NOT_VERIFIED（不得以本報告主張） |
| 全套回歸 | 709 passed / 2 failed（兩項失敗經 HEAD 基準比對，與本次修改無關） |
| 資料庫、HTTP、前端行為 | 未變更（DB、API、前端檔案未修改） |

---

## 2. 修改範圍（僅 2 個正式檔案 + 2 個新檔案）

| 檔案 | 修改 |
| --- | --- |
| `app/rules.py` | 新增 `FACT_UNKNOWN_LABELS` 單一對照表；新增 `recompute_fact_projections(gate1)`；`analyze_gate1` 改用同一份標籤表 |
| `app/workflow.py` | `update_gate1` 在 facts 變更後重算衍生狀態（含 UNKNOWN 標籤、矛盾連結）；`analyze_candidates` 將 `case["gate1"]` 傳入 `candidate_offenses` / `classify_candidates`，並在摘要被改寫時不傳 |
| `tests/test_gate1_fact_delivery_contract.py`（新增） | 17 項傳遞／狀態同步／證據分離測試 |
| `tools/gate1_fact_contract_audit.py`（新增） | 唯讀、可獨立重跑的五案稽核腳本 |

未修改：候選罪名排序／評分／產生規則、正式 Prompt、DB schema／遷移、前端、HTTP API、其他法律要件。

---

## 3. 修正前後差異（以同一支稽核腳本實測）

「修正前」= `c155633` 的程式（`git worktree` 另開 detached 樹），「修正後」= 本次工作樹。兩邊跑同一支 `tools/gate1_fact_contract_audit.py`；為讓腳本能在舊版載入，舊版副本另以 1 行 shim 補上當時還不存在的 `FACT_UNKNOWN_LABELS` 常數（除此之外未改任何程式邏輯）。

### 3.1 逐案檢查狀態

| 案例 | 修正前 | 修正後 | 修正前失敗的檢查 |
| --- | --- | --- | --- |
| BASE | FAIL | PASS | `update_gate1_unknown_sync`、`analyze_candidates_delivery` |
| A_RETAINED | FAIL | PASS | 同上 |
| B_LOST | FAIL | PASS | 同上 |
| C_HANDOVER | FAIL | PASS | 同上 |
| D_CONFLICT | FAIL | PASS | 同上（另 3 項 D 專屬檢查修正前後皆 PASS） |

### 3.2 兩個正式缺口（修正前的實際行為）

1. `update_gate1` 移除 `intent` 事實後：

   ```
   A) intent facts after: []
   A) unknowns still mention intent: True      # 「行為人的不法所有意圖」殘留
   A) unknowns before/after equal: True        # 衍生狀態完全沒重算
   ```

   修正後：`intent` 事實為 `[]`，`unknowns` 不再含該標籤，仍為 UNKNOWN 的
   `original_possession` 標籤保留，非 typed 的未知項（時間、客體、證據…）全部保留。

2. `analyze_candidates` 呼叫 `candidate_offenses(clean_summary, bank)`：

   ```
   B) gate1 passed to candidate_offenses is None: True
   ```

   修正後：`gate1 is None: False`，且候選端的 `unknown_fact_keys` 由「所有相依欄位」
   變成「facts 中實際為 UNKNOWN 的欄位」（BASE：`['original_possession','intent']`，
   A：`['intent']`）。

### 3.3 傳遞鏈（修正後實測）

| 邊界 | 證據方式 | 結果 |
| --- | --- | --- |
| `analyze_gate1` → `create_case` | 候選產生器 spy：收到 facts 與案件保存的 facts 完全相同（BASE 16 筆） | PASS |
| `case["gate1"]` → `candidate_offenses`（analysis 路徑） | spy 取得 `gate1`，非 `None`，facts 與案件一致 | PASS |
| 摘要被改寫時 | spy 取得 `gate1 is None`（span 不再有效，不得沿用） | PASS |
| `case["gate1"]` → `build_questions` | 正式 `approve_gate1` → `set_offenses` 路徑中以 spy 取得 `gate1`，facts 與案件一致 | PASS |
| `build_questions` → `mark_known_questions` | spy 取得 `gate1`，含 typed 契約欄位 | PASS |
| 問句不得把 UNKNOWN 當已知 | D 案 `original_possession`、`intent` 為 UNKNOWN，對應問句 `known_from_summary` 不為 `True`、狀態不為 `AUTO_FILLED_FROM_SUMMARY` | PASS |

---

## 4. 五案逐案結果（修正後，實際執行）

`typed facts` 為稽核腳本輸出；`candidate_ids` 僅為觀察值，不是預期答案。

| 案例 | typed facts（value｜assertion｜source｜verification） | unknowns（typed） | 矛盾 | 候選觀察 | 問句數 |
| --- | --- | --- | --- | --- | --- |
| BASE | original_possession=UNKNOWN｜UNKNOWN｜PARTY_STATEMENT｜UNKNOWN；intent=UNKNOWN｜UNKNOWN｜PARTY_STATEMENT｜UNKNOWN；taking=TAKING_OR_REMOVAL_ADMITTED｜ADMITTED｜PARTY_STATEMENT｜UNVERIFIED | original_possession, intent | 0 | theft | 20 |
| A_RETAINED | original_possession=POSSESSION_RETAINED｜ASSERTED｜PARTY_STATEMENT｜UNVERIFIED；intent=UNKNOWN；taking=TAKING_OR_REMOVAL_ADMITTED｜ADMITTED | intent | 0 | theft | 20 |
| B_LOST | original_possession=LOST_OR_OUT_OF_POSSESSION｜ASSERTED｜PARTY_STATEMENT｜UNVERIFIED；intent=UNKNOWN；taking=TAKING_OR_REMOVAL_ADMITTED｜ADMITTED | intent | 0 | （無） | 20 |
| C_HANDOVER | intent=UNKNOWN；post_acquisition_conduct=IMMEDIATE_HANDOVER_TO_STORE_STAFF｜ASSERTED｜PARTY_STATEMENT｜UNVERIFIED | intent | 0 | （無） | 20 |
| D_CONFLICT | original_possession=UNKNOWN；intent=UNKNOWN；taking=TAKING_OR_REMOVAL_DENIED｜DENIED｜PARTY_STATEMENT｜UNVERIFIED；taking=EVIDENCE_DEPICTS_TAKING_OR_REMOVAL｜ASSERTED｜EVIDENCE｜UNVERIFIED | original_possession, intent | 1 筆（2 個 fact_refs，`resolved_value=UNKNOWN`） | （無） | 20 |

所有 typed fact 都帶 `fact_id`、`proposition_key`、`event_id`，且 `source_start:source_end` 與 `source_excerpt` 完全相符（逐案以字串切片驗證）。

B、C、D 目前沒有規則候選，屬「候選關鍵字未命中」的既有候選產生行為；本次依邊界未調整候選規則，因此不列為失敗，也不宣稱候選正確。

---

## 5. 測試

### 5.1 新增測試 `tests/test_gate1_fact_delivery_contract.py`（17 項）

| 測試 | 驗證 |
| --- | --- |
| `test_audit_script_cases_match_lineage_fixtures` | 稽核腳本與契約測試使用同一組五案文字（防漂移） |
| `test_analyze_candidates_hands_case_facts_to_candidate_generator`（5 案參數化） | `analyze_candidates` 把 Gate 1 facts 傳給 `candidate_offenses`；`unknown_fact_keys` 由 facts 決定 |
| `test_analyze_candidates_does_not_attach_stale_facts_to_rewritten_summary` | 摘要改寫後不得沿用 span 對不上的 facts |
| `test_update_gate1_removes_stale_unknown_label_and_keeps_unrelated_unknowns` | 移除事實 → UNKNOWN 標籤同步移除；其他未知項與仍為 UNKNOWN 的標籤保留 |
| `test_update_gate1_restores_unknown_label_when_unknown_fact_returns` | 事實回復為 UNKNOWN → 標籤回復 |
| `test_update_gate1_keeps_unknown_label_for_assertion_class_only_unknown` | 客戶端只標 `assertion_class=UNKNOWN`（`machine_status=FACT`）時仍算未知 |
| `test_update_gate1_keeps_facts_derived_state_stable_when_facts_do_not_change`（5 案參數化） | facts 未變更時 8 項衍生狀態不漂移 |
| `test_update_gate1_does_not_flatten_denial_and_evidence` | 否認與證據維持兩筆 fact、矛盾連結不被壓平 |
| `test_formal_flow_passes_facts_into_build_questions_and_unknowns_stay_unknown` | 正式流程把 facts 傳入 `build_questions`；問句不得把 UNKNOWN 當已知 |

### 5.2 實際執行指令與結果

```
# 針對性（Gate 1 契約／lineage／delivery／workflow／rules）
python -m pytest tests/test_gate1_fact_lineage_contract.py tests/test_legal_fact_lineage.py \
  tests/test_gate1_fact_delivery_contract.py tests/test_workflow.py tests/test_rules.py \
  tests/test_p0_confirmed_rules.py -q
→ 135 passed

# 新增測試單獨執行
python -m pytest tests/test_gate1_fact_delivery_contract.py -q
→ 17 passed

# 全套
python -m pytest -q
→ 2 failed, 709 passed in 53.03s
```

### 5.3 兩項失敗的分類證據（不得僅以「既有」宣稱）

以 `git worktree add --detach <temp> c155633` 取得本次修改前的程式，直接跑同兩項測試：

```
python -m pytest tests/test_legal_retrieval_human_gate_packet.py::test_runtime_surfaces_are_hash_stable_and_unreachable \
  tests/test_question_family_catalog.py::test_every_family_has_a_current_readable_markdown_file -q
→ 2 failed
```

失敗訊息與修正後完全相同（`runtime_surfaces` sha256 封包記錄值不符；family template
文件產物與 catalog 輸出一致性）。因此這兩項在本次修改前即失敗，**不是本次造成**，
本次也依邊界未修改它們。

### 5.4 新測試的負向對照（證明測試抓得到原本的缺陷）

把新測試複製到 `c155633` 的 detached 樹執行（同樣只補 1 行常數 shim）：

```
python -m pytest tests/test_gate1_fact_delivery_contract.py -q
→ 8 failed, 9 passed
```

失敗項正是 `analyze_candidates` 傳遞與 `update_gate1` UNKNOWN 同步；修正後 17 項全過。
其中 `test_formal_flow_passes_facts_into_build_questions_...` 在修正前也通過，如實反映
`build_questions` 這條鏈原本就正確。

---

## 6. 可執行的稽核腳本

```
cd legal-case-web
python -m tools.gate1_fact_contract_audit
python -m tools.gate1_fact_contract_audit --json out.json
```

- 唯讀：只建立記憶體中的 case dict，不寫 DB、不呼叫 HTTP server、不呼叫 LLM。
- `analyze_candidates_v3` 在腳本內被強制為 `None`，只跑 deterministic 規則路徑，不可能連網。
- 每個案例輸出各檢查項的 `PASS`/`FAIL` 與說明，最後輸出 `overall`。
- 實測輸出：`overall: PASS`；完整結果存於
  `docs/evidence/gate1_fact_contract_audit_20261029.json`。
- 退出碼：`overall == FAIL` 時為 1，可直接接 CI。

檢查項：`typed_fact_contract`、`unknown_preserved`、`create_case_delivery`、
`update_gate1_unknown_sync`、`update_gate1_projection_stability`、
`analyze_candidates_delivery`、`stale_summary_guard`、`build_questions_delivery`，
以及 D 案專屬的 `denial_evidence_separated`、`contradiction_traceable`、
`contradiction_cleared_on_fact_removal`。

---

## 7. 已知限制與未確認事項（NOT_VERIFIED）

1. **法律正確性 NOT_VERIFIED**：五案標註仍為 `PENDING_HUMAN_REVIEW`；本報告只證明事實契約、狀態保存、證據追溯與傳遞，未證明候選罪名正確。
2. **B／C／D 無規則候選**：屬既有候選關鍵字命中行為，本次依修改邊界未調整；因此這三案的「候選是否正確」仍 NOT_VERIFIED。
3. **`_local_analysis_payload`（`app/server.py`）**：standalone 示範端點以 `classify_candidates(summary, BANK)` 執行，沒有案件 Gate 1 可用，因此仍不帶 facts。它不是案件流程，本次未修改；該路徑的 facts 傳遞為 NOT_VERIFIED。
4. **空 `fact_key` 的原始陳述事實**：敘事切段與 `default_unknowns` 產生的部分事實 `fact_key` 為空字串（BASE 有 4 筆），其 `proposition_key` 也可能為空。它們仍有 `fact_id`、來源 span、`machine_status` 與 `assertion_status`，但沒有 typed 語意標籤與統一命題鍵；typed 契約只保證 `original_possession`／`intent`／`taking`／`ownership_knowledge`／`third_party_possession`／`post_acquisition_conduct` 等欄位。是否要為所有事實補 typed key 與 proposition_key 屬下一步設計，未在本次處理。
5. **`update_gate1` 的衍生欄位覆寫**：當請求同時帶 `facts` 與 `evidence_leads`／`verified_evidence`／`consent_states`／`causal_edges`／`legal_characterizations` 時，這些「唯一來源是 facts」的欄位會以 facts 重算結果為準（`causation` 例外，明示輸入優先）。目前前端只送 `unknowns`／`causation` 與 legacy 陣列，未受影響；若有其他 API 用戶依賴手動覆寫這些欄位，需另行確認。
6. **`UNKNOWN` 標籤同步的範圍**：在「直接提供 `facts`」的更新路徑，`update_gate1` 只增刪 `FACT_UNKNOWN_LABELS` 中的 4 個 typed 標籤，其餘 `unknowns` 條目（承辦人手填）一律保留。若承辦人刻意手動填寫與 typed 標籤相同文字，該筆會被視為衍生值而重算。另有一條既有行為：只更新 `events`（未帶 `facts`）時，系統會以重新分析結果整體替換 `unknowns`，該路徑不保留手填的未知項；此行為本次未變更，若要保留需另外設計。
7. **本次未執行**：真實資料庫、HTTP API、前端瀏覽器、AI 外部分析路徑、DOCX 產生流程。上述皆 NOT_VERIFIED。

---

## 8. 可重現步驟

```
cd legal-case-web
python -m pytest -q
python -m tools.gate1_fact_contract_audit

# 修正前對照（可選）
git worktree add --detach %TEMP%\gate1-head c155633
copy tools\gate1_fact_contract_audit.py %TEMP%\gate1-head\legal-case-web\tools\
python -m pytest tests/test_legal_retrieval_human_gate_packet.py::test_runtime_surfaces_are_hash_stable_and_unreachable tests/test_question_family_catalog.py::test_every_family_has_a_current_readable_markdown_file -q
```

修正前的稽核腳本副本需補上 1 行 `FACT_UNKNOWN_LABELS`（該常數在 `c155633` 尚不存在），
除此之外不改任何邏輯；本報告的「修正前」數據即以此方式取得。
