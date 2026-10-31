# Architecture Gap Report（Stage 2）

日期：2026-10-31  
基準 commit：`d44453e`（skills merge）+ `feat/stage2-architecture`

## 已處理（本 branch）

| ID | 項目 | 狀態 |
|----|------|------|
| P0 | 根目錄 `AGENTS.md` + `.agents/skills/` Codex 發現路徑 | 已新增 |
| P0 | `skills/` 保留為 playbook／文件權威來源 | 維持 |
| P0 | `mcp_verification.py` 狀態機與 case log | 已新增 |
| P0 | `RUNTIME_STORAGE_BOUNDARY.md` 對齊 ephemeral／Supabase／SQLite | 已新增 |
| P1 | `competing_hypotheses.py` | 已新增（未強制接入 workflow runtime） |
| P1 | `question_traceability.py` 雙向欄位與 orphan 檢查 | 已擴充 |
| P1 | `judicial-resource-discovery` skill | 已新增 |
| P1 | `tools/check_skill_discovery.py` | 已新增 |

## 尚未完成（明確列出）

| 項目 | 說明 |
|------|------|
| workflow 強制寫入 mcp_verification_log | 需在實際 MCP adapter 呼叫點掛載 |
| competing_hypotheses 接入 Gate 候選 UI | 僅模組＋範例，未改 frontend |
| Gold Dataset 與評估 runner | 僅原則；需人工標註合成案 |
| README 與 TEST_RESULTS 數字統一 | 需本機跑完整 pytest 後再生 |
| server.py 預設 store 自動偵測文件產生器 | 建議後續 |

## 原則重申

系統為筆錄與分析輔助；不得自動認定犯罪成立。Human Gate、revision、外部 AI 預設關閉維持不變。
