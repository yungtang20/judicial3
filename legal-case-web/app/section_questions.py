"""區段感知的 Markdown 問句解析。

questions/*.md 問句段位階（docs/QUESTION_DESIGN_AND_USE.md 第六節優先序）：
  core（核心問句）→ evidence_gap（補充問句，查證身分、文件與來源）
  → reinforce（補強問句，佐證與後續）→ distinguishing（區分問句）
  → aggravating（加重問句）→ precedent（判決／函示爭點問句）
"""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path
from typing import Any


QUESTION_RE = re.compile(
    r"^\s*-\s+\*\*(?P<id>[A-Z0-9]+(?:-[A-Z0-9]+)+)\*\*"
    r"(?:（[^）]*）)?：(?P<text>.+?)\s*$"
)

SECTION_MAP: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("core", ("核心問句", "預備問句")),
    ("evidence_gap", ("補充問句",)),
    ("reinforce", ("補強問句",)),
    ("distinguishing", ("區分問句",)),
    ("aggravating", ("加重問句",)),
    ("precedent", ("判決爭點問句", "實務爭點問句", "函示爭點問句")),
)

SECTION_PRIORITY: dict[str, int] = {
    "core": 1,
    "evidence_gap": 2,
    "reinforce": 3,
    "distinguishing": 4,
    "aggravating": 5,
    "precedent": 6,
}

# 題庫的固定分層契約。這裡只描述「問句應放在哪一層」及其審核狀態，
# 不替任何罪章補寫未經查證的法律見解。
QUESTION_LAYER_CONTRACT_VERSION = "question-layers-v1"
QUESTION_LAYER_LABELS: dict[str, str] = {
    "core": "核心問句",
    "evidence_gap": "證據／資料補充問句",
    "reinforce": "補強問句",
    "distinguishing": "罪名區分問句",
    "aggravating": "加重構成要件問句",
    "precedent": "判決／函示爭點問句",
}


def _section_of(heading: str) -> str | None:
    for section, keywords in SECTION_MAP:
        if any(word in heading for word in keywords):
            return section
    return None


def _role_for_heading(heading: str) -> str:
    if any(word in heading for word in ("涉嫌人", "行為人", "相對人端")):
        return "suspect"
    if any(word in heading for word in ("被害人", "告訴人", "舉發人", "機關端", "執行單位端")):
        return "victim"
    if "證人" in heading:
        return "witness"
    return "both"


def read_section_questions(path: Path) -> dict[str, dict[str, list[dict[str, str]]]]:
    """回傳 {role: {section: [question]}}。question 具 id 與 text。"""
    result: dict[str, dict[str, list[dict[str, str]]]] = {
        "victim": {name: [] for name, _ in SECTION_MAP},
        "suspect": {name: [] for name, _ in SECTION_MAP},
        "transfer": {name: [] for name, _ in SECTION_MAP},
        # 證人尚非 runtime 角色。保留供人工審查，但 flatten_sections 不得接線。
        "witness_review_only": {name: [] for name, _ in SECTION_MAP},
    }
    role_scope = "both"
    role_scope_level = 0
    section: str | None = None
    seen: set[tuple[str, str]] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            heading_match = re.match(r"^(?P<marks>#+)\s*(?P<title>.*)$", line)
            if heading_match is None:
                continue
            level = len(heading_match.group("marks"))
            new_heading = heading_match.group("title").strip()
            new_role = _role_for_heading(new_heading)
            if new_role != "both":
                role_scope = new_role
                role_scope_level = level
            elif role_scope_level and level <= role_scope_level + 1:
                role_scope = "both"
                role_scope_level = 0
            section = _section_of(new_heading)
            continue
        match = QUESTION_RE.match(line)
        if not match:
            continue
        text = match.group("text").strip()
        # 一題一事項由題庫審核（docs/QUESTION_DESIGN_AND_USE.md）把關；
        # 此處只排除明顯雜訊，
        # 不再以「？」數量丟題——公司核定套表題常含合法的子問（例：竊盜 T-N-05）。
        if not text or len(text) < 8:
            continue
        resolved = section if section is not None else _section_by_id(match.group("id"))
        if resolved is None:
            continue
        role = role_scope
        if role == "witness":
            roles = ("witness_review_only",)
        elif role == "suspect":
            roles = ("suspect", "transfer")
        elif role == "victim":
            roles = ("victim",)
        else:
            # 沒有角色標題的舊小罪章檔不得再把同一題複製給所有角色。
            # N=涉嫌人、W=證人；其餘先歸被害／權利受影響端，待 Human Gate
            # 補上明確角色章節後再擴充。
            id_code = match.group("id").split("-")[1][:1]
            roles = (
                ("suspect", "transfer") if id_code == "N"
                else (("witness_review_only",) if id_code == "W" else ("victim",))
            )
        for target in roles:
            key = (target, text)
            if key in seen:
                continue
            seen.add(key)
            result[target][resolved].append({"id": match.group("id"), "text": text})
    return result


_ID_CODES: dict[str, tuple[str, ...]] = {
    "core": ("C", "N", "W", "P"),
    "evidence_gap": ("S",),
    "reinforce": ("R",),
    "distinguishing": ("D",),
    "aggravating": ("A",),
    "precedent": ("J",),
}


def _section_by_id(question_id: str) -> str | None:
    segments = question_id.split("-")
    if len(segments) < 2:
        return None
    code = segments[1][:1]
    for section, codes in _ID_CODES.items():
        if code in codes:
            return section
    return None


def build_question_layer_coverage(
    offenses: list[dict[str, Any]],
) -> dict[str, Any]:
    """建立全庫分層覆蓋表，供 UI／人工審查使用。

    ``precedent`` 是可選但高風險的人工審查層；沒有該層時標示
    ``NOT_PROVIDED``，不自動產生題目，也不把缺口誤報成「已完成」。
    ``core`` 是 runtime 最低要求，缺少時標示 ``MISSING_REQUIRED``。
    """
    coverage: dict[str, Any] = {}
    for offense in offenses:
        sections = offense.get("section_questions", {})
        layers: dict[str, Any] = {}
        for layer in QUESTION_LAYER_LABELS:
            count = sum(
                len(sections.get(role, {}).get(layer, []))
                for role in ("victim", "suspect", "transfer", "witness_review_only")
            )
            if layer == "core":
                status = "READY" if count else "MISSING_REQUIRED"
            else:
                status = "READY" if count else "NOT_PROVIDED"
            layers[layer] = {
                "label": QUESTION_LAYER_LABELS[layer],
                "question_count": count,
                "status": status,
                "human_review_required": True,
            }
        missing = [
            layer for layer, item in layers.items()
            if item["status"] in {"MISSING_REQUIRED", "NOT_PROVIDED"}
        ]
        coverage[offense["id"]] = {
            "offense_id": offense["id"],
            "question_source": offense.get("question_source", ""),
            "layers": layers,
            "missing_layers": missing,
            "status": "READY_WITH_GAPS" if missing else "READY",
            "human_review_required": True,
        }
    return {
        "contract_version": QUESTION_LAYER_CONTRACT_VERSION,
        "layer_order": list(QUESTION_LAYER_LABELS),
        "layers": deepcopy(QUESTION_LAYER_LABELS),
        "offenses": coverage,
    }


def ordered_section_questions(
    sections: dict[str, list[dict[str, str]]],
    role: str,
    offense_id: str,
    offense_name: str,
    source: dict[str, Any],
    *,
    max_questions: int | None = None,
) -> list[dict[str, Any]]:
    """依核心→補充→補強→區分→加重→判決爭點順序展開為問句物件。"""
    kind_by_section = {
        "core": "core",
        "evidence_gap": "supplemental",
        "reinforce": "reinforce",
        "distinguishing": "distinguishing",
        "aggravating": "aggravating",
        "precedent": "precedent",
    }
    questions: list[dict[str, Any]] = []
    for section, _ in SECTION_MAP:
        for raw in sections.get(section, []):
            if max_questions is not None and len(questions) >= max_questions:
                return questions
            questions.append({
                "id": f"{role[0].upper()}-{offense_id}-{raw['id']}",
                "text": raw["text"],
                "kind": kind_by_section[section],
                "section": section,
                "priority": SECTION_PRIORITY[section],
                "role": role,
                "offense_id": offense_id,
                "offense_name": offense_name,
                "source": deepcopy(source),
                "question_layer": section,
                "source_citation": _source_citation(raw["text"]),
                "human_review_required": True,
                "status": "PENDING",
                "answer": "",
            })
    return questions


def _source_citation(text: str) -> str:
    """擷取題目末尾的來源標記；沒有標記就保留空字串供人工補查。"""
    match = re.search(r"（來源：([^）]+)）", text)
    return match.group(1).strip() if match else ""
