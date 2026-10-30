# 刑事偵查輔助系統 - 資料庫欄位字典 (DATA_DICTIONARY.md)

- **版本**: v2.0-DB
- **資料表總數**: 24 表
- **字元編碼**: UTF-8
- **主鍵規範**: 所有實體表均採用 UUID v4 作為主鍵 (`gen_random_uuid()` 或 `uuid_generate_v4()`)

---

## 模組一：身分鑑別、授權與案件主檔 (Tables 1 - 5)

### 1. `users` (使用者帳號表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 使用者唯一識別碼 |
| `username` | `VARCHAR(64)` | NOT NULL, UNIQUE | 帳號名稱 |
| `email` | `VARCHAR(255)` | NOT NULL, UNIQUE | 電子郵件信箱 |
| `password_hash` | `TEXT` | NOT NULL | 密碼雜湊值 (Argon2id/bcrypt) |
| `full_name` | `VARCHAR(100)` | NOT NULL | 人員真實姓名 |
| `badge_number` | `VARCHAR(50)` | UNIQUE | 執法人員證號/警員編號 |
| `organization` | `VARCHAR(128)` | NOT NULL DEFAULT '偵查專案組' | 所屬單位/機關 |
| `role_id` | `UUID` | NOT NULL, FK -> `user_roles(id)` | 預設系統角色 |
| `is_active` | `BOOLEAN` | NOT NULL DEFAULT TRUE | 帳號啟用狀態 |
| `security_stamp` | `VARCHAR(64)` | NOT NULL DEFAULT `gen_random_uuid()::text` | 安全戳記 (權限變更自動失效 session) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 建立時間 |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 最後更新時間 |

### 2. `user_roles` (角色與權限定義表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 角色唯一識別碼 |
| `role_code` | `VARCHAR(32)` | NOT NULL, UNIQUE | 角色識別代碼 (`LEAD_INVESTIGATOR`, `REVIEWER`, `ANALYST`) |
| `role_name` | `VARCHAR(64)` | NOT NULL | 角色顯示名稱 |
| `permissions` | `JSONB` | NOT NULL DEFAULT '[]'::jsonb | 細部權限代碼清單陣列 |
| `description` | `TEXT` | NULL | 角色權限說明 |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 建立時間 |

### 3. `user_sessions` (連線階段與安全稽核表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 連線 Session 識別碼 |
| `user_id` | `UUID` | NOT NULL, FK -> `users(id)` ON DELETE CASCADE | 關聯使用者 |
| `session_token_hash`| `VARCHAR(64)` | NOT NULL, UNIQUE | 權杖雜湊值 (SHA-256) |
| `ip_address` | `INET` | NULL | 登入來源 IP |
| `user_agent` | `TEXT` | NULL | 用戶端環境資訊 |
| `expires_at` | `TIMESTAMPTZ` | NOT NULL | 憑證過期時間 |
| `is_revoked` | `BOOLEAN` | NOT NULL DEFAULT FALSE | 是否已主動撤銷 |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 登入時間 |

### 4. `cases` (案件基本檔主表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 案件唯一識別碼 |
| `case_number` | `VARCHAR(64)` | NOT NULL, UNIQUE | 案件管制編號 (例如：115偵字第0001號) |
| `title` | `VARCHAR(255)` | NOT NULL | 案件名稱/專案名稱 |
| `lead_investigator_id`| `UUID` | NOT NULL, FK -> `users(id)` | 主辦承辦人員 |
| `current_revision_id`| `UUID` | NULL, FK -> `case_revisions(id)` (DEFERRABLE) | 目前生效中之最新版本指針 |
| `classification_level`| `classification_level_enum` | NOT NULL DEFAULT 'CONFIDENTIAL' | 機密等級 (`PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `SECRET`) |
| `is_archived` | `BOOLEAN` | NOT NULL DEFAULT FALSE | 是否已結案封存 |
| `archived_at` | `TIMESTAMPTZ` | NULL | 結案歸檔時間 |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 建立時間 |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 更新時間 |

### 5. `case_revisions` (案件歷史版本快照主表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 版本唯一識別碼 |
| `case_id` | `UUID` | NOT NULL, FK -> `cases(id)` ON DELETE RESTRICT | 所屬案件識別碼 |
| `revision_number` | `INTEGER` | NOT NULL, CHECK (`revision_number` >= 1) | 版本序號 (1, 2, 3...) |
| `parent_revision_id`| `UUID` | NULL, FK -> `case_revisions(id)` | 父版本識別碼 |
| `revision_hash` | `VARCHAR(64)` | NOT NULL | 版本關鍵內容 SHA-256 數位簽章 |
| `change_summary` | `TEXT` | NOT NULL | 本版變更事由摘要 |
| `is_locked` | `BOOLEAN` | NOT NULL DEFAULT FALSE | 是否已封存鎖定 (鎖定後禁止異動) |
| `locked_at` | `TIMESTAMPTZ` | NULL | 鎖定時間戳記 |
| `created_by` | `UUID` | NOT NULL, FK -> `users(id)` | 建立版本人員 |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 建立時間 |
| **約束** | `UNIQUE(case_id, revision_number)` | 防止版本號重疊 |
| **約束** | `UNIQUE(case_id, id)` | 供下游子表建立複合外鍵 |

---

## 模組二：事實、證據、來源與行為拆解 (Tables 6 - 10)

### 6. `facts` (結構化事實表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 事實識別碼 |
| `case_id` | `UUID` | NOT NULL | 案件識別碼 |
| `revision_id` | `UUID` | NOT NULL | 版本快照識別碼 |
| `fact_seq` | `INTEGER` | NOT NULL | 事實編號 (F-001...) |
| `description` | `TEXT` | NOT NULL | 客觀事實內容陳述 |
| `fact_type` | `VARCHAR(32)` | NOT NULL DEFAULT 'OBJECTIVE' | 事實性質 (`OBJECTIVE`, `STATEMENT`, `TIMELINE`, `STATE_OF_MIND`) |
| `status` | `fact_status_enum` | NOT NULL | 狀態 (`ASSERTED`, `ADMITTED`, `DENIED`, `INFERRED`, `UNKNOWN`) |
| `confidence_score` | `NUMERIC(4,3)` | NOT NULL DEFAULT 1.000, CHECK (0.000 ~ 1.000) | 可信度評分 (0.000 至 1.000) |
| `occurred_at` | `TIMESTAMPTZ` | NULL | 事實發生具體時點 (若已知) |
| `is_disputed` | `BOOLEAN` | NOT NULL DEFAULT FALSE | 是否有當事人或證人間之爭議 |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 建立時間 |
| **外鍵** | `FOREIGN KEY (case_id, revision_id) REFERENCES case_revisions(case_id, id)` |

### 7. `fact_relations` (事實因果推論與關聯圖表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 關聯識別碼 |
| `case_id` | `UUID` | NOT NULL | 案件識別碼 |
| `revision_id` | `UUID` | NOT NULL | 版本識別碼 |
| `source_fact_id` | `UUID` | NOT NULL, FK -> `facts(id)` | 前置事實識別碼 |
| `target_fact_id` | `UUID` | NOT NULL, FK -> `facts(id)` | 後置事實識別碼 |
| `relation_type` | `VARCHAR(32)` | NOT NULL | 關聯性 (`CAUSES`, `CORROBORATES`, `CONTRADICTS`, `INFERRED_FROM`) |
| `rationale` | `TEXT` | NOT NULL | 推論或關聯之論據說明 |
| **外鍵** | `FOREIGN KEY (case_id, revision_id) REFERENCES case_revisions(case_id, id)` |
| **約束** | `CHECK (source_fact_id <> target_fact_id)` | 禁止自我循環 |

### 8. `evidence_items` (證據品項與扣押鏈主表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 證據識別碼 |
| `case_id` | `UUID` | NOT NULL | 案件識別碼 |
| `revision_id` | `UUID` | NOT NULL | 版本識別碼 |
| `item_code` | `VARCHAR(64)` | NOT NULL | 證物編號 (E-001) |
| `name` | `VARCHAR(255)` | NOT NULL | 證物名稱 (如：交易匯款水單、通訊軟體對話紀錄) |
| `category` | `VARCHAR(64)` | NOT NULL | 類別 (`DIGITAL`, `DOCUMENTARY`, `PHYSICAL`, `TESTIMONIAL`) |
| `custody_chain_summary`| `TEXT` | NULL | 扣押、調取與保管鏈摘要 |
| `hash_md5_sha256` | `VARCHAR(128)`| NULL | 數位證據驗證雜湊值 |
| `storage_path` | `TEXT` | NULL | 實體儲位或雲端路徑 (內部安全儲存) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 建立時間 |
| **外鍵** | `FOREIGN KEY (case_id, revision_id) REFERENCES case_revisions(case_id, id)` |

### 9. `evidence_sources` (證據來源核實表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 來源識別碼 |
| `case_id` | `UUID` | NOT NULL | 案件識別碼 |
| `revision_id` | `UUID` | NOT NULL | 版本識別碼 |
| `evidence_item_id` | `UUID` | NOT NULL, FK -> `evidence_items(id)` | 關聯證物識別碼 |
| `provider_name` | `VARCHAR(128)` | NOT NULL | 提供單位或人員 (如：玉山銀行股份有限公司、告訴人林○○) |
| `provider_type` | `VARCHAR(64)` | NOT NULL | 來源類別 (`FINANCIAL_INSTITUTION`, `TELECOM`, `WITNESS`, `SUSPECT`, `VICTIM`) |
| `status` | `source_status_enum` | NOT NULL DEFAULT 'UNVERIFIED' | 核實狀態 (`VERIFIED`, `UNVERIFIED`, `UNAVAILABLE`, `VERSION_UNCERTAIN`) |
| `verified_by` | `UUID` | NULL, FK -> `users(id)` | 核實確認人員 |
| `verified_at` | `TIMESTAMPTZ` | NULL | 核實時間 |
| **外鍵** | `FOREIGN KEY (case_id, revision_id) REFERENCES case_revisions(case_id, id)` |

### 10. `behaviors` (行為人具體行為拆解表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 行為識別碼 |
| `case_id` | `UUID` | NOT NULL | 案件識別碼 |
| `revision_id` | `UUID` | NOT NULL | 版本識別碼 |
| `actor_name` | `VARCHAR(100)` | NOT NULL | 行為人姓名或角色 (如：不詳男子、帳戶名義人) |
| `action_description`| `TEXT` | NOT NULL | 客觀具體行為 (如：傳送虛假平台網址、提供個人金融帳戶供他人使用) |
| `means_method` | `TEXT` | NULL | 手段與方法 (如：透過通訊軟體密集話術誘導、面交收取提款卡) |
| `time_context` | `VARCHAR(255)` | NULL | 發生時空脈絡說明 |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 建立時間 |
| **外鍵** | `FOREIGN KEY (case_id, revision_id) REFERENCES case_revisions(case_id, id)` |

---

## 模組三：法律查證、構成要件與候選罪名 (Tables 11 - 16)

### 11. `statute_references` (法定規範基準庫)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 法規條文識別碼 |
| `law_name` | `VARCHAR(128)` | NOT NULL | 法規名稱 (如：中華民國刑法、洗錢防制法) |
| `article_number` | `VARCHAR(32)` | NOT NULL | 條次 (如：339-4, 14) |
| `paragraph` | `INTEGER` | NOT NULL DEFAULT 1 | 項次 |
| `subparagraph` | `VARCHAR(32)` | NULL | 款/目次 (如：第1項第2款、第3款) |
| `content` | `TEXT` | NOT NULL | 法條全文內容 |
| `effective_date` | `DATE` | NOT NULL | 生效日期 (供新舊法比較) |
| `expiry_date` | `DATE` | NULL | 廢止/修正日期 |
| `is_current` | `BOOLEAN` | NOT NULL DEFAULT TRUE | 是否為現行有效法規 |
| **約束** | `UNIQUE(law_name, article_number, paragraph, subparagraph, effective_date)` |

### 12. `precedent_references` (裁判例與實務見解庫)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 裁判見解識別碼 |
| `court_level` | `VARCHAR(64)` | NOT NULL | 法院層級 (最高法院、高等法院) |
| `case_identifier` | `VARCHAR(128)` | NOT NULL | 裁判字號 (如：最高法院108年度台上大字第3101號裁定) |
| `verdict_date` | `DATE` | NOT NULL | 裁判裁判日期 |
| `holding_summary` | `TEXT` | NOT NULL | 裁判要旨/法律座談會決議內容 |
| `topic_tags` | `TEXT[]` | NOT NULL DEFAULT '{}' | 主題標籤 (`["加重詐欺", "人頭帳戶", "不確定故意", "競合"]`) |
| `verified_in_law_bank`| `BOOLEAN` | NOT NULL DEFAULT TRUE | 是否已在司法院裁判書系統驗證存在 |

### 13. `legal_candidates` (候選法律方向/罪名表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 候選法律方向識別碼 |
| `case_id` | `UUID` | NOT NULL | 案件識別碼 |
| `revision_id` | `UUID` | NOT NULL | 版本識別碼 |
| `statute_id` | `UUID` | NOT NULL, FK -> `statute_references(id)` | 參照法規條文 |
| `charge_name` | `VARCHAR(128)` | NOT NULL | 罪名標題 (如：刑法第339條之4加重詐欺罪、洗錢防制法第14條洗錢罪) |
| `status` | `candidate_status_enum` | NOT NULL | 候選狀態 (`PRIMARY`, `ALTERNATIVE`, `LOW_CONFIDENCE`, `UNRESOLVED`, `REJECTED`) |
| `rationale` | `TEXT` | NOT NULL | 納入或排除候選方向之分析說明 |
| `competition_type` | `VARCHAR(64)` | NULL | 競合關係備註 (`IMAGINARY_CONCURRENCE` 想像競合、法條競合等) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 建立時間 |
| **外鍵** | `FOREIGN KEY (case_id, revision_id) REFERENCES case_revisions(case_id, id)` |

### 14. `constituent_elements` (罪名構成要件拆解表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 要件識別碼 |
| `case_id` | `UUID` | NOT NULL | 案件識別碼 |
| `revision_id` | `UUID` | NOT NULL | 版本識別碼 |
| `candidate_id` | `UUID` | NOT NULL, FK -> `legal_candidates(id)` ON DELETE CASCADE | 所屬候選罪名 |
| `element_type` | `VARCHAR(32)` | NOT NULL | 要件類型 (`OBJECTIVE_ACT`, `OBJECTIVE_RESULT`, `CAUSALITY`, `SUBJECTIVE_INTENT`, `ILLEGAL_PURPOSE`) |
| `element_name` | `VARCHAR(128)` | NOT NULL | 要件簡稱 (如：施用詐術、三人以上共犯、意圖為自己不法所有) |
| `description` | `TEXT` | NOT NULL | 該要件之法律定義與涵攝說明 |
| `status` | `element_status_enum` | NOT NULL DEFAULT 'UNRESOLVED' | 支持狀態 (`SUPPORTED`, `CONTRADICTED`, `UNRESOLVED`, `NOT_APPLICABLE`) |
| **外鍵** | `FOREIGN KEY (case_id, revision_id) REFERENCES case_revisions(case_id, id)` |

### 15. `element_fact_mappings` (構成要件與事實證據映射表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 映射識別碼 |
| `element_id` | `UUID` | NOT NULL, FK -> `constituent_elements(id)` ON DELETE CASCADE | 關聯構成要件 |
| `fact_id` | `UUID` | NOT NULL, FK -> `facts(id)` | 關聯事實 |
| `support_type` | `VARCHAR(32)` | NOT NULL | 影響性質 (`SUPPORTS`, `REFUTES`, `NEUTRAL`) |
| `weight` | `NUMERIC(3,2)` | NOT NULL DEFAULT 1.00, CHECK (0.00 ~ 1.00) | 證明力權重 |
| `analysis_note` | `TEXT` | NULL | 涵攝理由補充筆記 |
| **約束** | `UNIQUE(element_id, fact_id)` | 防止重複映射 |

### 16. `core_issues` (核心爭點與待證事項表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 爭點識別碼 |
| `case_id` | `UUID` | NOT NULL | 案件識別碼 |
| `revision_id` | `UUID` | NOT NULL | 版本識別碼 |
| `candidate_id` | `UUID` | NULL, FK -> `legal_candidates(id)` | 關聯罪名 |
| `issue_category` | `VARCHAR(32)` | NOT NULL | 爭點分類 (`FACTUAL_DISPUTE`, `LEGAL_INTERPRETATION`, `EVIDENTIARY_SUFFICIENCY`) |
| `title` | `VARCHAR(255)` | NOT NULL | 爭點標題 (如：人頭帳戶名義人是否具備洗錢之不確定故意) |
| `inquiry_target` | `TEXT` | NOT NULL | 待查明之具體事實與詢問目標 |
| `is_resolved` | `BOOLEAN` | NOT NULL DEFAULT FALSE | 爭點是否已釐清 |
| `resolution_summary`| `TEXT` | NULL | 爭點結論整理 |
| **外鍵** | `FOREIGN KEY (case_id, revision_id) REFERENCES case_revisions(case_id, id)` |

---

## 模組四：筆錄問答、事實更新與案件歷程 (Tables 17 - 20)

### 17. `interview_sessions` (筆錄詢問會話主表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 會話識別碼 |
| `case_id` | `UUID` | NOT NULL | 案件識別碼 |
| `revision_id` | `UUID` | NOT NULL | 版本識別碼 |
| `interviewee_name` | `VARCHAR(100)` | NOT NULL | 受詢人姓名 |
| `interviewee_role` | `VARCHAR(32)` | NOT NULL | 受詢人身分 (`SUSPECT`, `VICTIM`, `WITNESS`, `EXPERT`) |
| `interviewer_id` | `UUID` | NOT NULL, FK -> `users(id)` | 詢問官/調查官 |
| `started_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 開始時間 |
| `ended_at` | `TIMESTAMPTZ` | NULL | 結束時間 |
| `rights_notified` | `BOOLEAN` | NOT NULL DEFAULT FALSE | 是否已依刑訴第95條宣告權利 (程序保障) |
| `status` | `VARCHAR(32)` | NOT NULL DEFAULT 'PLANNED' | 狀態 (`PLANNED`, `IN_PROGRESS`, `CONCLUDED`, `CANCELLED`) |
| **外鍵** | `FOREIGN KEY (case_id, revision_id) REFERENCES case_revisions(case_id, id)` |

### 18. `interview_questions` (筆錄擬定問句表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 問句識別碼 |
| `case_id` | `UUID` | NOT NULL | 案件識別碼 |
| `revision_id` | `UUID` | NOT NULL | 版本識別碼 |
| `session_id` | `UUID` | NULL, FK -> `interview_sessions(id)` | 關聯會話 (可為範本問句) |
| `question_seq` | `INTEGER` | NOT NULL | 問句次序編號 |
| `question_text` | `TEXT` | NOT NULL | 筆錄問句文字 |
| `target_element_id`| `UUID` | NULL, FK -> `constituent_elements(id)` | 鎖定之構成要件 |
| `target_issue_id` | `UUID` | NULL, FK -> `core_issues(id)` | 鎖定之爭點 |
| `is_mandatory` | `BOOLEAN` | NOT NULL DEFAULT TRUE | 是否為關鍵核心必問問題 |
| **外鍵** | `FOREIGN KEY (case_id, revision_id) REFERENCES case_revisions(case_id, id)` |

### 19. `interview_answers` (筆錄受詢回答紀錄表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 回答紀錄識別碼 |
| `question_id` | `UUID` | NOT NULL, FK -> `interview_questions(id)` | 關聯問題 |
| `answer_text` | `TEXT` | NOT NULL | 受詢人具體陳述回答文字 |
| `recorded_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 紀錄時間 |
| `eval_fact_status`| `fact_status_enum` | NOT NULL | 本次回答之法律性質 (`ADMITTED`, `DENIED`, `ASSERTED`) |
| `notes` | `TEXT` | NULL | 詢問官觀察或態度備註 |

### 20. `fact_update_logs` (事實修正與反饋歷程表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 更新日誌識別碼 |
| `case_id` | `UUID` | NOT NULL | 案件識別碼 |
| `fact_id` | `UUID` | NOT NULL, FK -> `facts(id)` | 受異動之事實識別碼 |
| `trigger_source` | `VARCHAR(32)` | NOT NULL | 誘發異動之來源 (`INTERVIEW_ANSWER`, `NEW_EVIDENCE`, `MANUAL_EDIT`) |
| `trigger_reference_id`| `UUID` | NULL | 誘發關聯記錄識別碼 (如 answer_id) |
| `previous_status` | `fact_status_enum` | NOT NULL | 異動前狀態 |
| `new_status` | `fact_status_enum` | NOT NULL | 異動後狀態 |
| `previous_description`| `TEXT` | NOT NULL | 異動前描述 |
| `new_description` | `TEXT` | NOT NULL | 異動後描述 |
| `changed_by` | `UUID` | NOT NULL, FK -> `users(id)` | 變更承辦人 |
| `changed_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 異動時間戳記 |

---

## 模組五：流程狀態機、人工核定、條陳產出與提示詞 (Tables 21 - 24)

### 21. `workflow_stages` (案件處理流程狀態機表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 階段狀態識別碼 |
| `case_id` | `UUID` | NOT NULL | 案件識別碼 |
| `revision_id` | `UUID` | NOT NULL | 版本識別碼 |
| `stage_name` | `workflow_stage_enum` | NOT NULL | 流程階段名稱 |
| `status` | `workflow_status_enum` | NOT NULL DEFAULT 'DRAFT' | 階段處理狀態 (`DRAFT`, `IN_REVIEW`, `APPROVED`, `CHANGES_REQUESTED`, `PROCESSING`, `FAILED`, `STALE`, `CANCELLED`, `ARCHIVED`) |
| `entered_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 進入該階段時間 |
| `completed_at` | `TIMESTAMPTZ` | NULL | 該階段完成/核定時間 |
| **外鍵** | `FOREIGN KEY (case_id, revision_id) REFERENCES case_revisions(case_id, id)` |
| **約束** | `UNIQUE(revision_id, stage_name)` | 單一版本內階段唯一 |

### 22. `review_approvals` (人工審核閘門紀錄表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 審核紀錄唯一碼 |
| `case_id` | `UUID` | NOT NULL, FK -> `cases(id)` | 案件識別碼 |
| `revision_id` | `UUID` | NOT NULL | 審核所針對之版本快照 |
| `target_entity_type`| `VARCHAR(64)` | NOT NULL | 被審核標的 (`REVISION_SUMMARY`, `LEGAL_DIRECTION`, `DOCUMENT_OUTPUT`) |
| `target_entity_id`| `UUID` | NOT NULL | 被審核標的實體識別碼 |
| `reviewer_id` | `UUID` | NOT NULL, FK -> `users(id)` | 審核主管/長官 |
| `status` | `approval_status_enum` | NOT NULL | 審核結果 (`APPROVED`, `REJECTED`, `PENDING`) |
| `comments` | `TEXT` | NOT NULL | 人工審核指示與意見 |
| `approval_hash` | `VARCHAR(64)` | NOT NULL | 審核時標的內容之 SHA-256 數位簽章 |
| `reviewed_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 審核完成時間 |

### 23. `document_outputs` (條陳、函稿與報告產出物表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 文件產出識別碼 |
| `case_id` | `UUID` | NOT NULL | 案件識別碼 |
| `revision_id` | `UUID` | NOT NULL | 依據之版本識別碼 |
| `document_type` | `VARCHAR(32)` | NOT NULL | 公文類型 (`MEMORANDUM` 條陳, `INVESTIGATION_REPORT` 調查報告, `TRANSCRIPT_SUMMARY` 筆錄摘要) |
| `title` | `VARCHAR(255)` | NOT NULL | 文件標題 |
| `content_markdown`| `TEXT` | NOT NULL | 文件正式內容 (Markdown / 結構化法規引用文字) |
| `is_final` | `BOOLEAN` | NOT NULL DEFAULT FALSE | 是否為核定正式本 |
| `approval_id` | `UUID` | NULL, FK -> `review_approvals(id)` | 正式本強制關聯之審核紀錄 |
| `generated_by` | `UUID` | NOT NULL, FK -> `users(id)` | 製表人員 |
| `generated_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 產出時間 |
| **外鍵** | `FOREIGN KEY (case_id, revision_id) REFERENCES case_revisions(case_id, id)` |
| **約束** | `CHECK (is_final = FALSE OR (is_final = TRUE AND approval_id IS NOT NULL))` | 正式本強制要求審核記錄 |

### 24. `llm_prompt_templates` (AI 輔助提示詞範本與版本管制表)
| 欄位名稱 | 型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | 範本識別碼 |
| `template_code` | `VARCHAR(64)` | NOT NULL | 範本代碼 (如：`FACT_DECOMPOSITION_V2`, `TRANSCRIPT_QUESTION_GEN`) |
| `version` | `INTEGER` | NOT NULL DEFAULT 1 | 範本版本號 |
| `system_prompt` | `TEXT` | NOT NULL | 系統規範指示詞 (包含嚴格禁止擅斷、法律追溯等 Guardrails) |
| `user_prompt_pattern`| `TEXT` | NOT NULL | 案件事實帶入模板 |
| `output_schema_json`| `JSONB` | NOT NULL | 嚴格要求之 JSON Schema 約束定義 |
| `is_active` | `BOOLEAN` | NOT NULL DEFAULT TRUE | 是否啟用 |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `clock_timestamp()` | 建立時間 |
| **約束** | `UNIQUE(template_code, version)` |
