"""問句衛生判定：載入公司題庫前，先決定每一格能否進訪談頻道。

依 questions/company-standard.md 第四節（不匯入已填寫實例的案情答案）與
questions/review-checklist.md 第一、二節（去重複、角色語句不得錯置）。
判定只決定「通道」，不修改公司原文：不合衛生的格子改列參考資料回報。
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    rule_id: str
    scope: frozenset[str]
    pattern: re.Pattern[str] | None
    decision: str
    reason: str


@dataclass(frozen=True)
class Verdict:
    rule_id: str
    decision: str
    reason: str


ALL_ROLES = frozenset({"victim", "suspect", "witness", "transfer"})

# 他案案情或日期殘留。第三個複合樣式（`字第…號`）補足無外文前綴的公文文號
# （例：北市警刑偵字第1133115422號），只靠 [A-Z]{2,} 會漏掉中文機關前綴。
_FOREIGN_CASE_ARTIFACT = re.compile(
    "|".join((
        r"民國\d+年\d+月\d+日",
        r"(?<!\d)\d{3,4}年\d{1,2}月\d{1,2}日",
        r"今?[（(]\s*\d{1,2}\s*[）)]日?",
        r"(?<![\d:：])\d{1,2}/\d{1,2}(?![\d:：])",
        r"[A-Z]{2,}字第\d+號",
        r"字第\s*\d{3,}號",
    )),
)

# 他案已填寫實例的車牌等識別細節（company-standard 第四節）。
_INSTANCE_DETAIL = re.compile(r"(?<![A-Za-z0-9])[A-Z0-9]{1,3}-\d{3,4}(?![A-Za-z0-9])")

RULES: tuple[Rule, ...] = (
    Rule(
        rule_id="foreign_case_artifact",
        scope=ALL_ROLES,
        pattern=_FOREIGN_CASE_ARTIFACT,
        decision="REFERENCE_ONLY",
        reason="他案案情或日期殘留（company-standard 四）",
    ),
    Rule(
        rule_id="foreign_case_instance_detail",
        scope=ALL_ROLES,
        pattern=_INSTANCE_DETAIL,
        decision="REFERENCE_ONLY",
        reason="他案已填寫實例細節（company-standard 四）",
    ),
    Rule(
        rule_id="role_inversion",
        scope=frozenset({"suspect", "witness"}),
        pattern=re.compile("|".join((r"遭人(?:傷害|毆打|攻擊)", r"遭受行為人", r"他為何要傷害你"))),
        decision="REFERENCE_ONLY",
        reason="涉嫌人/證人題組含被害人語句（review-checklist 二）",
    ),
    Rule(
        rule_id="role_inversion_victim",
        scope=frozenset({"victim"}),
        pattern=re.compile("|".join((r"是否認識被害人", r"遭受行為人", r"你於何時、何地遭受"))),
        decision="REFERENCE_ONLY",
        reason="被害人題組含他角色語句（review-checklist 二）",
    ),
    Rule(
        rule_id="duplicate_normalized",
        scope=ALL_ROLES,
        pattern=None,
        decision="DROP_DUPLICATE",
        reason="語意相同（review-checklist 一.6）",
    ),
)

SERVE = Verdict(rule_id="", decision="SERVE", reason="")

_PUNCTUATION_FOLD = str.maketrans({
    "？": "?", "！": "!", "，": ",", "。": ".", "、": ",",
    "：": ":", "；": ";", "（": "(", "）": ")",
    "「": '"', "」": '"', "『": '"', "』": '"', "〈": "<", "〉": ">",
    "－": "-", "\u3000": "",
})


def classify(text: str, role: str) -> Verdict:
    """依 RULES 順序判定單一格；第一個命中者決定通道，未命中即 SERVE。"""
    for rule in RULES:
        if rule.pattern is None or role not in rule.scope:
            continue
        if rule.pattern.search(text):
            return Verdict(rule_id=rule.rule_id, decision=rule.decision, reason=rule.reason)
    return SERVE


def duplicate_verdict() -> Verdict:
    """重複判定由載入器執行（classify 看不到先前的格子），規則資料仍取自同一表。"""
    rule = next(rule for rule in RULES if rule.rule_id == "duplicate_normalized")
    return Verdict(rule_id=rule.rule_id, decision=rule.decision, reason=rule.reason)


def normalize(text: str) -> str:
    """去重鍵：去除所有空白並折疊全形標點，使「？」與「?」等視為同一題。"""
    return re.sub(r"\s+", "", text.translate(_PUNCTUATION_FOLD))


def semantic_key(text: str) -> str:
    """回傳少數已核定的共同事實主題鍵。

    只合併跨題庫明確詢問同一事實的固定句型，不用模糊相似度猜測法律問題。
    未命中固定句型時，退回一般正規化文字鍵。
    """

    value = normalize(text)
    if (
        ("年籍資料" in value or "身分資料" in value or "姓名對照表" in value)
        and "是否正確" in value
        and ("是否為你本人" in value or "身分資料" in value)
    ):
        return "identity:personal-record"
    if "提出告訴" in value and ("民事求償" in value or "民事賠償" in value):
        return "procedure:complaint-and-civil-claim"
    if (
        ("與對方是否認識" in value or "與行為人原本有何關係" in value
         or "雙方之間的關係" in value)
        and ("關係" in value or "認識" in value)
    ):
        return "fact:prior-relationship"
    if any(
        marker in value
        for marker in (
            "現場有無裝設監視器",
            "其他人見聞",
            "哪些人可能看見或聽見",
            "資料或物品可以提供警方查證",
            "佐證資料可提供警方",
            "請警方協助調查",
            "需要警方協助調查其他有利事證",
            "目擊者或知情人",
            "提供警方相關佐證資料",
        )
    ):
        return "evidence:scene-and-investigation-support"
    if "送達" in value and ("地址" in value or "何處" in value):
        return "procedure:service-address"
    if "告訴意願另依" in value:
        return "procedure:complaint-confirmation"
    if "藥劑" in value and "兇器" in value:
        return "fact:drug-weapon"
    if "營利" in value and any(term in value for term in ("場所", "工具", "設備")):
        return "fact:profit-purpose-resources"
    if (
        ("以上" in value or "上述" in value or "其他想補充" in value)
        and any(term in value for term in ("補充", "實在", "陳述"))
    ):
        return "procedure:final-confirmation"
    if "自由意識下" in value or "親自陳述" in value:
        return "procedure:voluntary-statement"
    if "時間與地點為何" in value:
        return "fact:time-place"
    if "發現" in value and "時間為何" in value:
        return "fact:discovery-report-time"
    if "法定代理人或監護人" in value and "身分與聯絡方式" in value:
        return "person:legal-representative"
    if ("是否實在" in value or "是否屬實" in value) and "補充" in value:
        return "procedure:final-confirmation"
    return value
