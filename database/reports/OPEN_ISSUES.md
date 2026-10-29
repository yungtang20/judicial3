# 刑事偵查輔助系統 - 未解決問題與二期工程追蹤 (OPEN_ISSUES.md)

- **任務編號**: DB-P0-1
- **追蹤分類**: 架構審查、相依性與長期維護性議題

---

## 一、未解決問題與限制清單 (Open Issues & Limitations)

### 1. 繁體中文法律全文檢索 (Full-Text Search) 支援
- **現狀**: 目前 `facts`, `precedent_references`, `document_outputs` 支援標準 PostgreSQL B-Tree / GIN 陣列查詢，但針對大篇幅裁判要旨與事實內容尚未掛載中文斷詞（如 `pg_jieba` 或自訂斷詞字典）。
- **影響**: 若資料量擴大至數萬件以上，純文字 `LIKE` 或 `ILIKE` 搜尋效能可能下降。
- **後續建議**: 在第二階段（P1）若環境具備擴充套件編譯能力，引入繁體中文法律斷詞或以 Embedding 向量資料庫（pgvector）輔助。

### 2. 數位證據實體檔案儲存路徑
- **現狀**: `evidence_items` 僅記錄檔案之 SHA-256/MD5 雜湊與 `storage_path`，嚴禁將二進位影音檔案 (`BYTEA`) 直接寫入 PostgreSQL。
- **影響**: 正式部署時需要配合物件儲存服務（如 S3 / Supabase Storage）之 Presigned URL 機制。
- **後續建議**: 定義前端直接上傳至獨立 Storage 的中繼授權規則，資料庫僅保留雜湊校驗與路徑指針。

### 3. 版本快照 SHA-256 雜湊產生責任
- **現狀**: 目前 `case_revisions.revision_hash` 欄位由應用程式後端在提交版本時計算傳入，資料庫提供不可變觸發器保護。
- **影響**: 若後端計算演算法（序列化欄位順序、空格）發生偏差，可能造成數位簽章比對不一致。
- **後續建議**: 評估是否在資料庫層實作標準化的 `jsonb_canonical_hash()` 預存程序，統一由資料庫生成確定性雜湊。

### 4. 單使用者過渡至多單位組織管轄權
- **現狀**: 目前 RLS 以 `lead_investigator_id = current_app_user_id()` 進行案件強隔離。
- **影響**: 當專案擴展至偵查隊、分局與地檢署跨單位聯合偵辦時，需要「案件協辦授權」表 (`case_collaborators`)。
- **後續建議**: 已在架構中保留 `user_roles` 與機密等級欄位，二期可平滑增加 `case_assignments` 表，不影響現有一期結構。

---

## 二、雲端部署注意事項 (若未來啟用 Render / Supabase)

1. **連線池 (Connection Pooling)**:
   由於案件分析涉及長時間閱讀與串流推論，Web API 連線需透過 Transaction-mode PgBouncer 或 Supabase Supavisor，避免過多閒置連線耗盡 PostgreSQL 連線上限。
2. **Session 變數生命週期**:
   自建環境中使用 `SET LOCAL app.current_user_id = '...'` 必須確保在單一交易區塊 (`BEGIN ... COMMIT`) 內生效，防止連線池重複利用時造成身分污染。
