# 條件式程序模組問句主檔

## Metadata

- family_id: `common_procedure`
- version: `1.0.0`
- legal_review_status: `HUMAN_REVIEW_REQUIRED`
- runtime_status: `AVAILABLE_WITH_WARNING`

## Questions

| question_id | role | text | fact_target | element_type | layer | requirement | routes | preconditions | prohibitions | source | version | editorial_status | method_review_status | legal_review_status | runtime_status | page_cost | template_binding |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M-DV-V01 | victim | 請說明你與對方的家庭、同住、照顧或親密關係？ | domestic_relationship | relationship | conditional_module | CONDITIONAL | ALL | DOMESTIC_RELATIONSHIP_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-DV-S01 | suspect | 請說明你與對方的家庭、同住、照顧或親密關係？ | domestic_relationship | relationship | conditional_module | CONDITIONAL | ALL | DOMESTIC_RELATIONSHIP_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-DV-W01 | witness | 就你親自知道的部分，雙方有何家庭、同住、照顧或親密關係？ | domestic_relationship | relationship | conditional_module | CONDITIONAL | ALL | DOMESTIC_RELATIONSHIP_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-DV-V02 | victim | 你目前需要哪些立即安全協助？ | immediate_safety_need | procedure | conditional_module | CONDITIONAL | ALL | DOMESTIC_RELATIONSHIP_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-JU-S01 | suspect | 你的出生年月日可由哪些資料確認？ | minor_age_proof | identity | conditional_module | CONDITIONAL | ALL | MINOR_INVOLVED_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-JU-W01 | witness | 未成年當事人的年齡可由哪些資料確認？ | minor_age_proof | identity | conditional_module | CONDITIONAL | ALL | MINOR_INVOLVED_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-JU-S02 | suspect | 你目前需要法定代理人、陪同人或其他程序協助嗎？ | minor_procedure_support | procedure | conditional_module | CONDITIONAL | ALL | MINOR_INVOLVED_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-CP-V01 | victim | 你目前有何照顧、安置、醫療或安全協助需求？ | child_safety_support | procedure | conditional_module | CONDITIONAL | ALL | MINOR_INVOLVED_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-SX-V01 | victim | 你希望由何種性別或具何種專業的人員進行後續詢問？ | special_interview_preference | procedure | conditional_module | CONDITIONAL | ALL | SEXUAL_CASE_ROUTE | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-SX-V02 | victim | 你目前需要哪些陪同、醫療、隔離或其他程序協助？ | special_interview_support | procedure | conditional_module | CONDITIONAL | ALL | SEXUAL_CASE_ROUTE | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-ST-V01 | victim | 目前已有告誡、保護令或其他安全措施的情形為何？ | existing_protection | procedure | conditional_module | CONDITIONAL | ALL | STALKING_ROUTE | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-ST-V02 | victim | 哪些近期變化使你認為風險增加或降低？ | risk_change | context | conditional_module | CONDITIONAL | ALL | STALKING_ROUTE | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-IN-V01 | victim | 你慣用何種語言或溝通方式？ | communication_language | procedure | conditional_module | CONDITIONAL | ALL | INTERPRETER_NEED_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-IN-S01 | suspect | 你慣用何種語言或溝通方式？ | communication_language | procedure | conditional_module | CONDITIONAL | ALL | INTERPRETER_NEED_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-IN-W01 | witness | 你慣用何種語言或溝通方式？ | communication_language | procedure | conditional_module | CONDITIONAL | ALL | INTERPRETER_NEED_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-IN-V02 | victim | 你需要何種翻譯、手語或其他溝通協助？ | communication_support | procedure | conditional_module | CONDITIONAL | ALL | INTERPRETER_NEED_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-IN-S02 | suspect | 你需要何種翻譯、手語或其他溝通協助？ | communication_support | procedure | conditional_module | CONDITIONAL | ALL | INTERPRETER_NEED_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-NI-S01 | suspect | 請說明本次在夜間進行詢問的原因？ | night_interview_reason | procedure | conditional_module | CONDITIONAL | ALL | NIGHT_INTERVIEW_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-NI-S02 | suspect | 你目前的身心狀況是否適合繼續接受詢問？ | interview_fitness | procedure | conditional_module | CONDITIONAL | ALL | NIGHT_INTERVIEW_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-RC-V01 | victim | 錄音或錄影中斷發生在何時？ | recording_interruption_time | procedure | conditional_module | CONDITIONAL | ALL | RECORDING_INTERRUPTION_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-RC-S01 | suspect | 錄音或錄影中斷發生在何時？ | recording_interruption_time | procedure | conditional_module | CONDITIONAL | ALL | RECORDING_INTERRUPTION_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-RC-W01 | witness | 錄音或錄影中斷發生在何時？ | recording_interruption_time | procedure | conditional_module | CONDITIONAL | ALL | RECORDING_INTERRUPTION_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-RC-S02 | suspect | 錄音或錄影中斷的原因為何？ | recording_interruption_reason | procedure | conditional_module | CONDITIONAL | ALL | RECORDING_INTERRUPTION_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-ID-V01 | victim | 請確認本案使用的代號及其對應紀錄由何處查得？ | coded_identity_record | evidence | conditional_module | CONDITIONAL | ALL | CODED_VICTIM_CONFIRMED | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-GE-V01 | victim | 事件發生時雙方在工作或教育場所各自具有何種身分？ | work_education_role | identity | conditional_module | CONDITIONAL | ALL | WORK_OR_EDUCATION_CONTEXT | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-GE-S01 | suspect | 事件發生時雙方在工作或教育場所各自具有何種身分？ | work_education_role | identity | conditional_module | CONDITIONAL | ALL | WORK_OR_EDUCATION_CONTEXT | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-GE-W01 | witness | 就你親自知道的部分，雙方在工作或教育場所各自具有何種身分？ | work_education_role | identity | conditional_module | CONDITIONAL | ALL | WORK_OR_EDUCATION_CONTEXT | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| M-DI-S01 | suspect | 對於雙方陳述不一致的部分，請依你的記憶逐項說明事實與依據？ | role_statement_difference | distinguishing | conditional_module | CONDITIONAL | ALL | ROLE_DISCREPANCY_PRESENT | LEADING,ASSUMES_GUILT | PROCEDURE_MODULE_DESIGN | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |

## Activation boundary

- 前置條件未由案件文字或候選 route 明確支持時不得顯示。
- 程序模組仍須依現行法及機關內規完成人工核對。
