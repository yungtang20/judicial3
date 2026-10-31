# Repository Agent Rules（司法案件工作台）

本檔為 **repository 根目錄** Agent 規則，供 Codex / Cursor / Claude Code 等自動載入。
詳細台灣法域硬規則、MCP 清單與技能選擇見：

- `skills/AGENTS.md`（權威法域與硬規則）
- `.agents/skills/*/SKILL.md`（Codex 可發現技能；內容與 `skills/` 對齊，以 `skills/` 為文件來源）

## 專案定位（不可偏離）

- 本機優先的 **Gate 1–5 案件分析與筆錄輔助**工具。
- **不是**自動定罪系統；候選僅供人工審閱（NEED_REVIEW）。
- 外部 AI 預設關閉；需要法源時必須實際呼叫 **taiwan-law-mcp**，不得用模型記憶冒充法條／裁判。
- 輸出一律標「輔助草稿，需人工審閱」。

## Skills 載入

1. 優先使用 `.agents/skills/` 下各 `SKILL.md`（Codex 自動發現路徑）。
2. Playbook 與長文說明在 `skills/playbooks/` 與 `skills/README.md`。
3. 修改技能時：**先改 `skills/` 權威副本**，再同步 `.agents/skills/`，避免長期分歧。

## Runtime 安全邊界（摘要）

詳見 `docs/RUNTIME_STORAGE_BOUNDARY.md`：

- **本機預設**：`EphemeralCaseStore`（程序記憶體，重啟即失）。
- **Render + Supabase**：`SupabaseCaseStore`（加密 payload + RLS + 單一 owner）；依部署設定啟用。
- **SQLite `CaseStore`**：相容模組，未必為目前 HTTP runtime 預設。
- 文件不得暗示「已全面持久化」若實際仍為 ephemeral。

## 修改原則

- 不刪除既有 Human Gate、revision fail-closed、個資保護。
- 測試通過 = 工程證據，**不是**法律正確性證明。
- 新功能先獨立 branch + Draft PR，不直接改 main。
