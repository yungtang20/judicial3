# 刑事案件筆錄輔助系統

本專案是獨立、本機優先的刑事案件事實整理與筆錄問句工作台。候選罪章永遠是待查證假設，不是法律結論。

## 問句資料庫

- 人工可讀來源：`question_sources/families/*.md` 與 `question_sources/procedure/*.md`
- 權威清單：`question_sources/families.manifest.json`
- 決定性編譯：`py -3 -X utf8 tools/compile_questions.py`
- 漂移檢查：`py -3 -X utf8 tools/compile_questions.py --check`
- Runtime 只讀：`data/runtime/question_bank.json` 與 `data/runtime/source_manifest.json`
- `docs/audit/` 永遠不得被編譯器或 runtime 載入。

每題是一筆正規化記錄，包含角色、家族、route、事實目標、要件類型、層級、必要性、前置／禁止條件、來源、版本、四軸審查狀態、頁面成本及模板位置。

## 本機啟動

```powershell
py -3 -m pip install -r requirements.txt
py -3 -X utf8 tools/compile_questions.py
py -3 -X utf8 -m pytest -q
py -3 -X utf8 -m app.server
```

預設網址：`http://127.0.0.1:8790/`。

## 安全邊界

- 不部署、不呼叫外部 AI、不傳送案件內容。
- `AI_REVIEWED` 不等於 `HUMAN_LEGAL_APPROVED`。
- 未支援 route 必須顯示 `UNSUPPORTED_ROUTE` 或 `HUMAN_REVIEW_REQUIRED`。
- Audit 僅保存命令與 hash，不保存姓名、案號、摘要或回答。
