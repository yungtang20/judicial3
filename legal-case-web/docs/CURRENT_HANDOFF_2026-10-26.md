# Legal Case Workbench 當前交接手冊（2026-10-26）

## 1. 本次交接目標

下一階段先執行「財產罪代表案例的本機橫向驗收」，不要部署、不要擴張全部罪章，也不要把候選方向寫成法律結論。

驗收目的：確認同一套流程面對不同財產取得型態時，仍能維持 20 題上限、問句不重複、條陳單一案由、純事實摘要及可下載 DOCX。

## 2. 專案與執行邊界

- 專案：`D:\工作用\judicial1\legal-case-web`
- 正式本機入口：`http://127.0.0.1:8787/`
- 啟動命令：`./start.ps1`
- 健康檢查：`GET http://127.0.0.1:8787/api/health`
- 正式 runtime：`Browser -> app/server.py -> app/workflow.py -> app/rules.py / app/questions.py -> app/documents.py`
- 測試瀏覽器：只使用 Codex 內建瀏覽器。
- 測試資料：只能使用虛擬、去識別化案件，不得輸入真實個資或卷證。
- 本階段禁止部署、push、commit、reset、clean、checkout 或清理既有變更。
- 工作樹已有大量使用者及先前工作留下的未提交變更；只修改本階段缺陷直接涉及的檔案。
- Human Gate、法律來源核准狀態及證據鏈不得由 AI 自行改成已核准。

## 3. 已完成且已驗證

### 功能

- 問句實務上限為 20 題，超出題目會裁切並保留提示。
- 問句已有精確文字去重防線。
- Enter 可保存目前回答並自動移到下一題；Shift+Enter 保留換行。
- 可以從輸出階段返回問答、查看並修改本案問句與答案。
- 條陳案由與保存案件名稱分離：條陳不含年月日及員警姓名。
- 條陳案由只顯示一個主要方向，不串接「竊盜、侵占」兩個案由。
- 條陳抬頭在 intake station 為空白或 `○○所` 時，使用 Gate 2.5 管轄資料，例如 `虛擬派出所報告`。
- 條陳「五、案情摘要」只保留案件事實，不加入「仍應查明」「候選方向」等分析文字。
- LibreOffice 文件 renderer 已在本機健康檢查顯示 `READY`。

### 目前驗證基線

2026-10-26 實際執行：

```text
pytest -q                         -> 629 passed in 53.81s
node --check app/static/app.js   -> PASS
GET /api/health                  -> HTTP 200
document_renderer                -> READY
mode                             -> LOCAL_ONLY
external_ai_enabled              -> false
```

Codex 內建瀏覽器已實際完成兩輪模糊竊盜／侵占案件流程，包含：建案、20 題回答、Enter 換題、年籍、Gate 2.5、條陳、返回修改及兩種 DOCX 下載按鈕。

### 本輪直接相關檔案

- `app/case_identity.py`
- `app/documents.py`
- `tests/test_case_identity_and_brief_template.py`
- `tests/test_virtual_case_wallet_atm.py`

新增回歸案例：`tests/test_virtual_case_wallet_atm.py::test_ambiguous_theft_or_embezzlement_case_keeps_single_brief_reason_and_factual_summary`

## 4. 下一步：財產罪本機橫向驗收

依序使用 Codex 內建瀏覽器建立下列四個虛擬案例。每個案例都要走完整流程，不得只呼叫 API：

1. 竊盜／侵占遺失物界線：物品短暫離開本人視線，但是否仍在支配範圍不明。
2. 普通侵占：對方原本因借用或保管合法持有，之後拒不返還或處分。
3. 強奪／強盜界線：突然取物，是否有對人施強暴、脅迫及是否達不能抗拒程度不明。
4. 皮夾、金融卡及後續提款：分開呈現原始取物與後續使用行為，避免把後行為機械地重複列成多個案由。

每案驗收下列項目：

- 系統自動產生候選方向，不要求使用者先從大量罪名中自行選擇。
- 最終問句為 1 至 20 題，精確重複數為 0。
- 問句包含核心、相鄰罪名區分及必要爭點，但不重複通用告訴、民事、證據與管轄題。
- Enter 後焦點留在下一題輸入框，可連續輸入。
- 條陳受理案由只顯示一個主要方向；不把候選清單直接當案由。
- 發生地點顯示地址；條陳抬頭只顯示派出所／分局名稱。
- 案情摘要為主管可閱讀的時間順序事實，不加入法律分析。
- 返回問答後可修改問句及答案，再次核准後資料仍一致。
- 筆錄實際排版不超過 8 頁；超過時必須 fail closed，禁止下載。
- 筆錄 DOCX 與條陳 DOCX 均可下載，且條陳含正確管轄、員警、報案時間及證明單號。

發現缺陷時：先建立最小可重現案例，再做最小修改，加入對應回歸測試，重跑相關測試及完整測試。不得為通過測試而刪除 assertion、skip、xfail 或降低既有防線。

## 5. 建議閱讀入口

先讀：

1. `README.md`
2. `docs/QUESTION_DESIGN_AND_USE.md`
3. `app/workflow.py`
4. `app/rules.py`
5. `app/questions.py`
6. `app/documents.py`
7. `app/case_identity.py`
8. `app/static/app.js`
9. `tests/test_virtual_case_wallet_atm.py`
10. `tests/test_question_logic.py`
11. `tests/test_frontend_api_errors.mjs`

若工作轉為罪章問句工作單，才改讀 `docs/AI_HANDOFF_PROMPT.md` 與 `docs/QUESTION_WORK_ITEM.md`；本次橫向驗收不得自行開始下一個 route。

## 6. 驗證命令

在 `D:\工作用\judicial1\legal-case-web` 執行：

```powershell
./start.ps1
py -3 -X utf8 -m pytest -q
node tests/test_frontend_api_errors.mjs
node --check app/static/app.js
Invoke-WebRequest http://127.0.0.1:8787/api/health -UseBasicParsing
```

如果只驗證本輪核心範圍，可先執行：

```powershell
py -3 -X utf8 -m pytest -q tests/test_virtual_case_wallet_atm.py tests/test_case_identity_and_brief_template.py tests/test_workflow.py tests/test_documents.py
```

完整測試仍是最後必要條件。

## 7. 已知限制與風險

- 目前正式服務使用記憶體案件儲存；重啟服務後案件會消失。
- 629 個測試通過是工程回歸證據，不是法律正確性或 Human Gate 核准。
- 外部 AI 目前停用；不得假設模型已參與罪名判斷。
- 問句不超過 20 題不等於 DOCX 必然不超過 8 頁，仍須以 LibreOffice 實際排版頁數判定。
- 工作樹非乾淨狀態；不得把全部變更視為本輪修改，也不得批次提交。

## 8. 新對話可直接貼上的指令

```text
MODE: IMPLEMENT
TARGET: D:\工作用\judicial1\legal-case-web

請先完整閱讀：
D:\工作用\judicial1\legal-case-web\docs\CURRENT_HANDOFF_2026-10-26.md

依交接手冊執行「財產罪本機橫向驗收」。

要求：
1. 只使用 Codex 內建瀏覽器操作 http://127.0.0.1:8787/。
2. 只使用虛擬、去識別化案件。
3. 依序完成竊盜／侵占遺失物、普通侵占、強奪／強盜、皮夾金融卡後續提款四個案例。
4. 每案完整驗證 20 題上限、零精確重複、Enter 連續輸入、單一條陳案由、純事實摘要、返回修改、8 頁上限及兩種 DOCX。
5. 發現缺陷時先建立最小重現，再最小修改並加入回歸測試。
6. 保留現有 dirty worktree，不得 reset、clean、checkout、覆蓋無關修改、commit、push 或部署。
7. 不得把候選罪名、測試結果或 AI 推論當成法律結論或 Human Gate 核准。
8. 完成後執行完整 pytest、前端測試、JavaScript 語法及健康檢查，並以 FACT／INFERENCE／UNKNOWN 回報。

目前已知基線：629 passed、HTTP 200、document_renderer=READY、LOCAL_ONLY、external_ai_enabled=false。
```

