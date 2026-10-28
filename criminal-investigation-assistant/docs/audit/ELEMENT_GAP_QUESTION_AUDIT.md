# 要件缺口與問句直接對應稽核（2026-10-28）

> 本文件是 `AUDIT_REPORT`，不得作為 runtime 問句來源。

## 問題

舊邏輯只以 `element_type`（例如 `mental_state`）記錄回答狀態。回答一題後，同一候選下所有同類型要件都會被標成 `ANSWERED_PENDING_REVIEW`，即使該題沒有問到那些具體要件。

## 修正

- 每個 `child_route_id + fact_element` 建立穩定 `route_element_key`。
- 每個尚未回答的具體要件產生一題中性、單一問號的 route 補強問句。
- 完全相同的要件文字可共用一題，但該題明確保存所有實際涵蓋的 key。
- 回答只更新問句所帶的 `route_element_keys`，不再以粗略的 `element_type` 一次清除其他缺口。
- 被害人、涉嫌人、證人使用不同角色語句；候選與問句仍標示 `HUMAN_REVIEW_REQUIRED`。
- 同一 parent 有多個 child route 時，以案情與已確認回答的明確線索排序；未命中的 child route 仍保留，不會被靜默排除。
- 線索最高的 child route 要件列為 `REQUIRED`；完成前 Gate 2 持續 fail closed。只有一個 child route 時，該 route 自動成為必要補強範圍。

## 覆蓋證據

- 310 個 snapshot child route。
- 1,025 個 route／要件配對。
- 三角色共 3,075 個直接對應關係。
- 811 個不重複要件文字；只在同字要件間共用問句。
- 測試逐一比對三角色問句所涵蓋 key 與全部 route element key 完全相等。

## 邊界

- 這是具體要件到問句的結構與執行對應，不等於人工法律核准。
- 動態補強題使用中性角色骨架包住已核對的要件摘要；仍需人工逐題潤飾專業術語與單位內部用語。
- 低相關 route 補強題維持條件題；候選範圍過廣時先靠家族骨架與回答縮小，避免把所有低可能路線塞入八頁文件。
- 優先分數只控制問句順序與必要範圍，不是犯罪成立分數，也不會把候選升格為法律結論。
