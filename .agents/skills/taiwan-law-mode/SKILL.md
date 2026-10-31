---
name: taiwan-law-mode
description: |
  台灣法律案件工作台的路由／總控技能（對應 pstack 的 /poteto-mode）。
  當使用者提到案情分析、Gate 流程、候選路由、證據鏈、筆錄草稿、法條／裁判檢索、
  或要求「用 skills / 本機優先法律推理」時啟動。
  負責選擇 playbook、串接原子技能、強制 MCP 驗證，並確保輸出為人工可審閱草稿。
---

# taiwan-law-mode（總控路由）

遵循根目錄 `AGENTS.md` 與 `skills/AGENTS.md`。

## 啟動後必做

1. 對應 playbook（`skills/playbooks/`）：fact-extraction、law-retrieval、evidence-chain、quality-verification、record-drafting。
2. 需要法源 → 先呼叫 search-taiwan-laws / search-taiwan-judgments（強制 MCP）。
3. 產出前 quality-gate；記錄 MCP verification status（見 `legal-case-web/app/mcp_verification.py`）。
4. 輸出：中性事實、候選 NEED_REVIEW、source_url/JID、證據缺口、建議問句、「輔助草稿，需人工審閱」。

## 禁止

自動定罪、編造法源、略過 MCP、把候選說成已成立／已排除。
