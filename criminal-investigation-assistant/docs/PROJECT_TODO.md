# 專案 TODO

## 已完成

- [x] 建立獨立專案與本機啟動入口。
- [x] 建立 15 個家族 Markdown 問句主檔。
- [x] 建立通用程序問句主檔。
- [x] 建立決定性 Markdown → JSON 編譯器、來源 lock、route 覆蓋矩陣。
- [x] 建立三份公司 DOC 的 hash 鎖定、LibreOffice 匯入與語義拆題 binding。
- [x] 建立不可變 case revision、CAS、冪等 command 與獨立 audit DB。
- [x] 建立 Gate 1 事實拆解與 Gate 2 每批 1–5 題動態重算。
- [x] 建立 Gate 2.5 條件案號。
- [x] 建立被害人、涉嫌人與無被害人移送分支。
- [x] 建立 DOCX、條陳 500 字、民國年與 LibreOffice 八頁 fail-closed。
- [x] 建立 Web UI、階段 TODO、候選卡、下載、複製與下一步。
- [x] 建立去識別法律查詢守門；外部連線維持停用。
- [x] 以官方法規資料定位 10 部 route 法規的 pcode、最新公布日、特殊施行日及來源 URL；未另報施行日時明確標示，不推測。
- [x] 以官方法規資料精確查詢 310 個 child route 的現行條號／條號區間；全部可取得且無 missing，僅標示條號存在，不升格法律核准。
- [x] 第一批比對 39 個高頻 child route 條文內容，建立 3 項可追溯 correction overlay，保留 imported snapshot 不變。
- [x] 第二批比對 79 個 child route，修正文書、隱私、詐欺及電腦路線共 6 項要件摘要。
- [x] 第三批比對 73 個 child route，修正毒品、性自主、人口販運及少年路線共 10 項要件摘要。
- [x] 第四批比對其餘 119 個 child route，修正 10 項要件摘要；另核對刑法第140條憲法限縮與第141條之1違憲失效排除。
- [x] 匯入並 hash 鎖定 44 個 parent／310 個 child route 結構快照。
- [x] 讓 15 個家族問句以 parent route 展開至 310 個 child route，並保留 `HUMAN_REVIEW_REQUIRED`。
- [x] 將每個家族擴充為至少 10 個事實軸，涵蓋核心、證據、區辨、有利及程序事實。
- [x] 建立家暴、未成年、性案件、跟蹤、通譯、夜間詢問、錄音中斷、代號被害人及職場／校園條件式程序模組。
- [x] Gate 2 顯示 child route、法條來源與逐項要件缺口，回答後僅標示 `ANSWERED_PENDING_REVIEW`。
- [x] 建立候選 `LOWERED` 相反線索與跨角色 `DISPUTED` 陳述隔離。
- [x] 建立 44 個 parent route 的明確候選觸發，並驗證 930 個 child-route／角色結構記錄的要件類型覆蓋。
- [x] 將 1,025 個 route／具體要件建立穩定 key，產生三角色共 3,075 個直接問句對應；回答不再誤清除同類型的其他缺口。
- [x] 依案情線索排序同一 parent 下的 child route 問句；高相關 child route 的具體要件列為必要問句，未答完不得完成 Gate。
- [x] 必要問句未答完前禁止完成 Gate；固定模板、程序、核心及區辨問句依優先序排程。
- [x] Gate 1 可修正 AI 推論／未知事實；相同值不會被誤升格為使用者確認。
- [x] 已確認回答可返回修正，修正會建立新 revision，並使候選、核准、案號及文件失效。
- [x] 無被害人／移送案件必須由使用者指定初始罪章／調查路線；路線只作待查證假設。
- [x] 建立本機附件上傳與 content-addressed 儲存；案件 revision 僅保存檔名、大小及雜湊 metadata。
- [x] 題庫／模板來源版本漂移時 fail closed，須明確 rebase 並重新確認 Gate 1。
- [x] 建立去識別化 audit 檢視；audit schema 不保存案情、姓名、案號、地點或回答。
- [x] 以 Codex 內建瀏覽器驗收首頁、Gate 1、Gate 2 child route 優先序、Gate 5、回答修正、家族頁、稽核頁及 375px 版面。

## 待法律／內規證據

- [ ] 現行條文內容與 route 要件摘要已完成 310 個 snapshot child route 的第一輪比對；仍須依案件行為時點核對歷史法、實務判決與機關內規。
- [ ] 將 `HUMAN_REVIEW_REQUIRED` 題目依證據升格；內容 hash 改變時重新失效。
- [ ] 確認警詢證人具結相關內部作業規定。
- [ ] 補入槍砲、組織犯罪、洗錢及贓物的正式 route crosswalk；目前四條 extension 維持 `BLOCKED`。
- [ ] 逐條完成人工法律審查及一般人語句潤飾；目前 310 個 snapshot child route 已有家族共用題、現行條文摘要與逐要件動態補強題，但不能宣稱 `HUMAN_LEGAL_APPROVED`。

## 暫緩／未授權

- [ ] 條陳最終正式版面。
- [ ] PostgreSQL／Supabase、RLS、登入及多人協作。
- [ ] Render 或其他外部部署。
- [ ] 真實案件資料匯入或外部 AI 傳輸。
