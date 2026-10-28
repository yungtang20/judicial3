# LEGAL-FACT-LINEAGE-007 事實血緣追蹤報告

## 結論

整體狀態：`PARTIAL_PASS`

本輪已在不修改正式推理邏輯的前提下，對相同原始摘要進行 A/B 單一事實變因測試，並追蹤 `analyze_gate1`、`candidate_offenses`、`build_questions` 的實際參數與輸出。

- `FACT`：Gate 1 facts 確實由 `app.workflow.create_case` 傳入 `candidate_offenses`。
- `FACT`：`candidate_offenses` 確實讀取 `gate1["facts"]`，但讀取用途主要是要件矩陣的原文 span 對應、支持事實引用及 typed `UNKNOWN` 缺口；候選初始加入仍由摘要關鍵字／場景規則控制。
- `FACT`：A、B 新增 facts 在相同摘要下被保留，但因沒有正式 `fact_key`、摘要 source span 或同步衍生陣列，未改變候選或問句輸出。
- `FACT`：診斷性加入 `fact_key="intent"` 且 `value="UNKNOWN"` 後，候選的 `unknown_fact_keys` 變為 `["intent"]`，問句輸出也改變。這證明下游並非完全不讀 facts，而是依賴特定欄位契約。
- `UNKNOWN`：尚未以正式 HTTP/API、歷史 revision、資料庫或原始錯誤執行 trace 重現第337條 `CANDIDATE`／第320條 `NEEDS_FACTS`。

## 一、實際函式與呼叫鏈

| 階段 | 程式位置 | 實際資料流 |
|---|---|---|
| 案件建立 | `app/workflow.py:305-319` | `analyze_gate1(intake, use_ai=False)` → `gate1` → `candidate_offenses(intake["summary"], bank, gate1)` |
| Gate 1 facts | `app/rules.py:1088` | 產生 facts、unknowns、來源位置、狀態欄位 |
| 候選產生 | `app/rules.py:2033` | `candidate_offenses(summary, bank, gate1=None)` |
| 要件矩陣 | `app/rules.py:249` 附近 `_route_element_matrix` | 讀 `gate1["facts"]` 的 `fact_id`、`source_start`、`source_end` |
| 候選補強／排序 | `app/rules.py:346` 附近 `_attach_element_evidence`、`2033` 後段 | 讀 facts 建立 supporting refs、unknown keys、rank factors |
| 問句 materialization | `app/workflow.py:748`、`app/rules.py:2735` | `build_questions(..., gate1=case["gate1"], candidates=case["candidates"], legal_route_ids=...)` |
| standalone server path | `app/server.py:159` | `_local_analysis_payload` 另呼叫 `classify_candidates(summary, BANK)`；本輪未執行 |

函式簽章由稽核腳本以 `inspect.signature` 實際記錄於 [LEGAL_FACT_LINEAGE_TRACE.json](D:/工作用/judicial1/legal-case-web/LEGAL_FACT_LINEAGE_TRACE.json)。

## 二、各階段資料依賴

### `analyze_gate1`

實際輸入是 `intake["summary"]`，在正式 `create_case` 中使用 `use_ai=False`。輸出包含：

- `facts`：來源文字、`fact_id`、`fact_key`、`source_start/source_end`、`assertion_status`、`machine_status` 等。
- `unknowns`：尚未確認事項。
- 衍生欄位：`events`、`people`、`objects`、`behaviors`、`evidence` 等。

`FACT`：來源陳述可被保留，但部分 facts 的 `fact_key` 為空字串；空字串不會自動變成 `original_possession` 或 `intent`。

### `candidate_offenses`

實際必要參數為：

```text
summary: str
bank: dict
gate1: dict | None
```

實際觀察：

1. 初始 `hits` 先由 `summary` 與 bank keywords／場景規則產生。
2. `_attach_element_evidence` → `_route_element_matrix` 讀取 `gate1.facts`，以 fact 的 `source_start/source_end` 是否覆蓋摘要匹配區間，建立 `supporting_fact_refs`。
3. 後段以 `value == "UNKNOWN"` 的 facts 收集 `fact_key`，再依候選 dependency 建立 `unknown_fact_keys`。
4. `candidate_rank_factors` 使用要件支持數、未知要求數及關鍵詞數；它是排序輔助，不是法律成立判斷。

因此，候選函式不是完全不讀 facts；但 facts 目前不能單獨建立摘要未命中的新候選方向。

### `build_questions`

實際必要參數包含：

```text
bank, role, offense_ids,
gate1, candidates, legal_route_ids
```

實際讀取包括：

- `source_summary`、`summary`、`objects`、`behaviors`、`events`：判斷特定問句包，例如錢包／提款卡情境。
- `gate1.facts` 是否存在具 `fact_key` 的 facts：影響 compact interview 模式。
- 後續 metadata enrichment／`mark_known_questions`：讀取 facts 對問句作已知／待查與目標標記。
- `legal_route_ids` 與候選 ID：控制 route element 對應與問句涵蓋。

`FACT`：問句不是只靠候選名稱；但 A/B marker 只有 facts 陣列，沒有同步建立正式衍生欄位或 typed key，因此本次直接函式重播問句未變。

## 三、單一變因測試

測試工具：[legal_fact_lineage.py](D:/工作用/judicial1/legal-case-web/tools/legal_fact_lineage.py)

測試保持原始摘要完全相同，只對複製的 Gate 1 facts 陣列追加測試資料；追加資料明確標為 `shadow:scenario:A/B`，不是原始案情證據。

| 測試 | 新增 facts | 摘要 | 候選輸出 | 問句輸出 | 首次差異 |
|---|---|---|---|---|---|
| A | 甲仍可實際支配、乙看見甲注意手機 | 不變 | `UNCHANGED` | `UNCHANGED` | facts 被保留，但下游可見輸出未變 |
| B | 甲離開後發現遺失、乙拾得時甲不在場 | 不變 | `UNCHANGED` | `UNCHANGED` | facts 被保留，但下游可見輸出未變 |

### 診斷性 typed fact probe

另加一個非案件測試資料的 probe：`fact_key="intent"`、`value="UNKNOWN"`。

- 基準候選：`unknown_fact_keys=[]`。
- typed probe 候選：`unknown_fact_keys=["intent"]`。
- 候選輸出：`DIFFERENT`。
- 問句輸出：`DIFFERENT`。

這不是 A/B 案情證據，也不能代表正式資料已有該欄位；它只證明下游對特定 typed fact contract 有實際依賴。

## 四、事實在哪裡被保留、忽略或消失

| 階段 | A/B 結果 | 判定 |
|---|---|---|
| 原始摘要 | 完全相同 | `FACT_CONFIRMED` |
| `analyze_gate1` facts | 新增 marker 存在於 `gate1.facts` | `FACT_CONFIRMED` |
| 傳入 `candidate_offenses` | `summary`、bank、完整 gate1 均傳入 | `FACT_CONFIRMED` |
| 候選初始命中 | 未因 marker 新增第337條或其他方向 | `FACT_CONFIRMED` |
| 要件矩陣 | 未引用沒有 source span 的 marker | `FACT_CONFIRMED`；`FACT_MAPPING_LOSS` 風險 |
| unknown fact keys | 空 `fact_key` marker 不形成 typed 缺口 | `FACT_CONFIRMED` |
| route／排序 | A/B 候選未變，未出現新 route | `NOT_OBSERVED` 對原始輸出；影子結果為 `UNCHANGED` |
| `build_questions` | A/B marker 未造成問句差異 | `FACT_CONFIRMED` |
| 正式 HTTP／前端／DB | 本輪未執行 | `NOT_RUN` |

## 五、分類

### `FACT_NOT_PASSED`

`RULED_OUT`（就 `create_case` 初始流程而言）。

證據：`app/workflow.py:305-319` 明確將 `gate1` 傳給 `candidate_offenses`；`app/workflow.py:748` 明確將 gate1 傳給 `build_questions`。

### `FACT_NOT_CONSUMED`

`CONTRIBUTING_FACTOR`，但不是「完全未消費」。

證據：A/B marker 未改變候選或問句；然而 typed `intent=UNKNOWN` probe 改變 `unknown_fact_keys` 與問句，表示消費邏輯存在，只接受特定欄位契約。

### `FACT_MAPPING_LOSS`

`CONTRIBUTING_FACTOR`。

證據：A/B marker 沒有 `fact_key`、`source_start/source_end`，且沒有透過 `workflow.update_gate1` 重新建立 `events/objects/behaviors`；因此無法進入目前下游的 typed unknown、source-span 對應或 compact 問句判斷。這是測試觀察到的資料契約限制，不是原始錯誤的唯一根因。

### `CANDIDATE_GENERATION`

`RISK_NOT_REPRODUCED`。

候選初始命中以摘要關鍵字／場景規則為入口，A/B 事實不會單獨新增候選。若設計目標是先廣泛檢索，這可屬於 `INTENTIONAL_STAGE_SEPARATION`；但目前沒有證據證明第337條應在該 bank／版本中被保留，也沒有原始輸出 trace 證明它在後續階段被移除。

### `ELEMENT_ASSESSMENT`

`CONTRIBUTING_FACTOR`。

要件矩陣會使用摘要 source span 與 facts 的位置交集；沒有 source span 的新增 facts 不會成為 supporting refs。這說明要件評估存在 facts 依賴，但 A/B marker 未符合其輸入契約。

### `QUESTION_GENERATION`

`CONTRIBUTING_FACTOR`／`RISK_NOT_REPRODUCED`。

`build_questions` 會讀 gate1 的摘要衍生欄位、typed facts 及 route IDs；A/B marker 未觸發這些欄位。正式 workflow 的 `update_gate1` 會從 facts 重建部分陣列，但本輪未執行完整 HTTP 或案件 revision 流程，因此正式顯示結果仍是 `UNKNOWN`。

## 六、刻意分工與可能缺陷

### 可由程式證實的刻意分工

- 初始候選先使用摘要／關鍵詞／場景規則廣泛建立方向。
- 要件矩陣與 supporting refs 在候選建立後補強。
- 問句必須在 Gate 2 選定 offense／route 後 materialize，未選方向不自動進入正式筆錄。

### 可能缺陷或契約風險

- 來源陳述可存在，但若沒有 `fact_key`、source span 或衍生欄位，對下游候選／問句的影響很有限。
- 新增事實若只寫入 `facts` 而未經正式 `update_gate1` 的欄位重建，可能被保存但不被後續規則使用。
- 初始候選未因「已遺失／拾得」類結構化 facts 增加第337條方向；這可能是合理的廣泛候選契約，也可能是候選規則覆蓋缺口，現有證據不足以二選一。

## 七、最小修正方案（本輪未執行）

1. 先定義並測試正式 fact contract：`fact_key`、`value`、`assertion_status`、`machine_status`、`source_start/source_end`、`source_ref` 的必要性與 UNKNOWN 語義。
2. 在 `app/workflow.py` 的 Gate 1 更新與候選重算邊界，保存完整 provenance 並明確重建衍生欄位；不要只把 facts 直接塞入候選函式。
3. 在 `app/rules.py` 分離「候選檢索」與「要件評估」：候選可由摘要廣泛進入，但需用 typed facts 對第320條／第337條所需要件產生可追溯的 unresolved／alternative 結果。
4. 在 `build_questions` 以 fact gap／element ID 產生問句，並保留來源狀態，不把 `ASSERTED` 升格成 VERIFIED。
5. 新增回歸測試：相同摘要下 A/B facts 必須出現在候選要件矩陣／問句 metadata 的追蹤結果；同時允許候選名稱不變，但不可靜默遺失 facts。

開始正式修改前仍需補：固定 revision 的正式 API trace、完整 candidate／route／question payload，以及原始第337／320 組合的來源紀錄。

## 八、驗證

```powershell
cd D:\工作用\judicial1\legal-case-web
python tools\legal_fact_lineage.py
pytest -q tests\test_legal_fact_lineage.py
python -m py_compile tools\legal_fact_lineage.py tests\test_legal_fact_lineage.py
```

本輪結果：

- lineage 稽核腳本：PASS。
- lineage 測試：`3 passed`。
- Python compile：PASS。
- LLM／資料庫／HTTP／前端：`NOT_USED`。
- 正式候選規則、Prompt、Schema、資料庫及案件流程：未修改。

