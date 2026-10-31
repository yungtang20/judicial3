# 法律案件工作台 (Judicial Case Workbench)

獨立、本機優先的 Gate 1–5 法律案件工作台。核心目標是整理事實、保留多個候選法律路由、產生角色化問句及輸出筆錄。它不是自動定罪系統。

## 專案結構

```
judicial3/
├── legal-case-web/          # 主系統（Python，本機優先）
│   ├── app/                 # 核心模組（server, workflow, rules, questions, documents, ...）
│   │   ├── mcp_client.py    # 本地/遠端 MCP 客戶端（stdlib JSON-RPC，失敗即閉鎖）
│   │   ├── legal_source_verification.py  # 候選法條與 MCP 交叉驗證
│   │   ├── agent_loop.py    # 代理驗證迴路（觀察→驗證→決定→沉澱）
│   │   ├── integration_checks.py         # 統一安全檢查入口（現有 + 推理輔助）
│   │   └── ...              # workflow, server, ai, quality_gate, ... 等核心模組
│   ├── tests/               # pytest 測試（約 1000 項）
│   ├── tools/               # 輔助工具（mcp_health_check, check_skill_discovery, ...）
│   ├── data/                # Runtime JSON（題庫、法源快取、路由對照）
│   ├── questions/           # Markdown 題庫
│   ├── docs/                # 架構、設計、審查、證據封包
│   └── ...
├── skills/                  # 本地 AI Agent Skills（台灣法域 + MCP 強制驗證）
│   ├── AGENTS.md            # 硬規則、法域、MCP 清單（本地 + 遠端來源）
│   ├── taiwan-law-mode/     # 總控路由（類 pstack /poteto-mode）
│   ├── atomic/              # 原子技能（法條／裁判檢索、證據鏈、quality gate）
│   ├── playbooks/           # Gate 對應流程
│   ├── verify-and-sediment/ # 驗證迴路技能
│   └── judicial-resource-discovery/  # 本機資源探索
├── criminal-investigation-assistant/  # 刑事筆錄輔助系統（獨立 Python 專案）
├── reasoning-flow/          # JS 推理流程原型
├── archive/                 # 已淘汰原型封存
├── docs/                    # 專案層級文件
└── tools/                   # 根目錄輔助腳本
```

## 設計靈感（訪談應用）

本專案參考 poteto/pstack 與 Legal-Skills-Chinese 的核心理念，並落實到程式碼：

- **Verification 為地基**：所有法條／裁判引用必須經 MCP 交叉驗證，失敗即回報 `MCP_UNAVAILABLE` / `NOT_FOUND`，決不以模型記憶補法條（`TaiwanLawMcpAdapter` 預設失敗閉鎖）。
- **決定性部分下放為腳本**：MCP 串流與法條驗證以純 Python 客戶端處理（`app/mcp_client.py`），agent 只負責決定「呼叫哪個工具、傳入哪些參數」。
- **推理輔助與品質閘門**：`run_pre_analysis_checks` 現在會串接 `quality_gate`、`dispute_issue_identifier` 與 `abductive_reasoning`（主張→要件→證據→證明力），產出 WARN 級別的審查訊號，供人工 Gate 決策使用，不會自動阻斷案件流程。
- **觀察→驗證→決定→沉澱**：`agent_loop.py` 與 `verify-and-sediment` 技能定義任務收尾迴路，反覆錯誤只「提案」寫入 skill/test，須人工核准，禁止自動合併。

## 本地 AI 與 MCP / 網頁呼叫

本專案讓本地 AI（Cursor / Claude Code / 其他支援 skills 的本地 AI）能夠呼叫本地相關的 skill、MCP 與官方網頁：

- **本地 MCP**（`mcp-taiwan-legal-db`，stdio JSON-RPC，透過 `JUDICIAL3_MCP_LOCAL` 啟用）：`search_judgments`、`get_judgment`、`query_regulation`、`get_pcode`、`search_regulations`、`get_interpretation`、`search_interpretations`、`get_citations`。
- **遠端 MCP**（`legaltech.org.tw/mcp`，HTTP JSON-RPC，透過 `JUDICIAL3_MCP_REMOTE` 啟用）：`search_taiwan_laws`、`search_taiwan_judgments`、`get_taiwan_judgment`、`search_taiwan_interpretations`、`get_taiwan_interpretation`、`search_moj_interpretations`、`search_taiwan_regulations`、`get_taiwan_pcode`、`get_taiwan_law_versions`、`analyze_legal_intent`、`search_taiwan_bills` 等。
- **官方網頁**：全國法規資料庫、司法院裁判、法務部行政函釋、立法院議案（僅公開資訊，案件正文不外送）。

呼叫後必須依據回傳內容引用，並保留 `source_url` / JID；不可用時回報 `MCP_UNAVAILABLE` / `NOT_FOUND`，**fail closed**，不得以模型記憶補法條。

詳細說明見 [`skills/AGENTS.md`](./skills/AGENTS.md) 與 [`skills/README.md`](./skills/README.md)。

## 快速啟動

### legal-case-web（主系統）

```powershell
cd legal-case-web
py -3 -m pip install -r requirements.txt
.\start.ps1
```

本機服務網址：`http://127.0.0.1:8787/`

健康檢查：`GET /api/health`

### 啟用本地 MCP（選擇性）

```powershell
$env:JUDICIAL3_MCP_LOCAL="<mcp-taiwan-legal-db 目錄路徑>"
.\start.ps1
```

啟用後，分析端點會嘗試以本地 MCP 交叉驗證候選法條；未設定時回報 `MCP_UNAVAILABLE`，流程不受影響。

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
3. **系統候選分析** — 確定性規則提出 0–3 個候選；外部 AI 預設關閉；法條來源隨案附上 MCP 驗證紀錄
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
- 案件正文不送外網；MCP 查詢僅使用已歸納的法條／案號關鍵字，不發送原始案情

## 測試

```powershell
cd legal-case-web
py -3 -X utf8 -m pytest -q
node --check app\static\app.js
```

技能探索檢查：

```powershell
py -3 ..\tools\check_skill_discovery.py
```

本地 MCP 健康檢查（需先設 `JUDICIAL3_MCP_LOCAL`）：

```powershell
py -3 tools\mcp_health_check.py
```

最新驗證：約 972 passed / 5 failed（5 項為既知基線失敗，與本次變更無關；約 838 passed, 1 failed 為舊基準）。

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

## 推理模組（Legal-Skills-Chinese 概念應用）

| 模組 | 來源 | 用途 | 納入狀態 |
|------|------|------|----------|
| `app/evidence_argument_chain.py` | Legal-Skills-Chinese | 主張→要件→證據→證明力評估 | 已埠留，供技能層參照 |
| `app/quality_gate.py` | Legal-Skills-Chinese | 推理前品質閘門 | 已納入 `run_pre_analysis_checks` |
| `app/dispute_issue_identifier.py` | Legal-Skills-Chinese | 爭議焦點識別 | 已納入 `run_pre_analysis_checks` |
| `app/counterfactual_reasoning.py` | Legal-Skills-Chinese | 反事實因果推理 | 已埠留，供技能層參照 |
| `app/abductive_reasoning.py` | Legal-Skills-Chinese | 溯因推理（米尔五法） | 已納入 `run_pre_analysis_checks`（未知事實假說） |
| `app/integration_checks.py` | 專家策略 | 統一安全檢查入口 | 現有安全閘門 + 推理輔助訊號 |

## 版本

- 最後更新：2026-10-31
- 維護原則：文件先行、邊界明確、證據可追溯、測試為工程證據而非法律核准
- `feat/local-mcp-integration`：接通本地/遠端 MCP 與失敗閉鎖驗證、將 Legal-Skills-Chinese 推理模組納入預分析檢查、同步 `.agents/skills` 與 `skills/`、修正 `mcp_health_check.py` 工具數判斷。
