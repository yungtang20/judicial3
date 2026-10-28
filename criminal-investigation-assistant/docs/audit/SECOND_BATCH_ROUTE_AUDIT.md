# route 條文內容比對（第二批，2026-10-28）

> 本文件是 `AUDIT_REPORT`，不是正式問句來源。比對範圍為殺人、墮胎、遺棄、毀損、強盜搶奪、詐欺背信、文書、名譽、隱私及電腦，共 79 個 child route。

## 證據

- 官方來源：全國法規資料庫現行法條。
- 精確查詢：各 route 引用條號及條號區間；不存在條號為 0。
- 案件資料傳送：無，只傳法規名稱與條號。

## 校正

| route_id | 問題 | 校正 |
|---|---|---|
| `forgery_218_official_seal` | 把「足生損害」誤套到偽造公印／公印文 | 只在盜用公印／公印文時列為明文要件 |
| `privacy_315_2_profit_facilitation_distribution` | 三種行為與目的混成一項 | 分開供給場所設備、竊錄目的及製造散布等態樣 |
| `privacy_319_1_nonconsensual_sexual_image` | 把替代目的寫成「營利散布」組合 | 改為營利、散布、播送、公然陳列或供人觀覽等替代目的 |
| `privacy_319_2_coerced_sexual_image` | 同上 | 同步拆開替代目的 |
| `fraud_339_4_aggravated` | 冒用名義漏列政府機關 | 改為政府機關或公務員 |
| `computer_362_malware` | 只有供犯罪意圖，漏列實際供犯罪及致損害 | 補入供自己或他人犯本章之罪及致生損害 |

校正由 `legal_sources/route_corrections.json` overlay 套用；原 imported snapshot 與 lock 不變。

## 狀態

- 條號存在性：`OFFICIAL_CURRENT_ARTICLE_EXISTS`。
- 六項內容校正：`OFFICIAL_ARTICLE_CORRECTED`。
- 法律核准：維持 `HUMAN_REVIEW_REQUIRED`；尚未完成歷史法、判決及機關內規核對。
