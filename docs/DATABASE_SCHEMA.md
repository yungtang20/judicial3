# 資料庫規格書（DATABASE_SCHEMA.md）

- **引擎**：Supabase PostgreSQL / PostgREST
- **權限架構**：Row Level Security (RLS) 全面啟用
- **金鑰原則**：應用層端對端 Fernet / AES-GCM 加密，PostgreSQL 僅保存 `encrypted_payload`

---

## 1. 核心資料表清單 (16 Tables)

1. **`users` / `profiles`**：單一指定使用者設定檔（`id`, `auth_user_id`, `display_name`, `created_at`）。
2. **`cases`**：案件主檔（`id uuid primary key`, `owner_id uuid`, `title`, `status`, `current_revision_id`, `created_at`, `updated_at`, `archived_at`）。
3. **`case_revisions`**：案件版本修訂檔（`id`, `case_id`, `revision_number`, `encrypted_payload`, `encryption_key_version`, `content_hash`, `created_by`, `created_at`）。
4. **`facts`**：結構化事實表（`id`, `case_id`, `revision_id`, `subject`, `predicate`, `object`, `event_time`, `event_location`, `source_type`, `source_ref`, `source_excerpt`, `assertion_status`, `confidence`, `created_at`, `updated_at`）。
5. **`evidence_items`**：扣案與保全物證（`id`, `case_id`, `evidence_type`, `source_description`, `encrypted_payload`, `collection_status`, `created_at`）。
6. **`fact_evidence_links`**：事實與證據關聯表（`fact_id`, `evidence_id`, `relationship_type`, `notes`）。
7. **`behaviors`**：行為階段整理表（`id`, `case_id`, `revision_id`, `actor_ref`, `action_description`, `object_ref`, `time_ref`, `fact_refs`, `uncertainty_status`）。
8. **`legal_candidates`**：候選法律方向表（`id`, `case_id`, `revision_id`, `legal_name`, `statute_ref`, `candidate_status`, `support_fact_refs`, `contrary_fact_refs`, `unknown_fact_refs`, `exclusion_reason`, `analysis_payload`, `created_at`）。
9. **`legal_elements`**：構成要件拆解分析表（`id`, `candidate_id`, `element_name`, `element_description`, `related_fact_refs`, `element_status`, `reasoning`, `source_ref`）。
10. **`core_issues`**：核心爭點表（`id`, `case_id`, `candidate_id`, `issue_description`, `supporting_facts`, `contrary_facts`, `unresolved_questions`, `priority`）。
11. **`interview_questions`**：筆錄問句表（`id`, `case_id`, `candidate_id`, `element_id`, `question_type`, `question_text`, `rationale`, `target_fact_refs`, `priority`, `review_status`, `revision_number`）。
12. **`interview_answers`**：受詢問人回答表（`id`, `question_id`, `answer_text_encrypted`, `source_type`, `answer_revision`, `created_at`, `created_by`）。
13. **`review_records`**：人工審核歷程表（`id`, `case_id`, `gate_name`, `target_revision_id`, `review_status`, `reviewer_id`, `comments_encrypted`, `reviewed_at`）。
14. **`analysis_runs`**：模型分析日誌表（`id`, `case_id`, `task_type`, `model_provider`, `model_id`, `prompt_version`, `input_revision_id`, `output_revision_id`, `validation_status`, `error_code`, `started_at`, `completed_at`）。
15. **`document_outputs`**：公務條陳與產製文件表（`id`, `case_id`, `document_type`, `source_revision_ids`, `encrypted_content`, `format`, `generation_status`, `review_status`, `created_at`）。
16. **`audit_events`**：安全稽核紀錄表（`id`, `actor_id`, `case_id`, `event_type`, `target_type`, `target_id`, `occurred_at`, `metadata`）。

---

## 2. RLS 隔離與約束政策
```sql
alter table public.cases enable row level security;
alter table public.cases force row level security;

revoke all on table public.cases from anon;
grant select, insert, update, delete on table public.cases to authenticated;

-- 單一核准使用者政策
create policy cases_owner_isolation on public.cases
  for all to authenticated
  using ( (select auth.uid()) = owner_id )
  with check ( (select auth.uid()) = owner_id );
```
