# 現行法規版本定位稽核（2026-10-28）

> 本文件是 `AUDIT_REPORT`，不是法條正文或問句來源。查詢只使用法規名稱，未傳送任何案件資料。

## 三格查證卡

1. 問句：確認 route snapshot 所引用 10 部法規在 2026-10-28 的現行狀態、pcode、最新公布日、特殊施行日及官方來源。
2. 證據：`taiwan_legal_db.query_regulation` 回傳之全國法規資料庫 metadata；正式保存於 `legal_sources/law_versions.json`。
3. 痕跡：provider、查核時間、`case_data_sent=false`、法規名稱、pcode、日期及 `law.moj.gov.tw` URL 均保留；compiler 將其 hash 納入 source manifest。

## 邊界

- `last_amended` 是整部法規最新公布日，不證明每一個被引用條文都在該日修正。
- `effective_date=NOT_SEPARATELY_REPORTED` 只表示該次查詢未回傳特殊施行日，不代表所有條文必然自公布日施行。
- 後續精確查詢已確認 310 個 child route 所引用的現行條號／區間均可取得且無 missing，並完成現行條文摘要第一輪比對；條文可取得不等於仍具效力，例如第141條之1另依113年憲判字第9號維持排除。
- 第140條另依113年憲判字第5號保留合憲限縮要件，憲法效力證據保存於 `legal_sources/constitutional_route_verifications.json`。
- 未把法條全文混入 runtime，也未處理個案行為時法。
- 因此 route 與問句仍維持 `HUMAN_REVIEW_REQUIRED`。

## 條號存在性驗證

- 中華民國刑法：259 個 child route，255 個不同基本條號，分 6 批查詢，missing 0。
- 其餘 9 部法規：51 個 child route，分法規查詢，missing 0。
- 查詢批次與回傳數量保存在 `legal_sources/article_verifications.json`，並綁定 route snapshot SHA-256。

## 結果

| 法規 | pcode | 最新公布日 | 特殊施行日 |
|---|---|---|---|
| 中華民國刑法 | C0000001 | 2026-07-22 | NOT_SEPARATELY_REPORTED |
| 人口販運防制法 | D0080177 | 2023-06-14 | NOT_SEPARATELY_REPORTED |
| 兒童及少年福利與權益保障法 | D0050001 | 2021-01-20 | NOT_SEPARATELY_REPORTED |
| 家庭暴力防治法 | D0050071 | 2023-12-06 | NOT_SEPARATELY_REPORTED |
| 少年事件處理法 | C0010011 | 2023-06-21 | NOT_SEPARATELY_REPORTED |
| 性別平等工作法 | N0030014 | 2023-08-16 | 2024-03-08 |
| 性別平等教育法 | H0080067 | 2023-08-16 | 2024-03-08 |
| 性騷擾防治法 | D0050074 | 2023-08-16 | NOT_SEPARATELY_REPORTED |
| 毒品危害防制條例 | C0000008 | 2022-05-04 | NOT_SEPARATELY_REPORTED |
| 跟蹤騷擾防制法 | D0080211 | 2021-12-01 | NOT_SEPARATELY_REPORTED |
