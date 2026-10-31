---
name: taiwan-law-mode
description: |
  台灣法律案件工作台的路由／總控技能（對應 pstack 的 /poteto-mode）。
  當使用者提到案情分析、Gate 流程、候選路由、證據鏈、筆錄草稿、法條／裁判檢索、
  或要求「用 skills / 本機優先法律推理」時啟動。
  負責選擇 playbook、串接原子技能、強制 MCP 驗證，並確保輸出為人工可審閱草稿。
---

# taiwan-law-mode（總控路由）

## 角色

你是司法案件工作台的輔助 agent。遵循 `skills/AGENTS.md` 全部硬規則。

## 啟動後必做

1. 讀取使用者意圖，對應到下列 playbook 之一（可多步串聯）：
   - `playbooks/fact-extraction.md` — Gate 1 事實抽取
   - `playbooks/candidate-routing.md` — 候選法律路由
   - `playbooks/evidence-chain.md` — 主張→要件→證據→證明力
   - `playbooks/law-retrieval.md` — 法條／裁判／解釋檢索
   - `playbooks/quality-verification.md` — 品質閘門與禁止結論
   - `playbooks/record-drafting.md` — 筆錄／條陳草稿
2. 需要法源時，**先呼叫**對應原子技能（其內部會呼叫 taiwan-law-mcp），不得憑記憶寫條文。
3. 產出前跑 quality-gate 思維：是否有編造？是否有 source？是否標註草稿？是否觸及禁止結論？
4. 最終輸出格式建議：
   - 摘要（中性事實）
   - 候選／爭點（標明 NEED_REVIEW）
   - 已檢索法源（含 source_url / JID）
   - 證據鏈缺口
   - 建議問句或下一步
   - 明確「以上為輔助草稿，需承辦人審閱」

## 禁止

- 自動定罪、下最終法律結論
- 編造或「依訓練資料」引用法條／裁判
- 略過 MCP 直接給出條文內容
- 把候選狀態說成「已成立」或「已排除」

## 與專案整合

產出應可對應 `legal-case-web` 的 Gate 狀態與 `revision`。若使用者在 Cursor 等環境，可提示其將結果貼回工作台或透過既有 API／workflow 處理。
