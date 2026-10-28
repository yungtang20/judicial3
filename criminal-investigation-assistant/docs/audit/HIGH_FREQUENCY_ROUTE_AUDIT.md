# 高頻 route 條文內容比對（第一批，2026-10-28）

> 本文件是 `AUDIT_REPORT`。比對範圍為傷害、竊盜、加重竊盜、侵占、公共危險、妨害自由及恐嚇，共 39 個 child route。

## 證據

- 官方來源：全國法規資料庫，中華民國刑法，pcode `C0000001`。
- 法規最新公布日：2026-07-22。
- 精確查詢條號：36 個基本條號，missing 0。
- 案件資料傳送：無。

## 校正

| route_id | 問題 | 校正 |
|---|---|---|
| `aggravated_theft_321` | 「結夥三人」漏列法定的「以上」 | 改為「結夥三人以上」 |
| `injury_287_complaint` | 「公務員執行職務例外」主體不夠明確 | 明定行為人為公務員，且於執行職務時犯第277條第1項 |
| `liberty_302_1_aggravated_deprivation` | 籠統寫「未遂或既遂」會誤含第五款 | 明定未遂只及第一款至第四款；第五款須確認七日以上完成 |

校正以 `legal_sources/route_corrections.json` overlay 套用，原 imported snapshot 與 hash 保留不變。

## 狀態

- 條號存在性：`OFFICIAL_CURRENT_ARTICLE_EXISTS`。
- 上述三項內容校正：`OFFICIAL_ARTICLE_CORRECTED`。
- route 法律核准：仍為 `HUMAN_REVIEW_REQUIRED`；本批尚未完成判決、歷史法或機關內規核對。
