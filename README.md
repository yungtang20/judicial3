# 法律案件工作台 (Judicial Case Workbench)

獨立、本機優先的 Gate 1–5 法律案件工作台。核心目標是整理事實、保留多個候選法律路由、產生角色化問句及輸出筆錄。它不是自動定罪系統。

## 專案結構

```
judicial3/
├── legal-case-web/          # 主系統（Python，本機優先）
│   ├── app/                 # 核心模組（server, workflow, rules, questions, documents, ...）
│   ├── tests/               # pytest 測試（800+ 項）
│   ├── data/                # Runtime JSON（題庫、法源快取、路由對照）
│   ├── questions/           # Markdown 題庫
│   ├── docs/                # 架構、設計、審查、證據封包
│   └── tools/               # 輔助工具
├── skills/                  # 本地 AI Agent Skills（台灣法域 + MCP 強制驗證）
│   ├── AGENTS.md            # 硬規則、法域、MCP 清單
│   ├── taiwan-law-mode/     # 總控路由（類 pstack /poteto-mode）
│   ├── atomic/              # 原子技能（法條／裁判檢索、證據鏈、quality gate）
│   └── playbooks/           # Gate 對應流程
├── criminal-investigation-assistant/  # 刑事筆錄輔助系統（獨立 Python 專案）
├── reasoning-flow/          # JS 推理流程原型
├── archive/                 # 已淘汰原型封存
└── docs/                    # 專案層級文件
```

## 本地 AI Skills（taiwan-law-mode）

設計靈感來自 **poteto/pstack**（信任階梯、verification 為地基）與 **Legal-Skills-Chinese**（原子／複合、主張→要件→證據）。

- 目錄：[`skills/`](./skills/)
- 總控：對 agent 說「使用 taiwan-law-mode」或載入 `skills/taiwan-law-mode`
- **硬規則**：不得編造法條／裁判；需要法源時必須呼叫已連接的 **taiwan-law-mcp**；輸出一律為輔助草稿
- 原子技能：`search-taiwan-laws`、`search-taiwan-judgments`、`evidence-argument-chain`、`quality-gate`
- 與 `legal-case-web/app/` 中 `evidence_argument_chain`、`quality_gate`、`forbidden_conclusions`、`citation_contract` 等模組對齊

詳細說明見 [`skills/README.md`](./skills/README.md) 與 [`skills/AGENTS.md`](./skills/AGENTS.md)。

## 快速啟動

### legal-case-web（主系統）

```powershell
cd legal-case-web
py -3 -m pip install -r requirements.txt
.\start.ps1
```

本機服務網址：`http://127.0.0.1:8787/`

健康檢查：`GET /api/health`

### criminal-investigation-assistant

```powershell
cd criminal-investigation-assistant
py -3 -m pip install -r requirements.txt
py -3 -X utf8 tools/compile_questions.py
py -3 -X utf8 -m app.server
```

預設網址：`http://127.0.0.1:8790/`

## 核心流程（Gate 1–5）

1. **輸入案情摘要** — 自由敘述，系統自動拆解人、事、時、地、物、行為、結果、證據
2. **Gate 1 事實抽取** — 抽取中性事實，無證據支持的維持 `UNKNOWN`
3. **系統候選分析** — 確定性規則提出 0–3 個候選；外部 AI 預設關閉
4. **人工一次確認** — 承辦人檢視摘要、理由及缺口後一次確認
5. **必要問句生成** — 依已知摘要、候選方向及回答狀態，受 20 題總題數預算控制
6. **作答與重評估** — 自由文字存為陳述；僅明確 YES/NO/UNKNOWN 觸發重評估
7. **Gate 2 基本資料** — 受詢問人年籍、詢問起訖時間
8. **Gate 2.5 條件欄位** — 證明單、婦幼、165 案號
9. **Gate 3 輸出** — 被害人筆錄與條陳
10. **Gate 4 延伸** — 涉嫌人問答與文件
11. **Gate 5 移送** — 無被害人案件走移送分支

## 安全與隱私

- 外部 AI 預設關閉（`ALLOW_EXTERNAL_AI=false`）
- 單一所有人、固定 UUID、強制 MFA
- 應用程式層加密（AES-256-GCM / Fernet）
- 稽核不落地（不存姓名、案號、自由文字）
- RLS + 後端案件擁有者雙重驗證

## 測試

```powershell
cd legal-case-web
py -3 -X utf8 -m pytest -q
node --check app\static\app.js
```

最新驗證：838 passed, 1 failed（既有 Human Gate hash-stability）

## 部署

- **Render Free + Supabase**：邀請制單一帳號，Docker 部署
- 線上工作台：https://legal-case-workbench.onrender.com
- 健康檢查：https://legal-case-workbench.onrender.com/api/health

## 相關文件

- `legal-case-web/README.md` — 完整說明文件
- `legal-case-web/docs/SYSTEM_ARCHITECTURE.md` — 系統架構與信任邊界
- `legal-case-web/OPEN_ISSUES.md` — 未決問題
- `legal-case-web/TEST_RESULTS.md` — 測試結果
- `skills/README.md` — 本地 AI Skills 使用說明

## 推理模組（Phase 5-6）

| 模組 | 來源 | 用途 |
|------|------|------|
| `app/evidence_argument_chain.py` | Legal-Skills-Chinese | 主張→要件→證據→證明力評估 |
| `app/quality_gate.py` | Legal-Skills-Chinese | 推理前品質閘門 |
| `app/dispute_issue_identifier.py` | Legal-Skills-Chinese | 爭議焦點識別 |
| `app/counterfactual_reasoning.py` | Legal-Skills-Chinese | 反事實因果推理 |
| `app/abductive_reasoning.py` | Legal-Skills-Chinese | 溯因推理（米尔五法） |
| `app/fact_states.py` | 專家策略 | 事實狀態機 |
| `app/forbidden_conclusions.py` | 專家策略 | 禁止結論掃描 |
| `app/candidate_completeness.py` | 專家策略 | 候選完整性檢查 |
| `app/question_traceability.py` | 專家策略 | 問句追溯性檢查 |
| `app/evaluation_metrics.py` | 專家策略 | 評估指標計算器 |
| `app/document_format_validator.py` | 專家策略 | 文件格式驗證 |
| `app/audit_integrity.py` | 專家策略 | 稽核日誌 hash chain |
| `app/confession_checklist.py` | 專家策略 | 自白補強 checklist |
| `app/version_invalidation.py` | 專家策略 | STALE 標記 + 版本鏈 |
| `app/integration_checks.py` | 專家策略 | 統一安全檢查入口 |
| `app/search_variants.py` | judicial-search-tool | 法條搜尋變體生成 |
| `app/synonym_tiers.py` | judicial-search-tool | 4-tier 同義詞管理 |
| `app/anomaly_log.py` | judicial-search-tool | JSONL 診斷記錄 |
| `app/two_stage_scoring.py` | judicial-search-tool | 兩階段 LLM 評分 |
| `app/citation_contract.py` 增強 | judicial-search-tool | Citation tuple match |

## 版本

- 最後更新：2026-10-31
- 維護原則：文件先行、邊界明確、證據可追溯、測試為工程證據而非法律核准
- `feat/taiwan-law-skills`：新增 skills/ 供本地 AI 呼叫 taiwan-law-mcp 與對接 Gate 推理
