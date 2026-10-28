"""Read-only Gate 1 fact-contract audit (five property scenarios).

Usage (from ``legal-case-web``)::

    python -m tools.gate1_fact_contract_audit
    python -m tools.gate1_fact_contract_audit --json out.json

What it proves, per scenario:

1. ``analyze_gate1`` produces typed facts with the full contract
   (``fact_key``/``value``/``assertion_class``/``source_type``/
   ``verification_status``) and exact source spans.
2. UNKNOWN stays UNKNOWN and is visible in ``gate1["unknowns"]``.
3. ``create_case`` hands the *same* fact records to ``candidate_offenses``.
4. ``update_gate1`` keeps facts-derived state in sync (no stale UNKNOWN label,
   contradiction links recomputed, unchanged facts -> unchanged projections).
5. ``analyze_candidates`` hands ``case["gate1"]`` to ``candidate_offenses``,
   and refuses to hand over facts when the analysed summary differs (spans
   would no longer match).
6. The formal ``approve_gate1`` -> ``set_offenses`` path passes facts into
   ``build_questions`` and its fact consumer ``mark_known_questions``.
7. Scenario D only: a party denial and a CCTV record stay as two separate
   facts, linked by one contradiction issue whose value stays UNKNOWN, and the
   link disappears when one side is removed.

It never writes to the case store, HTTP server, or LLM. ``analyze_candidates_v3``
is forced to ``None`` so only the deterministic rules path runs; no network call
is possible. Candidate ids are recorded as observations, never as expected
answers: the five scenario labels remain ``PENDING_HUMAN_REVIEW``.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import rules, workflow  # noqa: E402
from app.analysis_contract import (  # noqa: E402
    ASSERTION_CLASSES,
    SOURCE_TYPES,
    VERIFICATION_STATUSES,
)
from app.config import QUESTION_BANK_PATH  # noqa: E402
from app.rules import FACT_UNKNOWN_LABELS, analyze_gate1, load_bank  # noqa: E402

AUDIT_ID = "LEGAL-GATE1-FACT-CONTRACT-008"
AUDIT_VERSION = "gate1-fact-contract-audit-v1"

# Five scenarios fixed by the task; the legal labels stay PENDING_HUMAN_REVIEW.
CASES: dict[str, str] = {
    "BASE": (
        "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁。"
        "乙承認拿取手機離開，表示自己以為手機是他人遺留、不要的物品。"
        "目前未確認手機是否仍在甲的持有範圍、乙對手機所有權的認知及乙是否具有不法所有意圖。"
        "手機尚未尋獲。"
    ),
    "A_RETAINED": (
        "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁。"
        "甲仍在櫃檯旁，手機在甲伸手可及的位置；乙拿取時看見甲正在注意該手機。"
        "乙承認拿取手機離開；乙是否具有不法所有意圖仍未知。"
    ),
    "B_LOST": (
        "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁；甲離開店內後才發現手機遺失。"
        "乙承認拾得手機時甲不在現場，並將手機帶離；乙是否具有不法所有意圖仍未知。"
    ),
    "C_HANDOVER": (
        "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁。"
        "乙拿起手機後立即交給店員，並表示希望尋找失主。"
        "乙拿取、交付的時間與經過、店員證述及乙是否具有不法所有意圖仍待核對。"
    ),
    "D_CONFLICT": (
        "甲表示手機為其所有，曾將手機暫放在便利商店櫃檯旁。"
        "乙先否認曾將手機帶離店內；監視器資料顯示乙拿著手機離開。"
        "手機當時是否仍在甲的持有範圍、乙的認知及不法所有意圖仍待確認。"
    ),
}

# Facts that must stay explicitly UNKNOWN in each scenario (no silent negation).
EXPECTED_UNKNOWN: dict[str, tuple[str, ...]] = {
    "BASE": ("original_possession", "intent"),
    "A_RETAINED": ("intent",),
    "B_LOST": ("intent",),
    "C_HANDOVER": ("intent",),
    "D_CONFLICT": ("original_possession", "intent"),
}

TYPED_KEYS = (
    "original_possession",
    "third_party_possession",
    "ownership_knowledge",
    "intent",
    "taking",
    "post_acquisition_conduct",
)


def _typed(facts: list[dict[str, Any]], key: str | None = None) -> list[dict[str, Any]]:
    return [
        item for item in facts
        if item.get("fact_key") in TYPED_KEYS and (key is None or item.get("fact_key") == key)
    ]


def _check(status: str, detail: str, **extra: Any) -> dict[str, Any]:
    return {"status": status, "detail": detail, **extra}


def _summary_of(gate1: dict[str, Any]) -> str:
    return str(gate1.get("source_summary", ""))


def _contract_fields_ok(fact: dict[str, Any], summary: str) -> list[str]:
    problems: list[str] = []
    if not str(fact.get("fact_key") or ""):
        problems.append("fact_key 空白")
    if not str(fact.get("value") or ""):
        problems.append("value 空白")
    if fact.get("assertion_class") not in ASSERTION_CLASSES:
        problems.append(f"assertion_class={fact.get('assertion_class')!r}")
    if fact.get("source_type") not in SOURCE_TYPES:
        problems.append(f"source_type={fact.get('source_type')!r}")
    if fact.get("verification_status") not in VERIFICATION_STATUSES:
        problems.append(f"verification_status={fact.get('verification_status')!r}")
    for field in ("fact_id", "proposition_key", "event_id"):
        if not str(fact.get(field) or ""):
            problems.append(f"{field} 空白")
    excerpt = str(fact.get("source_excerpt") or "")
    start, end = fact.get("source_start"), fact.get("source_end")
    if excerpt:
        if not isinstance(start, int) or not isinstance(end, int):
            problems.append("source span 不是整數")
        elif summary[start:end] != excerpt:
            problems.append("source span 與 source_excerpt 不一致")
    return problems


def _gate1(summary: str) -> dict[str, Any]:
    return analyze_gate1(
        {"summary": summary, "event_time": "UNKNOWN", "location": "UNKNOWN"},
        use_ai=False,
    )


def _recorder(real: Any, store: list[dict[str, Any]], **fields: Any) -> Any:
    """Wrap ``real`` to capture args while still returning its real result."""

    def spy(*args: Any, **kwargs: Any) -> Any:
        row = {name: kwargs.get(name) for name in fields}
        row["args"] = args
        store.append(row)
        result = real(*args, **kwargs)
        for attr in ("question_coverage_by_route", "last_validation", "pruned_questions"):
            if hasattr(real, attr):
                setattr(spy, attr, getattr(real, attr))
        return result

    return spy


def _candidate_recorder(store: list[dict[str, Any]]) -> Any:
    """Capture the ``gate1`` argument of ``candidate_offenses`` (positional or keyword)."""
    real = rules.candidate_offenses

    def spy(*args: Any, **kwargs: Any) -> Any:
        gate1 = args[2] if len(args) > 2 else kwargs.get("gate1")
        store.append({"gate1": gate1, "args": args})
        return real(*args, **kwargs)

    return spy


def _positional_recorder(real: Any, store: list[dict[str, Any]], index: int) -> Any:
    """Capture one positional argument of ``real`` (used for gate1 consumers)."""

    def spy(*args: Any, **kwargs: Any) -> Any:
        store.append({"gate1": args[index] if len(args) > index else kwargs.get("gate1")})
        return real(*args, **kwargs)

    return spy


def _audit_case(name: str, summary: str, bank: dict[str, Any]) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    not_applicable: dict[str, str] = {}
    observations: dict[str, Any] = {"legal_labels": "PENDING_HUMAN_REVIEW"}

    try:
        gate1 = _gate1(summary)
    except Exception as exc:  # noqa: BLE001 - audit records the failure verbatim
        return {
            "case": name,
            "status": "FAIL",
            "checks": {"analyze_gate1_runs": _check("FAIL", f"{type(exc).__name__}: {exc}")},
            "not_applicable": {},
            "observations": observations,
        }
    gate1["source_summary"] = summary
    facts = [item for item in gate1.get("facts", []) if isinstance(item, dict)]
    typed = _typed(facts)
    observations["typed_fact_count"] = len(typed)
    observations["typed_facts"] = [
        {
            "fact_key": item.get("fact_key"),
            "value": item.get("value"),
            "assertion_class": item.get("assertion_class"),
            "source_type": item.get("source_type"),
            "verification_status": item.get("verification_status"),
            "machine_status": item.get("machine_status"),
            "has_source_span": isinstance(item.get("source_start"), int),
        }
        for item in typed
    ]

    # 1. typed contract
    problems = {
        item.get("fact_key"): _contract_fields_ok(item, summary)
        for item in typed
    }
    broken = {key: value for key, value in problems.items() if value}
    checks["typed_fact_contract"] = (
        _check("FAIL", "契約欄位不完整", problems=broken)
        if broken else
        _check("PASS", f"{len(typed)} 筆 typed facts 均有完整契約欄位與可回查 span")
    )

    # 2. UNKNOWN preserved
    missing_unknown: list[str] = []
    for key in EXPECTED_UNKNOWN[name]:
        rows = _typed(facts, key)
        if not any(
            item.get("value") == "UNKNOWN"
            and item.get("assertion_class") == "UNKNOWN"
            and item.get("verification_status") == "UNKNOWN"
            for item in rows
        ):
            missing_unknown.append(f"{key}: 無 UNKNOWN 事實")
            continue
        label = FACT_UNKNOWN_LABELS.get(key)
        if label and label not in gate1.get("unknowns", []):
            missing_unknown.append(f"{key}: unknowns 缺標籤")
    checks["unknown_preserved"] = (
        _check("FAIL", "UNKNOWN 遺失或被轉換", problems=missing_unknown)
        if missing_unknown else
        _check("PASS", f"UNKNOWN 保留：{', '.join(EXPECTED_UNKNOWN[name])}")
    )

    # 3. create_case delivery
    create_calls: list[dict[str, Any]] = []
    with mock.patch.object(workflow, "candidate_offenses", _candidate_recorder(create_calls)):
        case = workflow.create_case({"summary": summary, "has_victim": True}, bank)
    passed = create_calls[-1]["gate1"] if create_calls else None
    if passed is None:
        checks["create_case_delivery"] = _check("FAIL", "candidate_offenses 未收到 gate1")
    elif passed.get("facts") != case["gate1"]["facts"]:
        checks["create_case_delivery"] = _check(
            "FAIL", "候選產生器收到的 facts 與案件保存的 facts 不是同一組記錄"
        )
    else:
        received_unknown = [
            item.get("fact_key") for item in passed["facts"]
            if item.get("value") == "UNKNOWN" and item.get("fact_key") in TYPED_KEYS
        ]
        checks["create_case_delivery"] = _check(
            "PASS",
            f"{len(passed['facts'])} 筆 facts 與案件保存一致；其中 UNKNOWN typed keys="
            f"{sorted(set(received_unknown))}",
        )

    # 4. update_gate1: stale UNKNOWN label must disappear
    kept = [item for item in copy.deepcopy(case["gate1"]["facts"]) if item.get("fact_key") != "intent"]
    label = FACT_UNKNOWN_LABELS["intent"]
    before_unknowns = list(case["gate1"].get("unknowns", []))
    try:
        updated = workflow.apply_action(
            copy.deepcopy(case), "update_gate1", {"gate1": {"facts": kept}}, bank
        )
        after = updated["gate1"]
        intent_rows = _typed(after["facts"], "intent")
        remaining_labels = [item for item in after.get("unknowns", []) if item in FACT_UNKNOWN_LABELS.values()]
        stale = label in after.get("unknowns", [])
        checks["update_gate1_unknown_sync"] = (
            _check(
                "FAIL",
                "移除 intent 事實後 unknowns 仍殘留舊標籤",
                stale_label=label,
                unknowns_after=after.get("unknowns"),
            )
            if stale or intent_rows else
            _check(
                "PASS",
                f"intent 事實移除後 unknowns 同步（剩下的 typed UNKNOWN 標籤：{remaining_labels}）",
                unknowns_before_count=len(before_unknowns),
                unknowns_after=after.get("unknowns"),
            )
        )
        observations["unknowns_after_intent_removal"] = after.get("unknowns")
    except Exception as exc:  # noqa: BLE001
        checks["update_gate1_unknown_sync"] = _check("FAIL", f"{type(exc).__name__}: {exc}")

    # 5. update_gate1: unchanged facts -> unchanged derived projections
    projection_keys = (
        "unknowns", "evidence_leads", "verified_evidence", "consent_states",
        "causation", "causal_edges", "legal_characterizations", "contradiction_issues",
    )
    try:
        pristine = workflow.create_case({"summary": summary, "has_victim": True}, bank)
        snapshot = {key: copy.deepcopy(pristine["gate1"].get(key)) for key in projection_keys}
        roundtrip = workflow.apply_action(
            pristine,
            "update_gate1",
            {"gate1": {"facts": copy.deepcopy(pristine["gate1"]["facts"])}},
            bank,
        )["gate1"]
        drift = [key for key in projection_keys if roundtrip.get(key) != snapshot[key]]
        checks["update_gate1_projection_stability"] = (
            _check("FAIL", f"facts 未變更但衍生狀態漂移：{drift}")
            if drift else
            _check("PASS", f"{len(projection_keys)} 項 facts 衍生狀態在 facts 未變更時保持不變")
        )
    except Exception as exc:  # noqa: BLE001
        checks["update_gate1_projection_stability"] = _check("FAIL", f"{type(exc).__name__}: {exc}")

    # 6. analyze_candidates delivery (forces the rules fallback, no network)
    analysis_calls: list[dict[str, Any]] = []
    try:
        target = workflow.create_case({"summary": summary, "has_victim": True}, bank)
        with mock.patch.object(workflow, "analyze_candidates_v3", lambda *a, **k: None), mock.patch.object(
            workflow,
            "candidate_offenses",
            _candidate_recorder(analysis_calls),
        ):
            analysed = workflow.apply_action(
                target, "analyze_candidates", {"external_ai_consent": True}, bank
            )
        received = analysis_calls[-1]["gate1"] if analysis_calls else None
        if received is None:
            checks["analyze_candidates_delivery"] = _check(
                "FAIL", "analyze_candidates 呼叫 candidate_offenses 時 gate1 為 None"
            )
        else:
            received_unknown = {
                item.get("fact_key") for item in received.get("facts", [])
                if item.get("value") == "UNKNOWN"
            }
            checks["analyze_candidates_delivery"] = _check(
                "PASS",
                f"analysis 路徑收到 {len(received.get('facts', []))} 筆 facts；UNKNOWN keys="
                f"{sorted(received_unknown)}",
                candidate_ids=[item.get("id") for item in analysed.get("candidates", [])],
            )
        observations["candidate_ids"] = [item.get("id") for item in analysed.get("candidates", [])]
        observations["unknown_fact_keys"] = {
            item.get("id"): item.get("unknown_fact_keys") for item in analysed.get("candidates", [])
        }
    except Exception as exc:  # noqa: BLE001
        checks["analyze_candidates_delivery"] = _check("FAIL", f"{type(exc).__name__}: {exc}")

    # 7. rewritten summary must not inherit stale span-bound facts
    stale_calls: list[dict[str, Any]] = []
    try:
        stale_case = workflow.create_case({"summary": summary, "has_victim": True}, bank)
        with mock.patch.object(workflow, "analyze_candidates_v3", lambda *a, **k: None), mock.patch.object(
            workflow,
            "candidate_offenses",
            _candidate_recorder(stale_calls),
        ):
            workflow.apply_action(
                stale_case,
                "analyze_candidates",
                {"external_ai_consent": True, "summary": summary + "（另行改寫的摘要）"},
                bank,
            )
        received = stale_calls[-1]["gate1"] if stale_calls else "NO_CALL"
        checks["stale_summary_guard"] = (
            _check("PASS", "摘要被改寫時未把 span 對不上的 facts 傳給候選產生器")
            if received is None else
            _check("FAIL", "摘要被改寫時仍傳入 Gate 1 facts，span 可能失效")
        )
    except Exception as exc:  # noqa: BLE001
        checks["stale_summary_guard"] = _check("FAIL", f"{type(exc).__name__}: {exc}")

    # 8. formal build_questions path receives facts and forwards them to its consumer
    build_calls: list[dict[str, Any]] = []
    known_calls: list[dict[str, Any]] = []
    try:
        flow = workflow.create_case({"summary": summary, "has_victim": True}, bank)
        flow = workflow.apply_action(flow, "approve_gate1", {"confirmed": True}, bank)
        real_build = workflow.build_questions
        with mock.patch.object(
            workflow, "build_questions", _recorder(real_build, build_calls, gate1="gate1")
        ), mock.patch.object(
            rules,
            "mark_known_questions",
            _positional_recorder(rules.mark_known_questions, known_calls, 1),
        ):
            flow = workflow.apply_action(
                flow,
                "set_offenses",
                {
                    "offense_ids": ["theft"],
                    "legal_route_ids": ["theft_320_1_movable"],
                    "route_review_confirmed": True,
                    "role": "victim",
                },
                bank,
            )
        build_gate1 = build_calls[-1]["gate1"] if build_calls else None
        known_gate1 = known_calls[-1]["gate1"] if known_calls else None
        question_count = len(flow.get("questions", []))
        problems: list[str] = []
        if build_gate1 is None:
            problems.append("build_questions 未收到 gate1")
        elif build_gate1.get("facts") != flow["gate1"]["facts"]:
            problems.append("build_questions 收到的 facts 與案件不一致")
        if known_gate1 is None:
            problems.append("mark_known_questions 未收到 gate1")
        elif not any(item.get("fact_key") in TYPED_KEYS for item in known_gate1.get("facts", [])):
            problems.append("mark_known_questions 收到的 facts 沒有 typed 契約欄位")
        if question_count == 0:
            problems.append("未產生問句")
        checks["build_questions_delivery"] = (
            _check("FAIL", "；".join(problems), question_count=question_count)
            if problems else
            _check(
                "PASS",
                f"正式流程把 facts 傳入 build_questions 與 mark_known_questions；產生 {question_count} 題",
                question_count=question_count,
            )
        )
        observations["question_count"] = question_count
    except Exception as exc:  # noqa: BLE001
        checks["build_questions_delivery"] = _check("FAIL", f"{type(exc).__name__}: {exc}")

    # 9. scenario D only: denial vs evidence separation and traceable conflict
    if name == "D_CONFLICT":
        taking = _typed(facts, "taking")
        denial = next((item for item in taking if item.get("assertion_class") == "DENIED"), None)
        cctv = next((item for item in taking if item.get("source_type") == "EVIDENCE"), None)
        issues = gate1.get("contradiction_issues", [])
        separation_problems: list[str] = []
        if denial is None or denial.get("source_type") != "PARTY_STATEMENT":
            separation_problems.append("缺少當事人否認（PARTY_STATEMENT/DENIED）")
        if cctv is None or cctv.get("assertion_class") != "ASSERTED":
            separation_problems.append("缺少外部證據（EVIDENCE/ASSERTED）")
        if denial and cctv and denial.get("fact_id") == cctv.get("fact_id"):
            separation_problems.append("否認與證據被壓成同一筆 fact")
        checks["denial_evidence_separated"] = (
            _check("FAIL", "；".join(separation_problems))
            if separation_problems else
            _check(
                "PASS",
                f"否認與監視器各自保存（{denial['fact_id']} / {cctv['fact_id']}）",
            )
        )
        trace_problems: list[str] = []
        if len(issues) != 1:
            trace_problems.append(f"矛盾紀錄數={len(issues)}（預期 1）")
        else:
            issue = issues[0]
            if denial and cctv and set(issue.get("fact_refs", [])) != {denial["fact_id"], cctv["fact_id"]}:
                trace_problems.append("fact_refs 未同時連結否認與證據")
            if issue.get("denial_fact_ids") != ([denial["fact_id"]] if denial else []):
                trace_problems.append("denial_fact_ids 不正確")
            if issue.get("contrary_fact_ids") != ([cctv["fact_id"]] if cctv else []):
                trace_problems.append("contrary_fact_ids 不正確")
            if issue.get("resolved_value") != "UNKNOWN":
                trace_problems.append(f"resolved_value={issue.get('resolved_value')!r}（須為 UNKNOWN）")
        checks["contradiction_traceable"] = (
            _check("FAIL", "；".join(trace_problems))
            if trace_problems else
            _check(
                "PASS",
                "1 筆矛盾同時連結否認與證據，resolved_value=UNKNOWN（待人工複核）",
                issue=issues[0] if issues else None,
            )
        )
        try:
            retained = [
                item for item in copy.deepcopy(case["gate1"]["facts"])
                if not (item.get("fact_key") == "taking" and item.get("assertion_class") == "DENIED")
            ]
            cleared = workflow.apply_action(
                copy.deepcopy(case), "update_gate1", {"gate1": {"facts": retained}}, bank
            )["gate1"]
            checks["contradiction_cleared_on_fact_removal"] = (
                _check("PASS", "移除否認事實後矛盾連結同步清除")
                if cleared.get("contradiction_issues") == [] else
                _check("FAIL", "移除否認事實後仍留有矛盾連結")
            )
        except Exception as exc:  # noqa: BLE001
            checks["contradiction_cleared_on_fact_removal"] = _check("FAIL", f"{type(exc).__name__}: {exc}")
    else:
        for skipped in (
            "denial_evidence_separated",
            "contradiction_traceable",
            "contradiction_cleared_on_fact_removal",
        ):
            not_applicable[skipped] = "此情境沒有當事人否認與外部證據衝突"

    failed = [key for key, value in checks.items() if value["status"] == "FAIL"]
    status = "FAIL" if failed else "PASS"
    return {
        "case": name,
        "status": status,
        "failed_checks": failed,
        "checks": checks,
        "not_applicable": not_applicable,
        "observations": observations,
    }


def run() -> dict[str, Any]:
    bank = load_bank(QUESTION_BANK_PATH)
    report: dict[str, Any] = {
        "audit_id": AUDIT_ID,
        "audit_version": AUDIT_VERSION,
        "mode": "read-only / deterministic rules only (analyze_candidates_v3 forced to None)",
        "legal_label_status": "PENDING_HUMAN_REVIEW",
        "claims_not_made": [
            "不宣稱五案候選罪名正確",
            "不宣稱法律要件已成立",
            "未變更候選排序、Prompt、DB schema 或 HTTP 介面",
        ],
        "cases": {},
    }
    for name, summary in CASES.items():
        report["cases"][name] = _audit_case(name, summary, bank)
    statuses = [item["status"] for item in report["cases"].values()]
    report["overall"] = (
        "FAIL" if "FAIL" in statuses else
        "PARTIAL_PASS" if "NOT_VERIFIED" in statuses else
        "PASS"
    )
    report["summary"] = {
        name: {
            "status": item["status"],
            "failed_checks": item["failed_checks"],
            "candidate_ids": item["observations"].get("candidate_ids"),
            "question_count": item["observations"].get("question_count"),
        }
        for name, item in report["cases"].items()
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="write the full report JSON to this path")
    args = parser.parse_args(argv)
    report = run()
    if args.json:
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {args.json}")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"overall: {report['overall']}")
    return 0 if report["overall"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
