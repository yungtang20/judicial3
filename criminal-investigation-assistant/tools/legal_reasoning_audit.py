"""Deterministic, offline audit for the lost-phone legal-reasoning scenarios."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain import confirm_answers, confirm_gate1, make_case, update_gate1_facts  # noqa: E402
from app.question_bank import QuestionBank  # noqa: E402


SUMMARY = (
    "甲將手機放在便利商店櫃檯旁，乙拿起手機離開。甲表示手機是自己的；"
    "乙稱以為手機是別人遺留、不要的物品。手機當時是否仍在甲的持有範圍、"
    "乙的認知及其不法所有意圖均未確認。"
)


def phone_case(bank: QuestionBank) -> dict:
    return make_case({
        "event_time": "民國115年10月25日19時",
        "location": "臺中市便利商店",
        "summary": SUMMARY,
        "case_kind": "WITH_VICTIM",
    }, bank)


def apply_fact(case: dict, value: str, bank: QuestionBank) -> dict:
    return update_gate1_facts(case, {"facts": {"F-CONDUCT": value}}, bank)


def summary(case: dict) -> dict:
    return {
        "candidate_order": [
            {
                "id": item["candidate_id"],
                "score": item["score"],
                "role": item.get("candidate_role"),
                "issues": item.get("core_issue_ids", []),
                "supporting": item.get("supporting_facts", []),
                "contrary": item.get("contrary_facts", []),
            }
            for item in case["candidates"]
        ],
        "question_metadata": [
            {
                "id": item["question_id"],
                "type": item.get("question_type"),
                "basis": item.get("generation_basis"),
            }
            for item in case.get("next_question_batch", [])
        ],
    }


def main() -> int:
    bank = QuestionBank()
    baseline = apply_fact(phone_case(bank), "手機當時的持有狀態尚待確認。", bank)
    scenario_a = apply_fact(phone_case(bank), "甲一直坐在櫃檯旁，手機放在甲伸手即可取回的位置，乙拿取時看見甲正在注意該手機。", bank)
    scenario_b = apply_fact(phone_case(bank), "甲離開店內一段時間後才發現手機遺失；乙拾得時甲不在現場。", bank)
    scenario_c = confirm_gate1(phone_case(bank), bank)
    answers = {item["question_id"]: "乙拿起手機後立即交給店員，表示希望協助尋找失主。" for item in scenario_c["next_question_batch"]}
    scenario_c = confirm_answers(scenario_c, {"answers": answers}, bank)

    scenario_d = phone_case(bank)
    scenario_d["active_role"] = "suspect"
    scenario_d["answers"]["victim"] = {"Q-V": "乙拿著手機離開店內"}
    scenario_d["question_batches"] = [{
        "role": "victim", "answered_question_ids": ["Q-V"],
        "questions": [{"question_id": "Q-V", "fact_target": "acquisition_method"}],
    }]
    scenario_d["next_question_batch"] = [{
        "question_id": "Q-S", "text": "你如何處理手機？", "role": "suspect",
        "family_id": "property_possession_taking", "fact_target": "acquisition_method",
        "element_type": "conduct", "layer": "element_supplement", "requirement": "REQUIRED",
        "legal_review_status": "HUMAN_REVIEW_REQUIRED", "template_binding": "NONE", "why": "核對",
    }]
    scenario_d = confirm_answers(scenario_d, {"answers": {"Q-S": "我沒有把手機帶離店內"}}, bank)

    checks = {
        "baseline_keeps_both": {"pass": {"theft", "embezzlement"}.issubset({x["candidate_id"] for x in baseline["candidates"]})},
        "scenario_a_theft_first": {"pass": scenario_a["candidates"][0]["candidate_id"] == "theft"},
        "scenario_b_lost_property_first": {"pass": scenario_b["candidates"][0]["candidate_id"] == "embezzlement"},
        "scenario_c_not_auto_rejected": {"pass": all(x.get("candidate_role") != "REJECTED" for x in scenario_c["candidates"])},
        "scenario_d_preserves_conflict": {"pass": bool(scenario_d["disputed_facts"] and scenario_d["fact_assertions"])},
    }
    result = {
        "status": "PASS" if all(item["pass"] for item in checks.values()) else "FAIL",
        "checks": checks,
        "baseline": summary(baseline),
        "scenario_a": summary(scenario_a),
        "scenario_b": summary(scenario_b),
        "scenario_c": summary(scenario_c),
        "scenario_d": {
            "disputed_facts": scenario_d["disputed_facts"],
            "contradiction_issues": scenario_d["contradiction_issues"],
            "assertions": scenario_d["fact_assertions"],
            "candidate_order": summary(scenario_d)["candidate_order"],
        },
        "external_network_used": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
