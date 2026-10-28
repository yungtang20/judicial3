# 問句家族骨架設計稿

狀態：`DESIGN_DRAFT`、`runtime_enabled: false`、`HUMAN_REVIEW_REQUIRED`。

本設計稿依 `D:\工作用\judicial1\傷害家族問句樣板.md` 與使用者提出的家族分組建議建立。它改變的是問句設計與資料組織方式，不是法律分類，也不取代現有 `legal_route_crosswalk.json` 的 child route、法源版本或 `CASE_HUMAN_GATE`。

## 目標結構

```text
通用層 common
  └─ 人別、權利告知、自由陳述、補充、有利證據、結尾與筆錄確認
家族層 family skeleton
  └─ 同一事實骨架的角色化問句
要件補強層 route supplement
  └─ 各 child route 缺口、前置條件、區辨軸與證據追問
```

同一題不得因為出現在多個罪名而複製成多欄不同版本；應以 `family_id + fact_target + target_interview_role` 作為重用與去重索引，再由 route supplement 補足個別要件。

## 已確認的現況

- `data/question_bank.json` 已有 `common` 與 offense-level `elements`，並有角色化問句，但尚無家族主檔。
- `app/questions.py` 已支援 `fact_target`、`legal_targets`、角色實體化與 20 題預算，可作為家族層接入點；目前不可直接把家族題當 runtime 題，仍須通過 route allowlist、去重與 Human Gate。
- `witness_review_only` 應維持 review-only，不直接當現行 server role。
- 使用者提到的 32 個資料夾目前尚未在 `D:\工作用\judicial1\questions` 觀察到；catalog 已標記 `UNKNOWN_REQUIRES_USER_OR_REPOSITORY_MAPPING`。

## 目前建立的 draft artifact

- `data/question_family_catalog.json`
- `data/question_family_master/injury_family_questions.json`：第一份一題一列的家族題庫；由傷害家族 Markdown 樣板決定性產生。
- `data/question_family_master/common_questions.json`：既有 34 題 runtime 通用題加上 6 題證人 review-only 草稿的長表索引。
- `tools/question_family_compiler.py`：將人工可讀樣板轉為長表題庫，`--check` 用於檢查樣板與題庫是否同步。
- `tools/question_common_compiler.py`：從現有 `question_bank.json:common` 建立通用層索引，並合併不進 runtime 的證人草稿。
- 來源樣板：`D:\工作用\judicial1\傷害家族問句樣板.md`

catalog 只保存分組、共享事實軸、補強方向、前置模組與未映射標籤；不宣稱法條已查核、不啟用 runtime、不把家族名稱當候選罪名。

## 傷害家族的接入方式

傷害樣板可作為第一個 family fixture，先保留 V／S／W 三種角色與 E1、E3、E4、E5、E6 條件模組；A 欄通用層引用既有 `common`，不在 family fixture 重複。每一題需轉成：

`target_interview_role`、`family_id`、`fact_target`、`element_type`、`layer`、`required_or_optional`、`preconditions`、`legal_targets`、`provenance`、`review_status`。

家族主檔以 `target_interview_roles` 保存一題可適用的多個角色；真正接入 runtime 時才展開成單一 `target_interview_role` 的角色實例。傷害家族目前共有 78 題來源紀錄，其中 56 題為三類角色主表、22 題為 E1／E3／E4／E5／E6 條件模組。所有紀錄仍為 `runtime_enabled=false`；`legal_targets` 已完成 repository 內部 child route 結構映射，但法律適用範圍仍為 Human Gate。

家族來源列若已有通用層 owner，保留原列與 provenance，但標記 `materialization_policy=REUSE_COMMON_LAYER`；未來組題只能取 common owner，不得同時再取家族列。語意相近不會自動合併，必須在 `common_layer.json` 明列 ownership，避免誤刪具有要件補強功能的題目。

樣板中的「已用 tw-legal-rag 核對」與程序／實務主張在本專案尚未取得可回查證據前，維持 `USER_DESIGN_DRAFT`／`HUMAN_REVIEW_REQUIRED`，不得寫入 `VERIFIED_CURRENT`。

## 不在本次接入的範圍

- 不刪除或重命名現有章節 child routes。
- 不把贓物、槍砲、組織犯罪、洗錢等尚未存在於 crosswalk 的標籤自動創成 route。
- 不修改 runtime、前端、XLSM、正式題庫或部署設定。
- 不把第95條、第196-1條、具結適用性或內部作業規定的推論當成已核准法律結論。

## 下一個可驗證工作單

先將 `傷害家族問句樣板.md` 轉成一個獨立 fixture，執行：角色覆蓋、前置條件、每個 route 的要件缺口、exact／semantic 去重、20 題預算與 review-only 邊界測試；通過後才評估接入 `app/questions.py`。
