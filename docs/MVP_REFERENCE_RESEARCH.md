# JUDICIAL3 MVP 參考研究

研究日期：2026-10-29。執行模式：`SINGLE_AGENT_MODE`。

本文件區分「實際讀取來源」與「無法核實來源」，不把外部網站的功能或法律結論直接當成本系統的判斷結果。

## 1. 技術與法律來源

| 來源 | 類型 | 實際取得內容 | MVP 採用方式 | 限制 |
|---|---|---|---|---|
| [刑事訴訟法－全國法規資料庫](https://law.moj.gov.tw/LawClass/LawAll.aspx?PCode=C0010001) | 官方法規 | 可查到司法警察通知犯罪嫌疑人及證人到場詢問、筆錄製作及全程錄音錄影等條文內容 | 程式只保存法源 URL、法規版本待核對狀態；問句不直接代替法律結論 | 行為時法與機關內規仍須個案核對 |
| [警察刑事紀錄／警詢作法公開資料](https://www.cib.npa.gov.tw/ch/app/data/doc?detailNo=1046673163791896576&module=wg128&type=s) | 警政機關公開文件 | 可讀取通譯協助及警詢筆錄記載自白與不利陳述等內容 | 保留角色、來源、問句目的與人工審查欄位；不宣稱此頁等於完整內部手冊 | 公開頁面無法證明單位全部內部作業規定 |
| [刑法－全國法規資料庫](https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=C0000001) | 官方法規 | 作為第320、337、277、305、271等 registry 的官方查證入口 | 每個 registry route 保存法條 URL、版本待核對欄位及 human review 標示 | 本次未將法律資料庫內容自動推論成定罪 |
| [judicial-search-tool](https://github.com/ksliao0314/judicial-search-tool) | 開源技術參考 | README 實際描述關鍵字廣搜、逐筆 AI 精讀、candidate／confirmed／rejected 分層及人工確認 | MVP 採用「候選不等於確認」、保留人工審查及不可自動升級的設計 | 專案面向判決搜尋，不是警詢案件保存系統；不可直接複製其程式碼或法律結論 |
| [CAIL repository](https://github.com/china-ai-law-challenge/CAIL) | 開源資料／研究專案 | GitHub 頁面可確認 CAIL 專案及資料集研究背景 | 僅作資料集與評測設計參考，不納入臺灣法條或候選罪名來源 | 中國法資料集，不能直接作為臺灣刑事法律依據 |

## 2. 先前提供或專案既有紀錄中的來源

| 來源 | 本次狀態 | 可採用內容 |
|---|---|---|
| [TaiLexi](https://jp.tailexi.org/) | `NOT_VERIFIED`：本次工具讀取逾時；專案既有研究紀錄曾觀察到判決、法規、函釋、AI／MCP 導覽 | 只採用「法律資料檢索與引用應可回查」的 UX 原則；不宣稱內部實作 |
| [TWLawBot](https://twlawbot.com/) | `PARTIAL`：頁面可讀到 TaiLexi AI、判決／法條／函釋等品牌導覽，但內部能力不可由公開頁面證明 | 不作法律正確性或資料完整性證據 |
| [法源法律網 LawBank](https://www.lawbank.com.tw/SearchResult.aspx?membernotice=t) | `NOT_VERIFIED`：本次工具無法存取指定頁面 | 不以網站名稱或既有報告標籤推論功能 |

## 3. 研究如何影響 MVP

1. 候選法律方向採 `UNRESOLVED`／`ALTERNATIVE` 與人工審查，不把候選當定罪結論。
2. Fact、Evidence、Legal Element、Candidate、Question 分層保存；Evidence 的 `collection_status` 不由案情提及自動提升。
3. 問句綁定候選、要件、待查事實及調查目的，採中立描述，不要求回答「是否具有不法所有意圖」等法律評價。
4. 每次保存建立 revision；舊版結果不冒充目前版本。
5. 外部 AI／法律檢索不接收真實案件內容；本 MVP 的本機分析可以在無外部金鑰時運作。

## 4. 證據與讀取限制

- 本研究記錄的是 2026-10-29 可取得的公開頁面，不代表未公開的內部手冊、授權或資料庫內容。
- 法律適用版本、行為時法、內部警詢程序及證人具結規則仍須人工核對。
- 本文件是研究與設計依據，不是正式法律意見，也不會被 runtime 問句載入器當成資料來源。
