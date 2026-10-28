# 臺灣刑事案件離線評估契約

版本：`tw-legal-eval-v1`

## 1. 邊界

本契約只規範離線 sidecar。它重播既有 `analyze_gate1(use_ai=False) → candidate_offenses → build_questions`，不接入正式 Runtime、不修改候選規則、Prompt、資料庫或題庫。

評估資料的人工標準（gold）與待測系統輸出（DUT）必須分離。DUT 必須從 `raw_summary` 自行抽取 facts；gold facts 不得注入主要候選路徑。Fixture 狀態為 `INITIAL_REGRESSION_BASELINE_WITH_CONDITIONS`；A、B、D 的候選集合附有事實條件，不得脫離驗證狀態當成固定法律答案，也不代表任何犯罪已成立。

## 2. 追蹤鏈

每次重播保留以下節點及連線：

`raw source span → fact → legal element → candidate parent/route → question gap`

每個節點必須有穩定 ID。引用不存在、span 越界、span 文字不符或來源類型缺失均為 hard finding，不得以空值默默通過。

陳述類型、驗證狀態及要件狀態分開：

- `assertion_class`: `ASSERTED | ADMITTED | DENIED | INFERRED | UNKNOWN`
- `verification_status`: `UNVERIFIED | CORROBORATED | CONTRADICTED | UNKNOWN`
- `element_state`: `SUPPORTED | CONTRADICTED | UNKNOWN | NOT_APPLICABLE`

`machine_status=FACT` 只表示來源文字中有明示片段，不表示內容已獨立證實。`NOT_CHECKABLE` 是工具覆蓋狀態，不是要件正確或不成立。

## 3. 候選集合與排序

評估固定在 parent candidate ID 層，`K=3`，並保留 DUT 原始排序。人工標準分成：

- `required`: 偵查初期不得漏列的合理方向。
- `acceptable`: 可以保留但非必要的方向。
- `prohibited`: 依 fixture 契約不得自動列入的方向；進入 Top-K 即 hard fail。

計算方式：

- `Recall@K = |TopK ∩ required| / |required|`；required 為空時 `NOT_APPLICABLE`。
- `Precision@K = |TopK ∩ (required ∪ acceptable)| / |TopK|`；TopK 為空時 `NOT_APPLICABLE`。
- 同分不自行重排；以 DUT 回傳順序為準。

候選命中不等於犯罪成立、人工核准或法律適用。`Citation Mention`、`Legal Source`、`Legal Applicability Candidate`、`Applied Legal Basis` 必須分離；引用解析不得驅動候選 eligibility。

## 4. 六項初始指標

1. `candidate_recall_at_k`：required candidate 的涵蓋率。
2. `candidate_precision_at_k`：Top-K 中 required 或 acceptable 的比例。
3. `element_mapping_accuracy`：人工要件狀態與 DUT 可觀察矩陣的一致率。`NOT_CHECKABLE` 另計工具覆蓋，不算正確。
4. `unknown_preservation_rate`：gold 中明示 UNKNOWN 且具有 typed `fact_key` 的項目，在 DUT 中仍以 UNKNOWN 保留的比例。完全缺失不算保留。
5. `question_coverage_rate`：人工未決 gap 是否由 gold-selected parent/route 的實際 `build_questions` 輸出覆蓋。自動候選不得直接充當人工選取結果。
6. `source_trace_completeness`：source span、fact、element、candidate、question、legal source 各節點與引用的完整率。

每個 case 另外輸出依 `facts → elements → candidates → questions` 排序的 `first_divergence_stage`。只有實際 DUT 資料可作觀察值，預期值不得冒充執行結果。

## 5. 法律來源及時間

法律來源至少記錄法規、條號、版本、官方 URL、擷取時間、內容雜湊、解析器版本、行為時間及版本適用狀態。行為時間未知或缺乏歷史法版本時，適用狀態只能是 `UNKNOWN`，不得標成 PASS。

本版 fixture 的法律來源是離線 metadata；sidecar 不連線驗證官方內容。LLM、資料庫、HTTP、前端與外部服務均為 `NOT_USED`。

## 6. 反突變與可重播性

測試至少涵蓋：

- 錯誤候選或 prohibited-first 會失敗，且 gold hash 不變。
- K 邊界、空候選、acceptable-only。
- UNKNOWN 被升格、陳述被當成已驗證、D 案矛盾消失會失敗。
- 來源引用不存在、span 越界或文字不符會失敗。
- 只增加法條引用文字不得改變候選。
- 相同 fixture/rules/bank/crosswalk/law snapshot 的語義輸出可比較；非語義時間欄位不得納入 hash。

## 7. 完成邊界

首批 5 案只建立回歸基線，不足以證明整體法律推理品質。評估失敗代表已定位的契約差異，不代表工具執行失敗；只有 fixture/schema/執行錯誤才回傳非零退出碼。通過人工審核前，不得整合正式 Runtime。
