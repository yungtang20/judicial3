# Gold Dataset Report

## 狀態

- 已建立合成案例骨架：`legal-case-web/tests/fixtures/gold_dataset/case_custody_vs_theft.json`
- 評估器：`app/gold_dataset.py`（hypothesis recall 煙霧測試）
- **尚未**建立完整人工標註集與 Fact Extraction / Citation Accuracy 等全套指標 runner

## 原則

- 標準答案必須人工標註
- 禁止真實個資（`contains_case_data: false`）
- 分數是工程回歸用，不是法律驗收

## 建議後續案例類型

竊盜／侵占區別、詐欺／民事、主觀犯意不明、DENIED 與客觀矛盾、同源／反向證據、多人參與、時間地點不明。
