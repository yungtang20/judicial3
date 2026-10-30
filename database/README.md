# 刑事偵查輔助系統 (Criminal Investigation Analysis System) - PostgreSQL 資料庫套件

- **版本**: v2.0-DB
- **任務編號**: DB-P0-1
- **狀態**: 本機檔案就緒 (純靜態交付，未連線資料庫)
- **相容性**: PostgreSQL 15+ / 16+, Supabase / Self-hosted PostgreSQL
- **安全等級**: 司法敏感資料級別 (嚴格 RLS、不可竄改歷史、狀態機約束)

---

## 一、專案概述

本套件為全新、獨立的「刑事偵查輔助系統」所設計的正式 PostgreSQL 資料庫建置與安全架構。
系統宗旨並非建立單一罪名分類器，而是提供一套具備**可追溯性**、**可修正性**、**版本一致性**及**嚴格人工審核控制**的案件法律推理資料庫骨幹。

核心業務流程貫穿：
```
原始案情 (Case) 
  → 歷程版本快照 (Revisions) 
    → 結構化事實 (Facts) & 證據來源 (Evidence) 
      → 行為拆解 (Behaviors) 
        → 法規範 (Statutes) & 裁判 (Precedents) 查證 
          → 候選法律方向 (Legal Candidates) & 構成要件 (Elements) 
            → 核心爭點 (Core Issues) 
              → 筆錄問答 (Interviews) 
                → 事實更新反饋 (Fact Update Logs) 
                  → 人工審核 (Approvals) & 條陳文書產出 (Document Outputs)
```

---

## 二、目錄架構

```
/database
├── README.md                           # 本說明文件
├── ARCHITECTURE.md                     # 系統架構、狀態機、不可竄改設計說明
├── DATA_DICTIONARY.md                  # 24 張資料表完整欄位字典與型別約束
├── SECURITY.md                         # 安全控制、RBAC、RLS 政策與會話權限
├── MIGRATION_PLAN.md                   # 遷移執行計畫、依序套用與復原程序
├── migrations/                         # 循序執行之 PostgreSQL Migration 腳本
│   ├── 0001_extensions_enums.sql       # 擴充套件 (uuid-ossp, pgcrypto) 與 Enum 定義
│   ├── 0002_identity_cases.sql         # 使用者、角色、案件與版本快照主表
│   ├── 0003_facts_evidence.sql         # 事實、證據、來源、關聯與行為表
│   ├── 0004_analysis_legal.sql         # 法規、判決、候選罪名、要件與爭點表
│   ├── 0005_interview_workflow.sql     # 筆錄詢問、問句、回答、更新日誌與流程表
│   ├── 0006_documents_prompts.sql      # 人工審核、條陳文書輸出與提示詞範本表
│   ├── 0007_integrity_indexes_triggers.sql # 雜湊校驗、不可竄改性、無效化觸發器與索引
│   ├── 0008_rls_policies.sql           # 資料列層級安全 (RLS) 與工作階段驗證
│   └── 0009_validation.sql             # 結構完整性驗收函式與健全性檢查
├── tests/                              # 資料庫驗收與負向測試 SQL
│   ├── schema_validation.sql           # 結構與約束存在性檢查
│   ├── constraint_tests.sql            # CHECK / 外鍵 / 唯一約束測試
│   ├── version_integrity_tests.sql     # 版本封存、雜湊比對與不可竄改測試
│   ├── rls_positive_tests.sql          # 授權使用者讀寫存取測試
│   ├── rls_negative_tests.sql          # 跨案件、未授權及越權寫入阻擋測試
│   └── test_data.sql                   # 虛構模擬案件測試資料 (非真實個資)
├── scripts/                            # 自動化稽核腳本
│   └── audit_database_files.py         # 本機無連線靜態語法與完整性稽核程式
└── reports/                            # 建置與稽核報告
    ├── IMPLEMENTATION_REPORT.md        # 完整實作成果報告
    ├── TEST_RESULTS.md                 # 測試驗收矩陣 (實體 DB 標示 NOT_RUN)
    └── OPEN_ISSUES.md                  # 未解決問題與二期工程追蹤清單
```

---

## 三、不可違反的原則 (Database Guardrails)

1. **禁止直接判罪**: 候選罪名必須允許多重方向 (`PRIMARY`, `ALTERNATIVE`, `LOW_CONFIDENCE`, `UNRESOLVED`, `REJECTED`)，不得存在「單一強制結論」約束。
2. **事實狀態明確**: 事實狀態嚴格遵循 `ASSERTED`, `ADMITTED`, `DENIED`, `INFERRED`, `UNKNOWN`，`UNKNOWN` 絕對禁止被資料庫層自動視為否定或已證實。
3. **不可竄改歷程**: `case_revisions` 一旦 `is_locked = TRUE`，資料庫觸發器禁止任何 `UPDATE` 或 `DELETE` 操作，變更必須產生新 Revision。
4. **人工審核閘口**: 條陳文件與正式分析結果若未關聯狀態為 `APPROVED` 的 `review_approvals`，禁止將文件標示為正式完成。
5. **資料隔離與最小權限**: 所有案件子表皆綁定 `(case_id, revision_id)`，RLS 政策保證使用者只能存取自己有權限的案件。

---

## 四、靜態稽核執行方式

本套件提供 Python 3 靜態稽核腳本，無需連線資料庫即可驗證 SQL 檔案完整度：
```bash
python3 database/scripts/audit_database_files.py
```
該腳本會驗證：
- 24 張資料表是否存在且欄位齊全
- Enum 定義覆蓋性
- 外鍵約束與複合約束完整性
- 觸發器與不可竄改規則
- RLS 政策定義與安全設定
- 測試檔案與模擬資料完整性
