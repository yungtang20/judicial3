# Phase 2 內建瀏覽器驗收

驗收工具：Codex 內建瀏覽器。資料：虛構「超商拾得手機案」。瀏覽器 console `error` / `warn`：0 筆。

| ID | 結果 | 實際證據 |
|---|---|---|
| B01 建立案件 | PASS | UI 輸入摘要、分析、保存；案件庫數量更新並取得 draft 案號與 Rev #1。 |
| B02 狀態與要件 | PASS | UI 顯示 6 facts，含 1 DENIED、2 UNKNOWN；候選 320、337 均為 UNRESOLVED，elements 為 INSUFFICIENT_DATA；未取得影像為 PENDING_SEARCH。 |
| B03 問句操作 | PASS | 實際新增、編輯、刪除問句及填入兩筆回答；保存、reload、案件庫重開後內容仍在。刪除目前沒有確認對話框，取消分支不適用。 |
| B04 修改與失效 | PASS | 將 fact #1 改為 UNKNOWN 後，UI 顯示 STALE／重新確認並把工作版本推進 Rev #2；服務層測試另證明 revision 1→2 與歷史保留。 |
| B04 重新分析失敗 | NOT_RUN | 尚無可由 UI 注入的分析服務失敗點；本機規則引擎同步執行。 |
| B05 保存與重開 | PASS | reload 後由案件庫載回摘要、facts、evidence、兩個 candidates、elements、10 題問句與回答。 |
| B06 畫面輸出 | PASS | 條陳預覽使用案件原文與「待查」標記，未填入虛構機關、員警或受理字號。 |
| B06 實際下載檔 | NOT_RUN | 內建瀏覽器可觸發按鈕，但其 download event 未取得 blob 產物，無法證明檔案存在／可開啟；Word 實作實際為 HTML `.doc`，不是 DOCX。 |
| B07 API 輸入與失敗 | PASS | nested payload 無效 enum／空 fact 回 400；未登入回 401；外部 AI 關閉回 503；production start 與本機保存均有行為測試。 |
| B07 網路中斷／重複提交 | NOT_RUN | UI 尚無可控網路故障注入；保存 API 也尚未實作 command idempotency。 |
| B08 表單可辨識 | PASS | 首頁、重新分析、問句、回答與條陳 textarea 已補 `aria-label`；focus 樣式存在。 |
| B08 鍵盤完整流程／axe | NOT_RUN | 內建瀏覽器鍵盤事件未能可靠移動焦點；repository 無可重跑 axe harness。不得以人工檢查替代 axe PASS。 |

## 實際發現並修復

1. 同一句中的承認、辯解與待確認事項原先未拆分，造成 DENIED／UNKNOWN 漏失；修正 clause splitting 與 UNKNOWN 優先序。
2. 新生成問句把「待釐清內容」預填成受詢人答案；改為空字串。
3. 保存後 320 與 337 都顯示 §339-4；修正候選 `statuteRef` 解析與逐候選資料庫映射。
4. 表單 label 未與 textarea 建立可辨識名稱；補上 `aria-label`。

## 尚未通過的 UX 項目

- 空白輸入沒有穩定、可讀的 inline error / `aria-live` 證據。
- 問句刪除沒有確認／取消流程。
- 保存失敗、網路中斷與重複提交缺少 UI 故障注入及冪等保護。
- 下載檔與 axe 仍需可重跑的 browser harness。
