"""隔離驗證 legal-case-web 的事實／候選／問句契約。

執行：在 legal-case-web 目錄執行 `python tools/validate_pipeline_contract.py`。
本腳本不連線資料庫、LLM、HTTP 或雲端，也不寫入工作樹。
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.workflow import apply_action, create_case  # noqa: E402
from tests.helpers import BANK  # noqa: E402


BASE = (
    "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁；"
    "目前未確認甲是否仍能實際支配手機。乙承認拿取手機離開，"
    "表示自己以為手機是他人遺留、不要的物品；尚未確認乙是否具有不法所有意圖，"
    "手機目前尚未尋獲。"
)


def validate() -> dict[str, object]:
    case = create_case({"summary": BASE, "has_victim": True}, BANK)
    facts = case.get("gate1", {}).get("facts", [])
    candidates = case.get("candidates", [])
    assert facts, "Gate 1 facts must not be empty"
    assert all(item.get("assertion_class") in {"ASSERTED", "ADMITTED", "DENIED", "INFERRED", "UNKNOWN"} for item in facts)
    assert all("provenance" in item for item in facts)
    assert all("candidate_status" in item and "readiness_status" in item for item in candidates)
    prepared = apply_action(case, "auto_prepare", {}, BANK)
    assert all("contract" in item for item in prepared.get("questions", []))
    return {
        "case_id_present": bool(case.get("case_id")),
        "fact_count": len(facts),
        "candidate_ids": [item.get("id") for item in candidates],
        "candidate_readiness": [item.get("readiness_status") for item in candidates],
        "question_count": len(prepared.get("questions", [])),
        "external_services": "NOT_USED",
    }


if __name__ == "__main__":
    try:
        print(json.dumps({"status": "PASS", **validate()}, ensure_ascii=False, indent=2))
    except Exception as exc:  # pragma: no cover - command-line failure surface
        print(json.dumps({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
