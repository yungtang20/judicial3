# 審查歷史封存

封存日期：2026-10-25

本目錄只保存不再作為目前正式來源的歷史審查資料。正式 runtime、測試與 Human Gate 證據不得依賴本目錄。

## 2026-10-project-reports

原路徑：`legal-case-web/review/`

內容為 2026-10 的盤點版本、環境診斷、部署說明、MVP 計畫、階段總結、結案報告與盲測報告，共 11 個 Git 追蹤檔。封存前已確認正式程式碼、測試與 `review/` 外部文件沒有引用這些檔名。

## review-1-legacy-copy

原路徑：`legal-case-web/review/1/`

- `discovery_quality_comparison.md`：與 `legal-case-web/review/discovery_quality_comparison.md` 完全相同的舊副本。
- `xlsm_review_draft.md`：與 `legal-case-web/review/xlsm_review_draft.md` 完全相同的舊副本。
- `visual_baselines_candidate/`：較早的未核准候選快照。PNG 與目前 canonical PNG 相同，但 `STATUS.json` 較舊。

目前 canonical 來源保留在 `legal-case-web/review/`。`legal-case-web/review/1/` 只保留仍由 Human Gate 證據引用的 E／E2 人工審閱筆記。

## 邊界

- 封存內容不表示已通過法律、資安、視覺或部署驗收。
- 封存內容不得加入 runtime import、pytest fixture、Docker image 或部署流程。
- 若需恢復歷史檔案，應從 Git 歷史或本目錄複製到新的明確工作區，不得直接把封存路徑當成正式來源。
