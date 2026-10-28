# 臺灣法條引用契約（離線 v1）

## 範圍

本契約只處理 `Citation Mention`：文字中出現的法條引用及其位置。它不判斷否定／肯定立場、不判斷法律適用、不產生候選罪名，也不產生裁判採用的法律依據。

實作位於 `app/citation_contract.py`，不被正式案件 workflow import；因此不修改現有候選產生、排序、Prompt、Schema 或 runtime。

## 核心結構

每筆 `CitationMention` 包含：

- `law_name`
- `article_number`
- `article_subnumber`
- `paragraph_number`
- `item_number`
- `subitem_number`
- `raw_text`
- `source_ref`
- `source_start`／`source_end`
- `parse_status`：`SUCCESS`、`PARTIAL`、`UNPARSED`
- `law_name_status`
- `normalization_version`
- `mention_type=CITATION_MENTION`
- `stance_status=NOT_ANALYZED`

所有數字層級以整數保存；原始引用文字與 offset 永遠保留。

## 四層語義分離

| 概念 | 本契約表示 | 是否由 parser 自動產生 |
|---|---|---|
| Citation Mention | `CitationMention` | 是 |
| Legal Source | `LegalSource` | 否，需來源版本與驗證狀態 |
| Legal Applicability Candidate | `LegalApplicabilityCandidate` | 否，需分析流程明確建立 |
| Applied Legal Basis | `AppliedLegalBasis` | 否，需人工／授權步驟建立 |

`CitationMention` 成功解析，只表示文字引用可被結構化；不表示該法條適用、支持犯罪成立或已被採用。

## 正規化規則

- 只使用 `APPROVED_LAW_ALIASES` 中的簡稱；未知法規名稱回報 `PARTIAL`，不猜測。
- 支援阿拉伯、全形及中文數字。
- 支援條、條之、項、款、目。
- 支援同一法規的多條引用及 `同法` 前文 context。
- 不以文字是否包含「無關」「不適用」「否認」改寫引用；立場另由獨立流程處理。
- `normalization_version` 可隨規則版本升級；原始輸入不被正規化結果覆寫。

## 明確不做

- 不將 parser 結果轉成 `candidate_offense`。
- 不將 citation match 當成 `ELIGIBLE_CANDIDATE`、`NEEDS_FACTS` 或犯罪成立證據。
- 不把未核准同義詞自動加入正式詞庫。
- 不連接外部 MCP、LLM、正式 DB 或法律資料服務。
