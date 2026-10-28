# 臺灣案件推理離線評估報告

- Trace version: `tw-legal-eval-trace-v1`
- Fixture: `INITIAL_REGRESSION_BASELINE_WITH_CONDITIONS`（reviewer: `USER_REVIEWED_CONDITIONAL_2026-10-29`）
- Determinism: `PASS` / 3 runs
- Overall: `PARTIAL_PASS`

## 個案結果

| Case | First divergence | Recall@3 | Precision@3 | Element | Unknown | Question | Trace | Hard findings |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `phone-baseline` | `FACT` | 0.50 | 1.00 | 0.00 | 1.00 | 0.50 | 0.50 | none |
| `phone-possession-retained` | `FACT` | 1.00 | 1.00 | 0.50 | 1.00 | 1.00 | 0.83 | none |
| `phone-lost` | `LEGAL_ELEMENT` | 0.00 | N/A | 0.00 | 1.00 | 1.00 | 0.67 | none |
| `phone-immediate-handover` | `FACT` | N/A | N/A | 0.00 | 1.00 | 0.33 | 0.50 | none |
| `phone-denial-cctv-conflict` | `LEGAL_ELEMENT` | N/A | N/A | 0.00 | 1.00 | 0.75 | 0.50 | none |

## 邊界與結論

- 主要候選 lane 只接收 raw summary 經既有 `analyze_gate1` 產生的 facts；人工 gold facts 未注入。
- 問句 lane 使用人工預先選定的 parent/route，避免把所有自動候選誤當成人工核准方向。
- `NOT_CHECKABLE` 只表示工具未涵蓋，不計為正確要件判斷。
- 法規行為時間與歷史適用性為 `UNKNOWN`，來源追溯不得宣稱完整 PASS。
- 本結果只定位契約差異，不代表原始候選偏差已定位或修復。

## 獨立設計審查決策

- 執行模式：`REVIEWED_PIPELINE`；獨立 reviewer 的實際模型身分為 `UNVERIFIED`，不得標記 DUAL_MODEL_PASS。
- `ACCEPT`：gold/DUT 分離、精確來源 span、draft gold 狀態與 mutation test。
- `ACCEPT`：required/acceptable/prohibited、固定 parent ID layer 與 K 邊界。
- `ACCEPT`：問句採 gold-selected lane，不由全部自動候選直接生成評估結論。
- `ACCEPT`：來源追蹤為 source→fact→element→candidate→question 圖，不以 citation 命中判定適用。
- `ACCEPT`：assertion、verification、element state 分離；UNKNOWN promotion 與 D 案矛盾消失為 hard finding。
- `ACCEPT_WITH_MODIFICATIONS`：法律時間與外部法源在本輪維持 UNKNOWN/NOT_USED，不以網路補值。

## 未執行

- LLM、資料庫、HTTP、前端、歷史 revision、正式端到端：`NOT_RUN`。
