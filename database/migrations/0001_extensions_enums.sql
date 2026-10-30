-- Migration: 0001_extensions_enums.sql
-- Description: 初始化 PostgreSQL 核心擴充套件與系統列舉型別 (Enums)
-- System: 刑事偵查輔助系統 (Criminal Investigation Analysis System v2.0)

BEGIN;

-- 1. 核心擴充套件 (UUID 生成與密碼/雜湊演算法支援，原生或外掛容錯)
DO $$ BEGIN
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

DO $$ BEGIN
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

-- 2. 機密等級列舉
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'classification_level_enum') THEN
        CREATE TYPE classification_level_enum AS ENUM (
            'PUBLIC',         -- 一般公開/非密
            'INTERNAL',       -- 機關內部公務
            'CONFIDENTIAL',   -- 密 (偵查不公開案件預設)
            'SECRET'          -- 國家機密/重大重大矚目案件
        );
    END IF;
END $$;

-- 3. 事實認知與陳述狀態列舉 (遵循嚴格不可擅斷原則)
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'fact_status_enum') THEN
        CREATE TYPE fact_status_enum AS ENUM (
            'ASSERTED',       -- 告訴人/證人單方陳述，尚未有客觀佐證
            'ADMITTED',       -- 被告/嫌疑人坦承自白
            'DENIED',         -- 被告/嫌疑人否認 (不可等同客觀不存在)
            'INFERRED',       -- 由關聯證據或前後事實推論
            'UNKNOWN'         -- 待查證事實 (嚴禁視同 FALSE 或已否定)
        );
    END IF;
END $$;

-- 4. 構成要件支持度狀態列舉
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'element_status_enum') THEN
        CREATE TYPE element_status_enum AS ENUM (
            'SUPPORTED',      -- 有具體事證支持
            'CONTRADICTED',   -- 現存事證產生排斥或矛盾
            'UNRESOLVED',     -- 尚待調查釐清
            'NOT_APPLICABLE'  -- 該條文非必要要件或法律阻卻
        );
    END IF;
END $$;

-- 5. 候選法律方向/罪名狀態列舉 (防範單一罪名隧道視野)
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'candidate_status_enum') THEN
        CREATE TYPE candidate_status_enum AS ENUM (
            'PRIMARY',        -- 主要偵查/起訴罪名方向
            'ALTERNATIVE',    -- 備位/競合罪名方向
            'LOW_CONFIDENCE', -- 事證或見解仍顯脆弱之方向
            'UNRESOLVED',     -- 要件尚未分析完畢
            'REJECTED'        -- 事實排除或法規不符而剔除
        );
    END IF;
END $$;

-- 6. 證據來源核實狀態列舉
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'source_status_enum') THEN
        CREATE TYPE source_status_enum AS ENUM (
            'VERIFIED',          -- 正本或正式公文查核無誤
            'UNVERIFIED',        -- 影本或待驗證線索
            'UNAVAILABLE',       -- 來源調取不能或滅失
            'VERSION_UNCERTAIN'  -- 法規或文件版本有效性存疑
        );
    END IF;
END $$;

-- 7. 案件偵查流程階段列舉
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'workflow_stage_enum') THEN
        CREATE TYPE workflow_stage_enum AS ENUM (
            'FACTS_INTAKE',        -- 案情與事實整理
            'BEHAVIOR_ANALYSIS',   -- 行為人客觀行為拆解
            'LEGAL_RESEARCH',      -- 法規與裁判見解查核
            'ELEMENT_EVALUATION',  -- 構成要件涵攝與爭點整理
            'INTERVIEW_PREP',      -- 筆錄問句擬定
            'INTERVIEW_EXECUTION', -- 筆錄執行與事實更新
            'DOCUMENT_GENERATION', -- 條陳與調查報告製作
            'COMPLETED'            -- 全案階段結案核定
        );
    END IF;
END $$;

-- 8. 流程處理狀態列舉 (支援下游無效化 STALE)
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'workflow_status_enum') THEN
        CREATE TYPE workflow_status_enum AS ENUM (
            'DRAFT',               -- 草稿
            'IN_REVIEW',           -- 提交審核中
            'APPROVED',            -- 長官審核核可
            'CHANGES_REQUESTED',   -- 駁回補正
            'PROCESSING',          -- 背景計算/AI處理中
            'FAILED',              -- 處理失敗
            'STALE',               -- 上游異動導致下游過期無效
            'CANCELLED',           -- 取消
            'ARCHIVED'             -- 歷史封存
        );
    END IF;
END $$;

-- 9. 人工審核決定列舉
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'approval_status_enum') THEN
        CREATE TYPE approval_status_enum AS ENUM (
            'PENDING',    -- 待簽核
            'APPROVED',   -- 核定通過
            'REJECTED'    -- 退回修正
        );
    END IF;
END $$;

COMMIT;
