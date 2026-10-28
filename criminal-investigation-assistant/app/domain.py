from __future__ import annotations

import re
import hashlib
from copy import deepcopy
from typing import Any
from uuid import uuid4

from .question_bank import QuestionBank


SCHEMA_VERSION = "case-snapshot/v1"
MAX_SUMMARY_LENGTH = 500

ROUTE_RULES = [
    ("theft", "property_possession_taking", ("偷", "竊", "拿走", "取走", "皮夾", "手機", "金融卡")),
    ("aggravated_theft", "property_possession_taking", ("破壞門窗", "侵入住宅", "攜帶兇器", "結夥")),
    ("embezzlement", "property_possession_taking", ("保管", "借用", "代收", "拾得", "拒不返還", "侵占")),
    ("robbery", "coercion_liberty_threat", ("搶", "強盜", "強奪", "壓制", "不能抗拒")),
    ("damage", "property_damage", ("毀損", "砸", "破壞", "刮傷")),
    ("fraud", "deception_disposition_trust", ("詐騙", "詐欺", "假投資", "匯款", "騙")),
    ("injury", "human_violence", ("打", "踢", "傷害", "受傷", "毆")),
    ("homicide", "human_violence", ("殺", "死亡", "致死")),
    ("liberty", "coercion_liberty_threat", ("限制自由", "拘禁", "強制")),
    ("intimidation", "coercion_liberty_threat", ("恐嚇", "威脅")),
    ("stalking", "coercion_liberty_threat", ("跟蹤", "騷擾")),
    ("forgery", "document_seal_identity", ("偽造", "冒簽", "假文書", "印章")),
    ("defamation", "reputation_speech", ("誹謗", "侮辱", "名譽")),
    ("privacy", "privacy_secret_sexual_image", ("偷拍", "竊錄", "性影像", "秘密")),
    ("public_danger", "public_danger_traffic", ("酒駕", "毒駕", "肇事逃逸", "酒測")),
    ("drugs", "drugs_firearms_organization", ("毒品", "安非他命", "大麻", "販毒")),
    ("computer", "computer_network_digital_evidence", ("駭客", "入侵", "帳號", "密碼", "刪除資料")),
    ("sexual", "sexual_child_exploitation", ("性侵", "性交", "猥褻")),
    ("sexual_harassment", "sexual_child_exploitation", ("性騷擾",)),
    ("state_security", "specialist_routes", ("內亂", "外患", "國家安全", "國安法", "間諜")),
    ("duty", "justice_public_service_order", ("瀆職", "受賄", "賄賂", "圖利", "公務員洩密")),
    ("obstruction", "justice_public_service_order", ("妨害公務", "抗拒員警", "抗拒盤查", "對警察施暴", "辱罵", "侮辱公務員")),
    ("judicial_integrity", "justice_public_service_order", ("妨害司法", "影響證言", "證人賄賂")),
    ("voting", "justice_public_service_order", ("妨害投票", "賄選", "投票受賄")),
    ("disorder", "justice_public_service_order", ("妨害秩序", "聚眾施暴", "聚眾鬥毆")),
    ("escape", "justice_public_service_order", ("脫逃", "藏匿人犯", "使人犯脫逃")),
    ("evidence", "justice_public_service_order", ("湮滅證據", "隱匿證物", "偽造證據")),
    ("accusation", "justice_public_service_order", ("偽證", "誣告", "虛偽證述")),
    ("currency", "specialist_routes", ("偽造貨幣", "偽鈔", "變造貨幣")),
    ("securities", "money_flow_laundering_stolen_goods", ("偽造支票", "偽造本票", "偽造有價證券", "支付卡電磁紀錄")),
    ("weights_measures", "specialist_routes", ("度量衡", "磅秤不準", "偽造度量")),
    ("obscenity", "specialist_routes", ("公然猥褻", "散布猥褻物", "販賣猥褽物品")),
    ("marriage", "specialist_routes", ("重婚", "詐術結婚", "妨害婚姻")),
    ("graves_religion", "specialist_routes", ("褻瀆祀典", "破壞墳墓", "侵害遺骨", "侵害屍體")),
    ("agriculture_commerce", "specialist_routes", ("妨害農工商", "妨害農事", "囤積必需品", "哄抬價格")),
    ("opium", "drugs_firearms_organization", ("鴉片", "罌粟種子")),
    ("gambling", "specialist_routes", ("賭博", "聚眾賭博", "網路賭博")),
    ("abortion", "human_violence", ("墮胎", "使之流產", "非法終止懷孕")),
    ("abandonment", "human_violence", ("遺棄", "棄置", "無自救力", "不履行扶養")),
    ("trafficking", "sexual_child_exploitation", ("人口販運", "強迫勞動", "利用處境剝削")),
    ("juvenile", "specialist_routes", ("少年事件", "未成年觸法", "少年保護事件")),
    ("domestic_violence", "human_violence", ("家庭暴力", "家暴", "違反保護令")),
    ("child_protection", "sexual_child_exploitation", ("兒少保護", "兒童虐待", "兒少受虐")),
    ("gender_equality", "specialist_routes", ("職場性騷擾", "校園性平", "性別平等工作", "性別平等教育")),
]

ROUTE_LABELS = {
    "theft": "竊盜／竊佔",
    "aggravated_theft": "加重竊盜",
    "embezzlement": "侵占",
    "robbery": "強盜／搶奪",
    "damage": "毀損",
    "fraud": "詐欺／背信",
    "injury": "傷害",
    "homicide": "殺人",
    "liberty": "妨害自由／強制",
    "intimidation": "恐嚇",
    "stalking": "跟蹤騷擾",
    "forgery": "偽造文書／印文",
    "defamation": "妨害名譽",
    "privacy": "妨害秘密／性隱私",
    "public_danger": "公共危險／交通",
    "drugs": "毒品",
    "computer": "妨害電腦使用",
    "sexual": "妨害性自主",
    "sexual_harassment": "性騷擾",
    "state_security": "國安與國交",
    "duty": "瀆職",
    "obstruction": "妨害公務",
    "judicial_integrity": "妨害司法公正",
    "voting": "妨害投票",
    "disorder": "妨害秩序",
    "escape": "脫逃／藏匿人犯",
    "evidence": "湮滅／偽造證據",
    "accusation": "偽證／誣告",
    "currency": "偽造貨幣",
    "securities": "偽造有價證券／支付卡",
    "weights_measures": "度量衡",
    "obscenity": "妨害風化",
    "marriage": "妨害婚姻",
    "graves_religion": "褻瀆祀典／墳墓",
    "agriculture_commerce": "妨害農工商",
    "opium": "鴉片",
    "gambling": "賭博",
    "abortion": "墮胎",
    "abandonment": "遺棄",
    "trafficking": "人口販運",
    "juvenile": "少年事件",
    "domestic_violence": "家庭暴力",
    "child_protection": "兒少保護",
    "gender_equality": "性別平等工作／教育",
}

ROUTE_CONTRARY_RULES = {
    "theft": ("沒有拿走", "未拿走", "經所有人同意", "對方同意取走", "同意取走"),
    "aggravated_theft": ("沒有侵入", "未破壞門窗", "沒有攜帶兇器", "沒有結夥"),
    "embezzlement": ("已依約返還", "沒有拒絕返還", "仍依約保管"),
    "robbery": ("沒有使用強暴", "沒有脅迫", "未壓制反抗"),
    "damage": ("物品沒有損壞", "功能未受影響", "經所有人同意處理"),
    "fraud": ("內容均屬真實", "沒有因該內容處分財產"),
    "injury": ("沒有受傷", "傷勢與本案無關"),
    "homicide": ("無人死亡", "死亡與本案無關"),
}

# These hints only prioritize which child-route facts to ask first. They do not
# establish an offense, remove another route, or change candidate scores.
CHILD_ROUTE_RELEVANCE_HINTS = {
    "theft_320_1_movable": ("偷", "竊", "拿走", "取走", "皮夾", "錢包", "手機", "現金", "金融卡", "動產"),
    "theft_320_2_real_estate": ("竊佔", "土地", "房屋", "建物", "不動產"),
    "theft_323_energy": ("電能", "熱能", "瓦斯", "能源", "能量"),
    "theft_324_relative": ("親屬", "配偶", "家人", "家庭成員"),
    "public_danger_185_3_impaired_driving": ("酒駕", "毒駕", "酒測", "呼氣酒精", "血液酒精", "駕駛"),
    "public_danger_185_4_hit_and_run": ("肇事逃逸", "事故後離開", "致人死傷逃逸", "未留在現場"),
    "obstruction_135_violence_threat": ("施暴", "強暴", "脅迫", "攻擊", "推擠", "毆打", "對警察施暴"),
    "obstruction_136_group": ("聚集", "三人以上", "群眾", "在場助勢", "首謀"),
    "obstruction_137_exam_fraud": ("考試", "作弊", "代考", "非法方法"),
    "obstruction_138_official_property": ("公文", "公務文書", "公務物品", "隱匿文書", "毀損文書"),
    "obstruction_139_seal_seizure": ("封印", "查封", "扣押", "封條"),
    "obstruction_140_insult_official": ("侮辱", "辱罵", "髒話", "謾罵", "罵警察", "罵員警"),
    "obstruction_141_public_notice": ("文告", "公告", "公示", "揭示", "布告"),
}

BLOCKED_ROUTE_RULES = [
    ("firearms", "drugs_firearms_organization", "槍砲／彈藥", ("槍砲", "槍枝", "彈藥")),
    ("organized_crime", "drugs_firearms_organization", "組織犯罪", ("組織犯罪", "犯罪組織", "幫派組織")),
    ("money_laundering", "money_flow_laundering_stolen_goods", "洗錢", ("洗錢", "隱匿犯罪所得", "掩飾犯罪所得")),
    ("stolen_goods", "money_flow_laundering_stolen_goods", "贓物", ("贓物", "故買贓物", "收受贓物")),
]


def route_options() -> list[dict[str, str]]:
    supported = [
        {
            "route_id": route_id,
            "label": ROUTE_LABELS[route_id],
            "family_id": family_id,
            "runtime_status": "SUPPORTED_HUMAN_REVIEW_REQUIRED",
        }
        for route_id, family_id, _keywords in ROUTE_RULES
    ]
    blocked = [
        {
            "route_id": route_id,
            "label": label,
            "family_id": family_id,
            "runtime_status": "BLOCKED_NO_FORMAL_CROSSWALK",
        }
        for route_id, family_id, label, _keywords in BLOCKED_ROUTE_RULES
    ]
    return sorted([*supported, *blocked], key=lambda item: (item["label"], item["route_id"]))


def _validate_initial_route(route_id: str) -> str:
    valid = {item["route_id"] for item in route_options()}
    if route_id not in valid:
        raise ValueError("請選擇有效的初始罪章／調查路線")
    return route_id


def _fact(fact_id: str, category: str, value: str, provenance: str, status: str = "FACT", confidence: float = 1.0) -> dict:
    return {
        "fact_id": fact_id, "category": category, "value": value,
        "provenance": provenance, "status": status, "confidence": confidence,
    }


def _source_pack_digest(bank: QuestionBank) -> str:
    return hashlib.sha256(f"{bank.fingerprint}:{bank.template_fingerprint}".encode("utf-8")).hexdigest()


def extract_facts(intake: dict[str, Any]) -> list[dict[str, Any]]:
    summary = intake["summary"].strip()
    facts = [
        _fact("F-TIME", "time", intake["event_time"], "INTAKE:event_time"),
        _fact("F-PLACE", "place", intake["location"], "INTAKE:location"),
        _fact("F-NARRATIVE", "event", summary, "INTAKE:summary"),
    ]
    names = []
    for token in re.findall(r"(?:甲|乙|丙|丁|[A-Z]{1,3}\d{3,})", summary):
        if token not in names:
            names.append(token)
    for index, name in enumerate(names, start=1):
        facts.append(_fact(f"F-PERSON-{index}", "person", name, "INFERENCE:summary-token", "INFERENCE", 0.6))
    if any(word in summary for word in ("手機", "皮夾", "錢包", "金融卡", "現金", "文件", "車輛")):
        facts.append(_fact("F-OBJECT-1", "object", "摘要記載之物品，待逐項確認", "INFERENCE:summary-keyword", "UNKNOWN", 0.4))
    facts.append(_fact("F-CONDUCT", "conduct", "待問答確認具體行為、方式及前後順序", "SYSTEM:GATE1", "UNKNOWN", 0.0))
    facts.append(_fact("F-MENTAL-STATE", "mental_state", "待問答確認行為時認知、目的及可得知事項", "SYSTEM:GATE1", "UNKNOWN", 0.0))
    facts.append(_fact("F-RESULT", "result", "待問答確認實際結果、損害或影響", "SYSTEM:GATE1", "UNKNOWN", 0.0))
    facts.append(_fact("F-RIGHTS", "property_or_rights", "待問答確認所有、持有、授權或其他權利關係", "SYSTEM:GATE1", "UNKNOWN", 0.0))
    facts.append(_fact("F-CAUSATION", "causation", "待問答確認", "SYSTEM:GATE1", "UNKNOWN", 0.0))
    facts.append(_fact("F-EVIDENCE", "evidence", "待問答確認", "SYSTEM:GATE1", "UNKNOWN", 0.0))
    return facts


def _classify_route_element(element: str) -> str:
    rules = (
        ("mental_state", ("意圖", "認識", "知悉", "故意", "預見")),
        ("authorization", ("同意", "授權", "許可")),
        ("evidence", ("證明", "確認", "鑑定", "紀錄", "資料", "狀態")),
        ("result", ("死亡", "重傷", "傷害結果", "損害", "結果", "既遂")),
        ("relationship", ("親屬", "關係", "持有", "職務", "業務")),
        ("object", ("動產", "不動產", "物品", "能量", "年齡", "客體")),
    )
    for element_type, keywords in rules:
        if any(keyword in element for keyword in keywords):
            return element_type
    return "conduct"


def _route_element_key(route_id: str, element: str) -> str:
    digest = hashlib.sha256(element.encode("utf-8")).hexdigest()[:16]
    return f"{route_id}:{digest}"


def analyze_candidates(
    text: str,
    bank: QuestionBank | None = None,
    answered_element_keys: set[str] | None = None,
    disputed_targets: set[str] | None = None,
    selected_route_id: str = "",
) -> list[dict[str, Any]]:
    answered_keys = answered_element_keys or set()
    disputes = disputed_targets or set()
    candidates = []
    for route_id, family_id, keywords in ROUTE_RULES:
        hits = [keyword for keyword in keywords if keyword in text]
        selected = route_id == selected_route_id
        if not hits and not selected:
            continue
        contrary_hits = [keyword for keyword in ROUTE_CONTRARY_RULES.get(route_id, ()) if keyword in text]
        score = max(5, min(95, 35 + len(hits) * 15 + (15 if selected else 0) - len(contrary_hits) * 25))
        child_routes = []
        for child in bank.child_routes(route_id) if bank else []:
            gaps = [
                {
                    "element": element,
                    "element_type": _classify_route_element(element),
                    "route_element_key": _route_element_key(child["route_id"], element),
                    "status": "ANSWERED_PENDING_REVIEW"
                    if _route_element_key(child["route_id"], element) in answered_keys else "UNKNOWN",
                }
                for element in child["fact_elements"]
            ]
            child_routes.append({**child, "status": "NEEDS_FACTS", "element_gaps": gaps})
        unresolved = []
        for child in child_routes:
            for gap in child["element_gaps"]:
                if gap["status"] != "CONFIRMED" and gap["element"] not in unresolved:
                    unresolved.append(gap["element"])
        candidates.append({
            "candidate_id": route_id,
            "family_id": family_id,
            "label": ROUTE_LABELS.get(route_id, route_id),
            "status": "LOWERED" if contrary_hits else ("NEEDS_FACTS" if score < 65 else "CANDIDATE"),
            "score": score,
            "supporting_facts": (["使用者指定的初始調查路線（非犯罪認定）"] if selected else [])
            + [f"文字線索：{item}" for item in hits],
            "contrary_facts": [f"相反文字線索：{item}" for item in contrary_hits]
            + [f"被害人與涉嫌人對 {target} 的陳述不一致" for target in sorted(disputes)],
            "missing_elements": unresolved or ["主觀認知", "行為細節", "證據來源"],
            "child_routes": child_routes,
            "source_status": "HUMAN_REVIEW_REQUIRED",
            "explanation": (
                "依使用者指定的初始調查路線暫列，仍須由後續中性問句確認或排除。"
                if selected else "依已確認文字線索暫列，須由後續中性問句確認或排除。"
            ),
            "selected_by_user": selected,
        })
    for route_id, family_id, label, keywords in BLOCKED_ROUTE_RULES:
        hits = [keyword for keyword in keywords if keyword in text]
        selected = route_id == selected_route_id
        if not hits and not selected:
            continue
        candidates.append({
            "candidate_id": route_id,
            "family_id": family_id,
            "label": label,
            "status": "UNSUPPORTED_ROUTE",
            "score": 0,
            "supporting_facts": (["使用者指定的初始調查路線（非犯罪認定）"] if selected else [])
            + [f"文字線索：{item}" for item in hits],
            "contrary_facts": [],
            "missing_elements": ["正式 parent／child route crosswalk", "現行法與行為時法核對", "專屬問句人工審查"],
            "child_routes": [],
            "source_status": "BLOCKED_NO_FORMAL_CROSSWALK",
            "explanation": "已辨識可能方向，但正式 route crosswalk 尚未核准；禁止產生完整法律路線筆錄。",
            "selected_by_user": selected,
        })
    if not candidates:
        candidates.append({
            "candidate_id": "unclassified",
            "family_id": "specialist_routes",
            "label": "尚待分類",
            "status": "UNSUPPORTED_ROUTE",
            "score": 0,
            "supporting_facts": [],
            "contrary_facts": [],
            "missing_elements": ["行為類型", "客體", "結果", "主觀認知"],
            "child_routes": [],
            "source_status": "HUMAN_REVIEW_REQUIRED",
            "explanation": "現有規則無法安全縮小範圍，需先補充事實。",
        })
    return sorted(candidates, key=lambda item: (-item["score"], item["candidate_id"]))


def make_case(raw: dict[str, Any], bank: QuestionBank) -> dict[str, Any]:
    event_time = str(raw.get("event_time", "")).strip()
    location = str(raw.get("location", "")).strip()
    summary = str(raw.get("summary", "")).strip()
    if not event_time or not location or not summary:
        raise ValueError("發生／破獲時間、地點及案情摘要均為必填")
    case_kind = raw.get("case_kind")
    if case_kind not in {"WITH_VICTIM", "NO_VICTIM"}:
        raise ValueError("case_kind 必須為 WITH_VICTIM 或 NO_VICTIM")
    initial_route_id = str(raw.get("initial_route_id", "")).strip()
    if case_kind == "NO_VICTIM":
        if not initial_route_id:
            raise ValueError("無被害人／移送案件必須由使用者指定初始罪章／調查路線")
        _validate_initial_route(initial_route_id)
    elif initial_route_id:
        _validate_initial_route(initial_route_id)
    intake = {
        "event_time": event_time,
        "location": location,
        "summary": summary,
        "case_kind": case_kind,
        "notes": str(raw.get("notes", "")).strip(),
        "initial_route_id": initial_route_id,
    }
    candidates = analyze_candidates(summary, bank, selected_route_id=initial_route_id)
    role = "victim" if case_kind == "WITH_VICTIM" else "suspect"
    source_pack_digest = _source_pack_digest(bank)
    case = {
        "schema_version": SCHEMA_VERSION,
        "case_id": str(uuid4()),
        "state": "GATE1_REVIEW",
        "intake": intake,
        "facts": extract_facts(intake),
        "candidates": candidates,
        "element_gaps": _element_gaps(candidates),
        "active_role": role,
        "question_batches": [],
        "answers": {"victim": {}, "suspect": {}, "witness": {}},
        "case_numbers": {},
        "approvals": {},
        "documents": [],
        "disputed_facts": [],
        "source_pack_digest": source_pack_digest,
        "source_pins": {"question_bank": bank.fingerprint, "company_templates": bank.template_fingerprint},
        "warnings": ["候選罪章是待查證假設，不是法律結論。"],
    }
    case["next_question_batch"] = plan_next_batch(case, bank)
    return case


def _element_gaps(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gaps = []
    for candidate in candidates:
        if candidate.get("child_routes"):
            for child in candidate["child_routes"]:
                for gap in child["element_gaps"]:
                    gaps.append({
                        "candidate_id": candidate["candidate_id"],
                        "child_route_id": child["route_id"],
                        "child_route_name": child["name"],
                        **gap,
                    })
        else:
            gaps.extend(
                {"candidate_id": candidate["candidate_id"], "element": gap, "element_type": "UNKNOWN", "status": "UNKNOWN"}
                for gap in candidate["missing_elements"]
            )
    return gaps


def _answered_element_keys(case: dict[str, Any]) -> set[str]:
    answered_keys = set()
    for batch in case.get("question_batches", []):
        answered_ids = set(batch.get("answered_question_ids", []))
        for question in batch.get("questions", []):
            if question.get("question_id") in answered_ids:
                answered_keys.update(question.get("route_element_keys", []))
    return answered_keys


def _case_question_context(case: dict[str, Any]) -> str:
    return " ".join([
        case.get("intake", {}).get("summary", ""),
        case.get("intake", {}).get("notes", ""),
        *(
            str(answer)
            for role_answers in case.get("answers", {}).values()
            for answer in role_answers.values()
        ),
    ])


def _child_route_relevance(text: str, child: dict[str, Any]) -> int:
    hints = CHILD_ROUTE_RELEVANCE_HINTS.get(child["route_id"], ())
    matched_hints = {hint for hint in hints if hint in text}
    score = len(matched_hints) * 100
    if child.get("name") and child["name"] in text:
        score += 50
    score += sum(20 for element in child.get("element_gaps", []) if element.get("element") in text)
    return score


def _route_element_questions(case: dict[str, Any]) -> list[dict[str, Any]]:
    role = case["active_role"]
    context = _case_question_context(case)
    grouped: dict[str, dict[str, Any]] = {}
    for candidate_order, candidate in enumerate(case.get("candidates", [])):
        children = candidate.get("child_routes", [])
        child_priorities = [_child_route_relevance(context, child) for child in children]
        if len(children) == 1 and child_priorities:
            child_priorities[0] = max(1, child_priorities[0])
        highest_priority = max(child_priorities, default=0)
        for child_order, child in enumerate(children):
            route_priority = child_priorities[child_order]
            relevant_route = route_priority > 0 and route_priority == highest_priority
            for element_order, gap in enumerate(child.get("element_gaps", [])):
                if gap.get("status") != "UNKNOWN":
                    continue
                element = str(gap["element"])
                route_element_key = gap.get("route_element_key") or _route_element_key(child["route_id"], element)
                item = grouped.setdefault(element, {
                    "keys": [],
                    "route_ids": [],
                    "routes": [],
                    "element_type": gap.get("element_type", "UNKNOWN"),
                    "route_priority": route_priority,
                    "candidate_order": candidate_order,
                    "child_order": child_order,
                    "element_order": element_order,
                    "required_for_relevant_route": relevant_route,
                })
                item["keys"].append(route_element_key)
                item["route_ids"].append(child["route_id"])
                item["routes"].append(child["name"])
                item["required_for_relevant_route"] = item["required_for_relevant_route"] or relevant_route
                ranking = (route_priority, -candidate_order, -child_order, -element_order)
                current_ranking = (
                    item["route_priority"],
                    -item["candidate_order"],
                    -item["child_order"],
                    -item["element_order"],
                )
                if ranking > current_ranking:
                    item.update({
                        "route_priority": route_priority,
                        "candidate_order": candidate_order,
                        "child_order": child_order,
                        "element_order": element_order,
                    })
    prompts = {
        "victim": "關於「{element}」這一事項，請說明你親自經歷或知道的具體情形？",
        "suspect": "關於「{element}」這一事項，請說明實際情形及你當時的認知？",
        "witness": "關於「{element}」這一事項，請說明你親自看到、聽到或得知的具體情形？",
    }
    questions = []
    for element, item in grouped.items():
        digest = hashlib.sha256(f"{role}\0{element}".encode("utf-8")).hexdigest()[:16]
        questions.append({
            "question_id": f"R-{role.upper()}-{digest}",
            "text": prompts[role].format(element=element),
            "role": role,
            "family_id": "route_element_supplement",
            "fact_target": item["element_type"],
            "element_type": item["element_type"],
            "layer": "element_supplement",
            "requirement": "REQUIRED" if item["required_for_relevant_route"] else "CONDITIONAL",
            "legal_review_status": "HUMAN_REVIEW_REQUIRED",
            "runtime_status": "AVAILABLE_WITH_WARNING",
            "route_element": element,
            "route_element_keys": sorted(set(item["keys"])),
            "route_ids": sorted(set(item["route_ids"])),
            "route_names": sorted(set(item["routes"])),
            "route_priority": item["route_priority"],
            "candidate_order": item["candidate_order"],
            "child_order": item["child_order"],
            "element_order": item["element_order"],
            "template_binding": "NONE",
        })
    return sorted(questions, key=lambda item: (
        -item["route_priority"],
        item["candidate_order"],
        item["child_order"],
        item["element_order"],
        item["question_id"],
    ))


def _disputed_facts(case: dict[str, Any]) -> list[dict[str, Any]]:
    statements: dict[str, dict[str, list[str]]] = {"victim": {}, "suspect": {}}
    for batch in case.get("question_batches", []):
        role = batch.get("role")
        if role not in statements:
            continue
        answered_ids = set(batch.get("answered_question_ids", []))
        for question in batch.get("questions", []):
            question_id = question.get("question_id")
            target = question.get("fact_target")
            answer = case.get("answers", {}).get(role, {}).get(question_id)
            if question_id in answered_ids and target and answer:
                statements[role].setdefault(target, []).append(str(answer).strip())
    disputes = []
    for target in sorted(set(statements["victim"]) & set(statements["suspect"])):
        victim_values = statements["victim"][target]
        suspect_values = statements["suspect"][target]
        if {re.sub(r"\s+", "", value) for value in victim_values} == {re.sub(r"\s+", "", value) for value in suspect_values}:
            continue
        disputes.append({
            "fact_target": target,
            "status": "DISPUTED",
            "victim_statements": victim_values,
            "suspect_statements": suspect_values,
            "note": "僅標示雙方陳述不一致，不判定任一方陳述為真。",
        })
    return disputes


def _active_preconditions(case: dict[str, Any]) -> set[str]:
    text = " ".join([
        case["intake"].get("summary", ""),
        case["intake"].get("notes", ""),
        *(answer for role_answers in case.get("answers", {}).values() for answer in role_answers.values()),
    ])
    routes = {candidate["candidate_id"] for candidate in case.get("candidates", [])}
    active = {"NONE"}
    keyword_conditions = {
        "DOMESTIC_RELATIONSHIP_CONFIRMED": ("家暴", "家庭", "配偶", "同居", "親密關係"),
        "MINOR_INVOLVED_CONFIRMED": ("未滿18", "未滿 18", "兒童", "少年", "兒少", "未成年"),
        "INTERPRETER_NEED_CONFIRMED": ("通譯", "翻譯", "手語", "不懂中文", "溝通障礙"),
        "NIGHT_INTERVIEW_CONFIRMED": ("夜間詢問", "夜間製作筆錄"),
        "RECORDING_INTERRUPTION_CONFIRMED": ("錄音中斷", "錄影中斷", "未全程錄音", "未全程錄影"),
        "WORK_OR_EDUCATION_CONTEXT": ("職場", "工作場所", "學校", "校園", "教育場所"),
    }
    for condition, keywords in keyword_conditions.items():
        if any(keyword in text for keyword in keywords):
            active.add(condition)
    if routes.intersection({"sexual", "sexual_harassment", "child_protection", "trafficking"}):
        active.add("SEXUAL_CASE_ROUTE")
    if "stalking" in routes:
        active.add("STALKING_ROUTE")
    if re.search(r"(?<![A-Za-z0-9])[A-Za-z]{1,3}\d{6,}(?![A-Za-z0-9])", text):
        active.add("CODED_VICTIM_CONFIRMED")
    if case.get("disputed_facts"):
        active.add("ROLE_DISCREPANCY_PRESENT")
    return active


def _available_questions(case: dict[str, Any], bank: QuestionBank) -> list[dict[str, Any]]:
    role = case["active_role"]
    family_ids = sorted({item["family_id"] for item in case["candidates"]})
    route_ids = [item["candidate_id"] for item in case["candidates"] if item["candidate_id"] != "unclassified"]
    template_role = "transfer" if case["intake"]["case_kind"] == "NO_VICTIM" else role
    return bank.template_questions(template_role) + bank.questions(
        role=role,
        family_ids=family_ids,
        route_ids=route_ids,
        active_preconditions=_active_preconditions(case),
    ) + _route_element_questions(case)


def plan_next_batch(case: dict[str, Any], bank: QuestionBank, max_size: int = 5) -> list[dict[str, Any]]:
    role = case["active_role"]
    answered = set(case.get("answers", {}).get(role, {}))
    questions = _available_questions(case, bank)
    required_ids = {item["question_id"] for item in questions if item["requirement"] == "REQUIRED"}
    case["gate2_required_remaining"] = len(required_ids - answered)
    unresolved_types = {
        gap.get("element_type") for gap in case.get("element_gaps", [])
        if gap.get("status") == "UNKNOWN" and gap.get("element_type") not in {None, "UNKNOWN"}
    }
    def phase(item: dict[str, Any]) -> int:
        target = item.get("fact_target")
        if item["layer"] == "company_template":
            binding = item.get("template_binding", {})
            order = binding.get("order", 999) if isinstance(binding, dict) else 999
            return 0 if order <= 3 else 5
        if target in {"rights_notice", "identity", "witness_basis"}:
            return 0
        if target == "free_narrative":
            return 1
        if item["layer"] == "family_skeleton":
            return 2
        if item["layer"] == "element_supplement" and item["requirement"] == "REQUIRED":
            return 3
        if item.get("route_element_keys"):
            return 3
        if item["layer"] == "conditional_module":
            return 4
        if target in {"evidence", "knowledge_basis", "hearsay_source", "exculpatory_evidence"}:
            return 6
        if target == "closing":
            return 9
        return 7
    questions.sort(key=lambda item: (
        phase(item),
        0 if item["requirement"] == "REQUIRED" else 1,
        0 if item.get("element_type") in unresolved_types else 1,
        -item.get("route_priority", 0),
        item.get("candidate_order", 999),
        item.get("child_order", 999),
        item.get("element_order", 999),
        item.get("template_binding", {}).get("order", 999)
        if isinstance(item.get("template_binding"), dict) else 999,
        item["question_id"],
    ))
    batch = []
    for question in questions:
        if question["question_id"] in answered:
            continue
        batch.append({
            "question_id": question["question_id"],
            "text": question["text"],
            "role": question["role"],
            "family_id": question["family_id"],
            "fact_target": question["fact_target"],
            "element_type": question.get("element_type", "UNKNOWN"),
            "layer": question["layer"],
            "requirement": question["requirement"],
            "legal_review_status": question["legal_review_status"],
            "template_binding": question.get("template_binding", "NONE"),
            "route_element": question.get("route_element", ""),
            "route_element_keys": list(question.get("route_element_keys", [])),
            "route_ids": list(question.get("route_ids", [])),
            "route_names": list(question.get("route_names", [])),
            "route_priority": question.get("route_priority", 0),
            "why": (
                f"對應候選子路線的具體事實缺口：{question['route_element']}。回答只用於確認或排除候選，不代表罪名成立。"
                if question.get("route_element_keys")
                else f"補充 {question['fact_target']} 事實，對應目前尚未確認的 {question.get('element_type', 'UNKNOWN')} 要件缺口。"
                if question.get("element_type") in unresolved_types
                else f"補充 {question['fact_target']} 事實，供候選方向交叉檢查。"
            ),
        })
        if len(batch) >= max_size:
            break
    return batch


def confirm_gate1(case: dict[str, Any], bank: QuestionBank) -> dict[str, Any]:
    if case["intake"]["case_kind"] == "NO_VICTIM" and not case["intake"].get("initial_route_id"):
        raise ValueError("無被害人／移送案件必須先指定初始罪章／調查路線")
    analysis_text = " ".join([case["intake"]["summary"], *(fact["value"] for fact in case.get("facts", []))])
    case["candidates"] = analyze_candidates(
        analysis_text, bank, selected_route_id=case["intake"].get("initial_route_id", "")
    )
    case["element_gaps"] = _element_gaps(case["candidates"])
    case["state"] = "GATE5_QA" if case["intake"]["case_kind"] == "NO_VICTIM" else "GATE2_QA"
    case["approvals"]["gate1"] = {"status": "USER_FACT_CONFIRMED", "basis_digest": case.get("basis_digest", "PENDING")}
    case["next_question_batch"] = plan_next_batch(case, bank)
    return case


def update_gate1_facts(case: dict[str, Any], payload: dict[str, Any], bank: QuestionBank) -> dict[str, Any]:
    if case.get("state") != "GATE1_REVIEW":
        raise ValueError("只有 Gate 1 可修正拆解事實")
    incoming = payload.get("facts")
    if not isinstance(incoming, dict) or not incoming:
        raise ValueError("facts 必須是非空物件")
    by_id = {fact["fact_id"]: fact for fact in case.get("facts", [])}
    editable = {fact_id for fact_id, fact in by_id.items() if fact.get("status") != "FACT"}
    if not set(incoming).issubset(editable):
        raise ValueError("只能修正 Gate 1 的推論或未知事實")
    changed_count = 0
    for fact_id, raw_value in incoming.items():
        value = str(raw_value).strip()
        if not value:
            raise ValueError(f"{fact_id} 的修正內容不得空白")
        if value == str(by_id[fact_id].get("value", "")).strip():
            continue
        by_id[fact_id].update({
            "value": value,
            "provenance": "USER:GATE1_CORRECTION",
            "status": "USER_CONFIRMED",
            "confidence": 1.0,
        })
        changed_count += 1
    if changed_count == 0:
        raise ValueError("沒有可儲存的事實變更")
    analysis_text = " ".join([case["intake"]["summary"], *(fact["value"] for fact in case["facts"])])
    case["candidates"] = analyze_candidates(
        analysis_text, bank, selected_route_id=case["intake"].get("initial_route_id", "")
    )
    case["element_gaps"] = _element_gaps(case["candidates"])
    case["approvals"] = {}
    case["case_numbers"] = {}
    case["documents"] = []
    case["disputed_facts"] = []
    case["next_question_batch"] = plan_next_batch(case, bank)
    return case


def confirm_answers(case: dict[str, Any], payload: dict[str, Any], bank: QuestionBank) -> dict[str, Any]:
    role = case["active_role"]
    incoming = payload.get("answers")
    if not isinstance(incoming, dict) or not incoming:
        raise ValueError("answers 必須是非空物件")
    expected = {item["question_id"] for item in case.get("next_question_batch", [])}
    if not set(incoming).issubset(expected):
        raise ValueError("答案包含目前批次以外的 question_id")
    for question_id, value in incoming.items():
        text = str(value).strip()
        if not text:
            raise ValueError(f"{question_id} 的答案不得空白")
        case["answers"][role][question_id] = text
        question = next(item for item in case.get("next_question_batch", []) if item["question_id"] == question_id)
        fact_id = f"F-ANSWER-{role.upper()}-{question_id}"
        case["facts"] = [fact for fact in case.get("facts", []) if fact["fact_id"] != fact_id]
        case["facts"].append(_fact(
            fact_id,
            question.get("element_type", question.get("fact_target", "statement")),
            text,
            f"ANSWER:{role}:{question_id}",
            "STATEMENT",
            1.0,
        ))
    case.setdefault("question_batches", []).append({
        "role": role,
        "confirmed": True,
        "questions": deepcopy(case.get("next_question_batch", [])),
        "answered_question_ids": sorted(incoming),
    })
    combined = case["intake"]["summary"] + " " + " ".join(
        answer for answers in case["answers"].values() for question_id, answer in answers.items()
        if not question_id.startswith("T-")
    )
    case["disputed_facts"] = _disputed_facts(case)
    case["candidates"] = analyze_candidates(
        combined,
        bank,
        _answered_element_keys(case),
        {item["fact_target"] for item in case["disputed_facts"]},
        case["intake"].get("initial_route_id", ""),
    )
    case["element_gaps"] = _element_gaps(case["candidates"])
    for approval_id in ("gate2:victim", "gate4:suspect", "gate5:suspect", "output"):
        case["approvals"].pop(approval_id, None)
    case["approvals"].pop("output", None)
    case["documents"] = []
    case["next_question_batch"] = plan_next_batch(case, bank)
    if not case["next_question_batch"]:
        case["state"] = "GATE2_REVIEW"
    return case


def update_confirmed_answers(case: dict[str, Any], payload: dict[str, Any], bank: QuestionBank) -> dict[str, Any]:
    role = case["active_role"]
    incoming = payload.get("answers")
    if not isinstance(incoming, dict) or not incoming:
        raise ValueError("answers 必須是非空物件")
    existing = case.get("answers", {}).get(role, {})
    if not set(incoming).issubset(existing):
        raise ValueError("只能修改目前角色已確認的回答")
    question_lookup = {
        item["question_id"]: item
        for batch in case.get("question_batches", []) if batch.get("role") == role
        for item in batch.get("questions", [])
    }
    changed = 0
    for question_id, raw_value in incoming.items():
        value = str(raw_value).strip()
        if not value:
            raise ValueError(f"{question_id} 的答案不得空白")
        if value == str(existing[question_id]).strip():
            continue
        existing[question_id] = value
        question = question_lookup.get(question_id)
        if question is None:
            raise ValueError(f"找不到 {question_id} 的問句版本")
        fact_id = f"F-ANSWER-{role.upper()}-{question_id}"
        case["facts"] = [fact for fact in case.get("facts", []) if fact["fact_id"] != fact_id]
        case["facts"].append(_fact(
            fact_id,
            question.get("element_type", question.get("fact_target", "statement")),
            value,
            f"ANSWER:{role}:{question_id}",
            "STATEMENT",
            1.0,
        ))
        changed += 1
    if changed == 0:
        raise ValueError("沒有可儲存的回答變更")
    combined = case["intake"]["summary"] + " " + " ".join(
        answer for role_answers in case["answers"].values() for question_id, answer in role_answers.items()
        if not question_id.startswith("T-")
    )
    case["disputed_facts"] = _disputed_facts(case)
    case["candidates"] = analyze_candidates(
        combined,
        bank,
        _answered_element_keys(case),
        {item["fact_target"] for item in case["disputed_facts"]},
        case["intake"].get("initial_route_id", ""),
    )
    case["element_gaps"] = _element_gaps(case["candidates"])
    case["approvals"] = {}
    case["case_numbers"] = {}
    case["documents"] = []
    if case["intake"]["case_kind"] == "NO_VICTIM":
        case["state"] = "GATE5_QA"
    elif role == "suspect":
        case["state"] = "GATE4_QA"
    else:
        case["state"] = "GATE2_QA"
    case["next_question_batch"] = plan_next_batch(case, bank)
    return case


def complete_gate2(case: dict[str, Any], bank: QuestionBank) -> dict[str, Any]:
    role_answers = case["answers"][case["active_role"]]
    if len(role_answers) < 5:
        raise ValueError("至少完成第一批中性問句後才能結束 Gate 2")
    unsupported = [item["label"] for item in case["candidates"] if item["status"] == "UNSUPPORTED_ROUTE"]
    if unsupported:
        raise ValueError(f"候選方向尚未具備正式 route 支援，禁止產生完整筆錄：{'、'.join(unsupported)}")
    required_ids = {
        item["question_id"] for item in _available_questions(case, bank)
        if item["requirement"] == "REQUIRED"
    }
    remaining = sorted(required_ids - set(role_answers))
    case["gate2_required_remaining"] = len(remaining)
    if remaining:
        raise ValueError(f"尚有 {len(remaining)} 題必要問句未完成，不能結束目前 Gate")
    case["state"] = "OUTPUT_READY" if case.get("case_numbers") else "CASE_NUMBERS"
    if case["intake"]["case_kind"] == "NO_VICTIM":
        approval_id = "gate5:suspect"
    elif case["active_role"] == "suspect":
        approval_id = "gate4:suspect"
    else:
        approval_id = "gate2:victim"
    case["approvals"][approval_id] = {"status": "AI_REVIEWED", "basis_digest": case.get("basis_digest", "PENDING")}
    return case


def required_case_numbers(case: dict[str, Any]) -> dict[str, bool]:
    summary = case["intake"]["summary"]
    routes = {candidate["candidate_id"] for candidate in case["candidates"]}
    coded_victim = bool(re.search(r"(?<![A-Za-z0-9])[A-Za-z]{1,4}\d{6,}(?![A-Za-z0-9])", summary))
    return {"proof_number": True, "women_child_number": coded_victim, "case_165_number": "fraud" in routes}


def set_case_numbers(case: dict[str, Any], numbers: dict[str, Any]) -> dict[str, Any]:
    required = required_case_numbers(case)
    cleaned = {}
    for key, is_required in required.items():
        value = str(numbers.get(key, "")).strip()
        if is_required and not value:
            raise ValueError(f"{key} 為必填")
        if value:
            cleaned[key] = value
    case["case_numbers"] = cleaned
    case["state"] = "OUTPUT_READY"
    return case


def start_suspect(case: dict[str, Any], bank: QuestionBank, *, transfer: bool = False) -> dict[str, Any]:
    if transfer and case["intake"]["case_kind"] != "NO_VICTIM":
        raise ValueError("移送分支只適用無被害人案件")
    if not transfer and case["intake"]["case_kind"] != "WITH_VICTIM":
        raise ValueError("涉嫌人續辦只適用有被害人案件")
    case["active_role"] = "suspect"
    case["state"] = "GATE5_QA" if transfer else "GATE4_QA"
    case["next_question_batch"] = plan_next_batch(case, bank)
    case["approvals"].pop("gate4:suspect", None)
    case["approvals"].pop("output", None)
    case["documents"] = []
    return case


def update_intake(case: dict[str, Any], raw: dict[str, Any], bank: QuestionBank) -> dict[str, Any]:
    intake = deepcopy(case["intake"])
    for field in ("event_time", "location", "summary", "notes", "initial_route_id"):
        if field in raw:
            intake[field] = str(raw[field]).strip()
    if not intake["event_time"] or not intake["location"] or not intake["summary"]:
        raise ValueError("時間、地點及摘要不得空白")
    if intake["case_kind"] == "NO_VICTIM":
        if not intake.get("initial_route_id"):
            raise ValueError("無被害人／移送案件必須由使用者指定初始罪章／調查路線")
        _validate_initial_route(intake["initial_route_id"])
    case["intake"] = intake
    case["facts"] = extract_facts(intake)
    case["candidates"] = analyze_candidates(
        intake["summary"], bank, selected_route_id=intake.get("initial_route_id", "")
    )
    case["element_gaps"] = _element_gaps(case["candidates"])
    case["answers"] = {"victim": {}, "suspect": {}, "witness": {}}
    case["approvals"] = {}
    case["case_numbers"] = {}
    case["documents"] = []
    case["disputed_facts"] = []
    case["state"] = "GATE1_REVIEW"
    case["next_question_batch"] = plan_next_batch(case, bank)
    return case


def rebase_source_pack(case: dict[str, Any], bank: QuestionBank) -> dict[str, Any]:
    update_intake(case, {}, bank)
    case["source_pack_digest"] = _source_pack_digest(bank)
    case["source_pins"] = {
        "question_bank": bank.fingerprint,
        "company_templates": bank.template_fingerprint,
    }
    case["warnings"].append("來源版本已更新；舊問答、核准與文件均已失效，請重新確認 Gate 1。")
    return case


def add_attachment_metadata(case: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    required = {"attachment_id", "filename", "sha256", "size", "storage_name"}
    if set(metadata) != required:
        raise ValueError("附件 metadata 欄位不完整")
    if not isinstance(metadata["size"], int) or metadata["size"] <= 0:
        raise ValueError("附件大小不合法")
    attachments = case.setdefault("attachments", [])
    if any(item["attachment_id"] == metadata["attachment_id"] for item in attachments):
        raise ValueError("attachment_id 重複")
    attachments.append(dict(metadata))
    case["approvals"] = {}
    case["documents"] = []
    case["state"] = "GATE1_REVIEW"
    return case
