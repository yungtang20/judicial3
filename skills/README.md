# Taiwan Law Agent Skills

本目錄讓**本地 AI**（Cursor、Claude Code、或其他支援 Agent Skills 的環境）以 pstack 風格呼叫台灣法源 MCP，並對接 `legal-case-web` 的 Gate 與推理模組。

## 快速使用

1. 確認已連接 **taiwan-law-mcp**（Grok／Cursor 等環境）。
2. 對 agent 說：`使用 taiwan-law-mode` 或 `@skills/taiwan-law-mode`，再描述案情或任務。
3. Agent 應自動：選 playbook → 呼叫原子 skill → **真實呼叫 MCP** → quality-gate → 輸出草稿。

## 目錄

```
skills/
├── AGENTS.md                 # 法域、硬規則、MCP 清單、優先序
├── README.md                 # 本說明
├── taiwan-law-mode/          # 總控路由（類 /poteto-mode）
│   └── SKILL.md
├── atomic/
│   ├── search-taiwan-laws/
│   ├── search-taiwan-judgments/
│   ├── evidence-argument-chain/
│   └── quality-gate/
└── playbooks/
    ├── fact-extraction.md
    ├── law-retrieval.md
    ├── evidence-chain.md
    ├── quality-verification.md
    └── record-drafting.md
```

## 設計來源

- **pstack / poteto**：信任階梯、verification 優先、skills 編碼專業流程、避免 meat proxy。
- **Legal-Skills-Chinese**：原子／複合、證據論證鏈、品質閘門（已部分實作於 `legal-case-web/app/`）。
- **專案既有**：Gate 1–5、外部 AI 預設關閉、citation 與 forbidden_conclusions。

## 注意

- Skills 是**提示與流程契約**，真正法源以 MCP 回傳為準。
- 正式筆錄請仍走 `legal-case-web` 文件產製與人工 Gate。
- 歡迎依實務新增原子 skill（例如自白補強 checklist、婦幼程序檢查）。
