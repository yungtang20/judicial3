# OPEN_ISSUES

## 尚未完成

1. `analyze_candidates` 仍保留 legacy keyword route 作為候選入口；本次已加入語義調整與要件 metadata，但尚未完全改成獨立法律推理引擎。
2. `element_assessments.supporting_fact_ids`、`contrary_fact_ids` 目前只建立欄位，尚未由每個 assertion 自動完成精確 ID 綁定。
3. `fact_evidence_link` 已存在，但監視器、店員證述、手機定位等證據尚未由 UI 建立逐項證據鏈。
4. 問句已有核心／追問／區辨／證據核對 metadata，但尚未依回答內容即時只產生一題條件式追問；目前仍以既有每批 1–5 題 scheduler 為主。
5. 現行法條查證仍不等於行為時法、判決實務或機關內規確認；法律欄位維持 `HUMAN_REVIEW_REQUIRED`。
6. 尚未完成瀏覽器端針對 A/B/C/D 的完整互動驗收；本輪已完成後端決定性測試與 JavaScript 語法檢查。

## 風險處置

- 未知、矛盾及候選方向不得在 UI 或文件中顯示為犯罪成立。
- `candidate_role=UNRESOLVED` 時，不得跳過持有狀態、主觀認知及後續處理問句。
- assertion 新增只追加到 revision；不得刪除或覆寫歷史回答。
- 未完成人工法律審查的 route 維持既有 warning／Human Review 狀態。
