# TEST_RESULTS

## 執行結果

| 測試 | 結果 | 證據 |
|---|---|---|
| 既有 pytest suite | PASS | `95 passed` |
| 超商拾得手機基準案例 | PASS | theft 與 embezzlement 均保留，候選角色為 `UNRESOLVED` |
| 測試 A：甲仍能立即支配 | PASS | theft 排序第一，仍保留 `UNLAWFUL_OWNERSHIP_INTENT` 未決 |
| 測試 B：手機已脫離持有 | PASS | embezzlement 排序第一，仍保留不法所有意圖未決 |
| 測試 C：立即交給店員 | PASS | 產生降低不法所有意圖的相反線索，未自動排除候選 |
| 測試 D：矛盾回答 | PASS | 保留原始回答，於獨立 `contradiction_issues` 建立 `ROLE_CONTRADICTION:acquisition_method` |
| `tools/legal_reasoning_audit.py` | PASS | 五項 assertion 全部 PASS；`external_network_used=false` |
| 題庫漂移檢查 | PASS | `tools/compile_questions.py --check` |
| JavaScript syntax | PASS | `node --check app/static/app.js` |
| Python compile | PASS | `py -3 -X utf8 -m compileall -q app tools` |
| Diff whitespace | PASS | `git diff --check` |

## 測試解讀

PASS 只代表結構化規則、狀態轉換及反事實測試符合本次明確 assertion；不代表刑事法律結論已獲人工核准，也不代表所有 route 均已完成法律審查。

## 直接執行

```powershell
cd D:\工作用\judicial1\criminal-investigation-assistant
py -3 -X utf8 tools/legal_reasoning_audit.py
py -3 -X utf8 -m pytest -q
```
