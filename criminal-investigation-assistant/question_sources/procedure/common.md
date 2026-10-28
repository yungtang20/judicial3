# 通用程序問句主檔

## Metadata

- family_id: `common_procedure`
- version: `1.0.0`
- legal_review_status: `HUMAN_REVIEW_REQUIRED`
- runtime_status: `AVAILABLE_WITH_WARNING`

## Questions

| question_id | role | text | fact_target | element_type | layer | requirement | routes | preconditions | prohibitions | source | version | editorial_status | method_review_status | legal_review_status | runtime_status | page_cost | template_binding |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C-V01 | victim | 請說明你與本案及其他關係人的關係。 | identity | identity | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-V02 | victim | 請依時間順序，從你認為最早相關的事情開始完整說明。 | free_narrative | context | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-V03 | victim | 哪些內容是你親自知道，哪些是他人告知或事後推測？ | knowledge_basis | evidence | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-V04 | victim | 你有哪些資料、物品或證人可以提供警方查證？ | evidence | evidence | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-V05 | victim | 你是否還有需要補充、更正或提出告訴意願的事項？ | closing | procedure | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-S01 | suspect | 警方已向你告知本次詢問的案由及相關權利，你是否了解？ | rights_notice | procedure | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-S02 | suspect | 請依時間順序，從你認為最早相關的事情開始完整說明。 | free_narrative | context | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-S03 | suspect | 對於目前所述事情，你有哪些不同說明或需要釐清之處？ | response | context | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-S04 | suspect | 你有哪些對自己有利的事實或證據希望警方調查？ | exculpatory_evidence | evidence | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-S05 | suspect | 你是否還有需要補充或更正的事項？ | closing | procedure | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-W01 | witness | 請說明你與本案各關係人的關係，以及你當時所在位置。 | witness_basis | identity | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-W02 | witness | 請依時間順序說明你親自看見、聽見或處理的經過。 | free_narrative | context | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-W03 | witness | 請說明哪些內容不是你親自得知，以及其來源。 | hearsay_source | evidence | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-W04 | witness | 你有哪些資料或其他證人線索可以提供查證？ | evidence | evidence | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |
| C-W05 | witness | 你是否還有需要補充或更正的事項？ | closing | procedure | procedure | REQUIRED | ALL | NONE | LEADING,ASSUMES_GUILT | CPC_AND_INTERNAL_TEMPLATE_REVIEW | 1 | AI_REVIEWED | AI_REVIEWED | HUMAN_REVIEW_REQUIRED | AVAILABLE_WITH_WARNING | 1 | NONE |

## Review boundary

- 權利告知與程序文字必須再與現行法及機關內規核對。
