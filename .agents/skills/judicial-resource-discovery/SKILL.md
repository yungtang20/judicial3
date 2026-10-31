---
name: judicial-resource-discovery
description: |
  本機資源探索：掃描 Skills、MCP、Python 套件、官方法律網站與相關 GitHub，
  比較既有功能後提出整合計畫。禁止未授權安裝或修改 MCP 設定。
  涉及案件資料不得送外網搜尋。
---

# 司法資源探索 Agent

## 流程（強制）

`發現 → 分析 → 授權檢查 → 安全檢查 → 測試計畫 → 整合提案`

**不得**在未檢查前直接安裝第三方套件或改 MCP。

## 應檢查

1. `.agents/skills/` 與 `skills/` 是否同步、可被發現（執行 `tools/check_skill_discovery.py`）。
2. 已連接 MCP（名稱、schema、是否 fail closed）。
3. `legal-case-web` 既有推理模組，避免重複造輪。
4. 官方來源：全國法規、司法院裁判、法務部函釋等（僅公開資訊）。
5. 授權與個資：案件正文不得外送。

## 輸出

- 發現清單（本機 vs 網路分開）
- 與現況差距
- 建議整合步驟與風險
- **不自動執行**破壞性變更
