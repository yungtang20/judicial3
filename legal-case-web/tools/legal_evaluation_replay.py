"""Trace-first offline evaluator for the existing legal analysis functions.

This sidecar reads raw summaries from an independently authored fixture.  Gold
facts are never passed into the candidate runtime.  No LLM, database, HTTP or
frontend dependency is used.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import QUESTION_BANK_PATH  # noqa: E402
from app.rules import analyze_gate1, build_questions, candidate_offenses, load_bank  # noqa: E402


FIXTURE_PATH = ROOT / "LEGAL_EVALUATION_FIXTURE.json"
TRACE_PATH = ROOT / "LEGAL_EVALUATION_TRACE.json"
REPORT_PATH = ROOT / "LEGAL_EVALUATION_REPORT.md"
TRACE_VERSION = "tw-legal-eval-trace-v1"
ROUTE_MIN_FIELDS = {"route_id", "elements"}


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_fixture(path: Path = FIXTURE_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_source_spans(case: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    summary = case["raw_summary"]
    fact_ids: set[str] = set()
    for fact in case.get("gold_facts", []):
        fact_id = fact.get("fact_id", "")
        if not fact_id or fact_id in fact_ids:
            findings.append({"code": "INVALID_FACT_ID", "fact_id": fact_id})
        fact_ids.add(fact_id)
        source = fact.get("source", {})
        start, end, text = source.get("start"), source.get("end"), source.get("text")
        if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end > len(summary) or start >= end:
            findings.append({"code": "SOURCE_SPAN_OUT_OF_RANGE", "fact_id": fact_id})
        elif summary[start:end] != text:
            findings.append({"code": "SOURCE_SPAN_TEXT_MISMATCH", "fact_id": fact_id})
        if source.get("type") not in {"PARTY_STATEMENT", "EVIDENCE"}:
            findings.append({"code": "SOURCE_TYPE_MISSING_OR_INVALID", "fact_id": fact_id})
        if fact.get("assertion_class") not in {"ASSERTED", "ADMITTED", "DENIED", "INFERRED", "UNKNOWN"}:
            findings.append({"code": "ASSERTION_CLASS_INVALID", "fact_id": fact_id})
        if fact.get("verification_status") not in {"UNVERIFIED", "CORROBORATED", "CONTRADICTED", "UNKNOWN"}:
            findings.append({"code": "VERIFICATION_STATUS_INVALID", "fact_id": fact_id})
    for element in case.get("gold_elements", []):
        for fact_ref in element.get("fact_refs", []):
            if fact_ref not in fact_ids:
                findings.append({"code": "ORPHAN_ELEMENT_FACT_REF", "fact_ref": fact_ref})
    return findings


def candidate_metrics(
    actual_ids: Iterable[str], gold: dict[str, list[str]], k: int
) -> dict[str, Any]:
    top = list(actual_ids)[:k]
    required = set(gold.get("required", []))
    relevant = required | set(gold.get("acceptable", []))
    prohibited = set(gold.get("prohibited", []))
    recall = None if not required else len(required & set(top)) / len(required)
    precision = None if not top else len(relevant & set(top)) / len(top)
    prohibited_hits = [item for item in top if item in prohibited]
    return {
        "k": k,
        "top_k": top,
        "recall_at_k": recall,
        "recall_status": "NOT_APPLICABLE" if recall is None else "OBSERVED",
        "precision_at_k": precision,
        "precision_status": "NOT_APPLICABLE" if precision is None else "OBSERVED",
        "missing_required": sorted(required - set(top)),
        "prohibited_hits": prohibited_hits,
        "hard_fail": bool(prohibited_hits),
    }


def _function_evidence(function: Any) -> dict[str, Any]:
    path = Path(inspect.getsourcefile(function) or "")
    _, line = inspect.getsourcelines(function)
    return {"file": str(path), "line": line, "function": function.__name__, "signature": str(inspect.signature(function))}


def _candidate_view(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = (
        "id", "candidate_id", "name", "status", "candidate_state",
        "candidate_eligibility", "matched_terms", "selection_origin",
        "inclusion_reason", "reservation_reason", "supporting_fact_refs",
        "contradicting_fact_refs", "unknown_fact_keys", "unknown_elements",
        "candidate_rank_factors", "legal_route_states", "route_element_matrix",
    )
    return [{key: copy.deepcopy(item.get(key)) for key in keys if key in item} for item in candidates]


def _question_view(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "id": item.get("id"), "text": item.get("text"), "kind": item.get("kind"),
        "offense_id": item.get("offense_id"), "element_id": item.get("element_id"),
        "meta": copy.deepcopy(item.get("meta", {})),
    } for item in questions]


def _route_index(candidates: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for candidate in candidates:
        for route in candidate.get("route_element_matrix", []):
            if ROUTE_MIN_FIELDS <= route.keys():
                for element in route.get("elements", []):
                    index[(str(route.get("route_id")), str(element.get("element")))] = element
    return index


def _element_metrics(candidates: list[dict[str, Any]], gold_elements: list[dict[str, Any]]) -> dict[str, Any]:
    index = _route_index(candidates)
    rows: list[dict[str, Any]] = []
    correct = 0
    checkable = 0
    for gold in gold_elements:
        actual = index.get((gold["route_id"], gold["element_label"]))
        actual_status = "MISSING" if actual is None else str(actual.get("status", "MISSING"))
        expected = gold["state"]
        if actual_status == "NOT_CHECKABLE":
            outcome = "NOT_CHECKABLE"
        elif expected == "SUPPORTED":
            outcome = "MATCH" if actual_status == "SOURCE_SUPPORTED" else "MISMATCH"
        elif expected == "UNKNOWN":
            outcome = "MATCH" if actual_status == "ABSENT" else "MISMATCH"
        elif expected == "CONTRADICTED":
            outcome = "MATCH" if actual_status == "CONTRADICTED" else "MISMATCH"
        else:
            outcome = "MATCH" if actual_status == "NOT_APPLICABLE" else "MISMATCH"
        if outcome != "NOT_CHECKABLE":
            checkable += 1
        if outcome == "MATCH":
            correct += 1
        rows.append({
            "route_id": gold["route_id"], "element_label": gold["element_label"],
            "expected": expected, "actual": actual_status, "outcome": outcome,
            "actual_supporting_fact_refs": [] if actual is None else actual.get("supporting_fact_refs", []),
        })
    return {
        "accuracy": None if not gold_elements else correct / len(gold_elements),
        "correct": correct, "denominator": len(gold_elements),
        "checkable_count": checkable,
        "not_checkable_count": sum(row["outcome"] == "NOT_CHECKABLE" for row in rows),
        "rows": rows,
    }


def _runtime_fact_matches(gold_fact: dict[str, Any], runtime_fact: dict[str, Any]) -> bool:
    source = gold_fact["source"]
    start, end = runtime_fact.get("source_start"), runtime_fact.get("source_end")
    span_overlap = isinstance(start, int) and isinstance(end, int) and start < source["end"] and end > source["start"]
    return runtime_fact.get("fact_key") == gold_fact.get("fact_key") or span_overlap


def _unknown_metrics(gold_facts: list[dict[str, Any]], runtime_facts: list[dict[str, Any]]) -> dict[str, Any]:
    unknowns = [fact for fact in gold_facts if fact.get("assertion_class") == "UNKNOWN"]
    rows: list[dict[str, Any]] = []
    preserved = 0
    promoted: list[str] = []
    for fact in unknowns:
        typed = [item for item in runtime_facts if item.get("fact_key") == fact.get("fact_key")]
        matches = typed or [item for item in runtime_facts if _runtime_fact_matches(fact, item)]
        status = "MISSING"
        if any(item.get("machine_status") == "UNKNOWN" and item.get("value") == "UNKNOWN" for item in matches):
            status = "PRESERVED"
            preserved += 1
        elif matches:
            status = "PROMOTED_OR_UNTYPED"
            promoted.append(fact["fact_id"])
        rows.append({"fact_id": fact["fact_id"], "fact_key": fact["fact_key"], "status": status,
                     "runtime_fact_ids": [item.get("fact_id") for item in matches]})
    return {
        "rate": None if not unknowns else preserved / len(unknowns),
        "preserved": preserved, "denominator": len(unknowns), "rows": rows,
        "promoted_or_untyped": promoted, "hard_fail": bool(promoted),
    }


def _question_metrics(questions: list[dict[str, Any]], expected_gaps: list[str]) -> dict[str, Any]:
    observed: set[str] = set()
    for question in questions:
        if question.get("element_id"):
            observed.add(str(question["element_id"]))
        meta = question.get("meta", {})
        if meta.get("fact_target"):
            observed.add(str(meta["fact_target"]))
    covered = [gap for gap in expected_gaps if gap in observed]
    return {
        "rate": None if not expected_gaps else len(covered) / len(expected_gaps),
        "covered": covered, "missing": [gap for gap in expected_gaps if gap not in observed],
        "denominator": len(expected_gaps), "observed_fact_targets": sorted(observed),
        "lane": "GOLD_SELECTED_PARENT_AND_ROUTE",
    }


def _trace_metrics(
    case: dict[str, Any], runtime_facts: list[dict[str, Any]], candidates: list[dict[str, Any]], questions: list[dict[str, Any]],
    legal_sources: list[dict[str, Any]], span_findings: list[dict[str, Any]],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(check: str, passed: bool, detail: str = "") -> None:
        checks.append({"check": check, "passed": passed, "detail": detail})

    add("gold_source_spans", not span_findings, json.dumps(span_findings, ensure_ascii=False))
    runtime_fact_ids = {
        ref for candidate in candidates for ref in candidate.get("supporting_fact_refs", [])
    }
    known_fact_ids = {str(fact.get("fact_id")) for fact in runtime_facts if fact.get("fact_id")}
    orphan_refs = sorted(ref for ref in runtime_fact_ids if ref not in known_fact_ids and ref != "intake.summary")
    add("candidate_fact_refs_resolve", not orphan_refs, f"orphan_refs={orphan_refs}")
    expected_routes = {item["route_id"] for item in case.get("gold_elements", [])}
    observed_routes = {route.get("route_id") for candidate in candidates for route in candidate.get("route_element_matrix", [])}
    add("element_candidate_links", expected_routes <= observed_routes,
        f"missing={sorted(expected_routes - observed_routes)}")
    observed_targets = {
        str(question.get("meta", {}).get("fact_target")) for question in questions
        if question.get("meta", {}).get("fact_target")
    }
    expected_gaps = set(case.get("gold_question_gaps", []))
    add("question_gap_links", expected_gaps <= observed_targets,
        f"missing={sorted(expected_gaps - observed_targets)}")
    law_fields = {"source_id", "law_name", "article", "official_url", "law_version", "behavior_time",
                  "applicability_status", "fetched_at", "content_hash", "parser_version", "source_type"}
    add("legal_source_metadata", bool(legal_sources) and all(law_fields <= source.keys() for source in legal_sources))
    add("law_time_applicability_verified", all(source.get("applicability_status") != "UNKNOWN" for source in legal_sources),
        "UNKNOWN is retained and cannot be reported as PASS")
    passed = sum(item["passed"] for item in checks)
    return {"rate": passed / len(checks), "passed": passed, "denominator": len(checks), "checks": checks}


def _fact_stage(case: dict[str, Any], runtime_facts: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for gold in case.get("gold_facts", []):
        matches = [item for item in runtime_facts if _runtime_fact_matches(gold, item)]
        typed = any(item.get("fact_key") == gold.get("fact_key") for item in matches)
        assertion_preserved = (
            gold["assertion_class"] == "UNKNOWN" and any(item.get("machine_status") == "UNKNOWN" for item in matches)
        ) or (
            gold["assertion_class"] != "UNKNOWN" and any(
                item.get("assertion_class") == gold["assertion_class"] for item in matches
            )
        )
        rows.append({"fact_id": gold["fact_id"], "fact_key": gold["fact_key"], "runtime_fact_ids": [m.get("fact_id") for m in matches],
                     "typed_key_preserved": typed, "assertion_semantics_preserved": assertion_preserved})
    return {"match": all(row["typed_key_preserved"] and row["assertion_semantics_preserved"] for row in rows), "rows": rows}


def _first_divergence(fact_stage: dict[str, Any], elements: dict[str, Any], candidates: dict[str, Any], questions: dict[str, Any]) -> str:
    if not fact_stage["match"]:
        return "FACT"
    if elements["accuracy"] != 1.0:
        return "LEGAL_ELEMENT"
    if candidates["missing_required"] or candidates["prohibited_hits"]:
        return "CANDIDATE"
    if questions["rate"] != 1.0:
        return "QUESTION"
    return "NONE"


def replay_case(case: dict[str, Any], fixture: dict[str, Any], bank: dict[str, Any]) -> dict[str, Any]:
    summary = case["raw_summary"]
    gate1 = analyze_gate1({"summary": summary, "event_time": "", "location": ""}, use_ai=False)
    candidates = candidate_offenses(summary, bank, gate1)
    selected = case["question_selection"]
    questions = build_questions(
        bank, "victim", list(selected["parents"]), gate1=gate1,
        candidates=candidates, legal_route_ids=list(selected["routes"]),
    )
    candidate_view = _candidate_view(candidates)
    question_view = _question_view(questions)
    spans = validate_source_spans(case)
    candidate_result = candidate_metrics([item.get("id", "") for item in candidates], case["gold_candidates"], fixture["k"])
    element_result = _element_metrics(candidates, case["gold_elements"])
    unknown_result = _unknown_metrics(case["gold_facts"], gate1.get("facts", []))
    question_result = _question_metrics(questions, case["gold_question_gaps"])
    trace_result = _trace_metrics(case, gate1.get("facts", []), candidates, questions, fixture["legal_sources"], spans)
    fact_stage = _fact_stage(case, gate1.get("facts", []))
    hard_findings = list(spans)
    if candidate_result["prohibited_hits"]:
        hard_findings.append({"code": "PROHIBITED_CANDIDATE_IN_TOP_K", "ids": candidate_result["prohibited_hits"]})
    if unknown_result["hard_fail"]:
        hard_findings.append({"code": "UNKNOWN_PROMOTED_OR_UNTYPED", "fact_ids": unknown_result["promoted_or_untyped"]})
    if case["case_id"] == "phone-denial-cctv-conflict":
        conflict_preserved = any(
            row["fact_id"] == "d-denial" and row["runtime_fact_ids"] and row["assertion_semantics_preserved"]
            for row in fact_stage["rows"]
        )
        if not conflict_preserved:
            hard_findings.append({"code": "DENIAL_CONFLICT_NOT_PRESERVED"})
    first = _first_divergence(fact_stage, element_result, candidate_result, question_result)
    return {
        "case_id": case["case_id"], "purpose": case["purpose"], "raw_summary": summary,
        "gold_hash": canonical_hash({key: case[key] for key in case if key != "raw_summary"}),
        "actual": {"gate1_facts": copy.deepcopy(gate1.get("facts", [])), "candidates": candidate_view, "questions": question_view},
        "stages": {"fact": fact_stage, "element": element_result, "candidate": candidate_result,
                   "unknown": unknown_result, "question": question_result, "source_trace": trace_result},
        "first_divergence_stage": first, "hard_findings": hard_findings,
    }


def semantic_projection(case_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "case_id": item["case_id"],
        "facts": item["actual"]["gate1_facts"],
        "candidates": item["actual"]["candidates"],
        "questions": item["actual"]["questions"],
        "stages": item["stages"],
        "first_divergence_stage": item["first_divergence_stage"],
        "hard_findings": item["hard_findings"],
    } for item in case_results]


def _git_version() -> dict[str, Any]:
    def run(*args: str) -> str:
        return subprocess.run(
            args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            errors="replace", check=False,
        ).stdout.strip()
    return {"head": run("git", "rev-parse", "HEAD") or "UNKNOWN", "branch": run("git", "branch", "--show-current") or "UNKNOWN",
            "worktree_dirty": bool(run("git", "status", "--porcelain"))}


def run_evaluation(*, fixture_path: Path = FIXTURE_PATH, repetitions: int = 3) -> dict[str, Any]:
    fixture = load_fixture(fixture_path)
    fixture_findings = [finding | {"case_id": case["case_id"]} for case in fixture["cases"] for finding in validate_source_spans(case)]
    if fixture_findings:
        raise ValueError(f"Invalid fixture source graph: {fixture_findings}")
    bank = load_bank(QUESTION_BANK_PATH)
    runs = [[replay_case(case, fixture, bank) for case in fixture["cases"]] for _ in range(repetitions)]
    hashes = [canonical_hash(semantic_projection(run)) for run in runs]
    rules_path = Path(inspect.getsourcefile(candidate_offenses) or ROOT / "app" / "rules.py")
    trace = {
        "trace_version": TRACE_VERSION,
        "fixture_path": str(fixture_path), "fixture_hash": file_hash(fixture_path),
        "fixture_status": fixture["status"], "gold_reviewer": fixture["gold_reviewer"],
        "runtime": {"entry": "app.workflow-compatible deterministic functions", "git": _git_version(),
                    "functions": {name: _function_evidence(fn) for name, fn in {
                        "analyze_gate1": analyze_gate1, "candidate_offenses": candidate_offenses, "build_questions": build_questions}.items()},
                    "versions": {"rules_sha256": file_hash(rules_path), "question_bank_sha256": file_hash(QUESTION_BANK_PATH),
                                 "fixture_sha256": file_hash(fixture_path)}},
        "separation_controls": {"gold_facts_passed_to_candidate_runtime": False,
                                "question_lane": "independent gold-selected parent/route",
                                "citation_parser_drives_candidate": False},
        "determinism": {"repetitions": repetitions, "semantic_hashes": hashes,
                        "status": "PASS" if len(set(hashes)) == 1 else "FAIL"},
        "cases": runs[0],
        "external_dependencies": fixture["external_dependencies"],
        "overall": (
            "PASS"
            if len(set(hashes)) == 1
            and not any(item["hard_findings"] for item in runs[0])
            and all(item["first_divergence_stage"] == "NONE" for item in runs[0])
            else "PARTIAL_PASS"
        ),
        "limitations": [
            "Gold is an initial regression baseline with user-reviewed conditions; A/B/D are not unconditional legal answers.",
            "Law behavior time and historical applicability remain UNKNOWN.",
            "This sidecar does not reproduce or resolve the historical 337 CANDIDATE / 320 NEEDS_FACTS output.",
            "LLM, database, HTTP, frontend and formal end-to-end paths were not run.",
        ],
    }
    return trace


def render_report(trace: dict[str, Any]) -> str:
    lines = [
        "# 臺灣案件推理離線評估報告", "", f"- Trace version: `{trace['trace_version']}`",
        f"- Fixture: `{trace['fixture_status']}`（reviewer: `{trace['gold_reviewer']}`）",
        f"- Determinism: `{trace['determinism']['status']}` / {trace['determinism']['repetitions']} runs",
        f"- Overall: `{trace['overall']}`", "",
        "## 個案結果", "",
        "| Case | First divergence | Recall@3 | Precision@3 | Element | Unknown | Question | Trace | Hard findings |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    def fmt(value: Any) -> str:
        return "N/A" if value is None else f"{value:.2f}"
    for case in trace["cases"]:
        stages = case["stages"]
        lines.append(
            f"| `{case['case_id']}` | `{case['first_divergence_stage']}` | "
            f"{fmt(stages['candidate']['recall_at_k'])} | {fmt(stages['candidate']['precision_at_k'])} | "
            f"{fmt(stages['element']['accuracy'])} | {fmt(stages['unknown']['rate'])} | "
            f"{fmt(stages['question']['rate'])} | {fmt(stages['source_trace']['rate'])} | "
            f"{', '.join(item['code'] for item in case['hard_findings']) or 'none'} |"
        )
    lines += ["", "## 邊界與結論", "",
              "- 主要候選 lane 只接收 raw summary 經既有 `analyze_gate1` 產生的 facts；人工 gold facts 未注入。",
              "- 問句 lane 使用人工預先選定的 parent/route，避免把所有自動候選誤當成人工核准方向。",
              "- `NOT_CHECKABLE` 只表示工具未涵蓋，不計為正確要件判斷。",
              "- 法規行為時間與歷史適用性為 `UNKNOWN`，來源追溯不得宣稱完整 PASS。",
              "- 本結果只定位契約差異，不代表原始候選偏差已定位或修復。", "",
              "## 獨立設計審查決策", "",
              "- 執行模式：`REVIEWED_PIPELINE`；獨立 reviewer 的實際模型身分為 `UNVERIFIED`，不得標記 DUAL_MODEL_PASS。",
              "- `ACCEPT`：gold/DUT 分離、精確來源 span、draft gold 狀態與 mutation test。",
              "- `ACCEPT`：required/acceptable/prohibited、固定 parent ID layer 與 K 邊界。",
              "- `ACCEPT`：問句採 gold-selected lane，不由全部自動候選直接生成評估結論。",
              "- `ACCEPT`：來源追蹤為 source→fact→element→candidate→question 圖，不以 citation 命中判定適用。",
              "- `ACCEPT`：assertion、verification、element state 分離；UNKNOWN promotion 與 D 案矛盾消失為 hard finding。",
              "- `ACCEPT_WITH_MODIFICATIONS`：法律時間與外部法源在本輪維持 UNKNOWN/NOT_USED，不以網路補值。", "",
              "## 未執行", "", "- LLM、資料庫、HTTP、前端、歷史 revision、正式端到端：`NOT_RUN`。", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run trace-first Taiwan legal offline evaluation.")
    parser.add_argument("--fixture", type=Path, default=FIXTURE_PATH)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    try:
        trace = run_evaluation(fixture_path=args.fixture, repetitions=args.repetitions)
    except Exception as exc:
        print(json.dumps({"status": "ERROR", "type": type(exc).__name__, "message": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    if not args.no_write:
        TRACE_PATH.write_text(json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        REPORT_PATH.write_text(render_report(trace), encoding="utf-8")
    print(json.dumps({"overall": trace["overall"], "determinism": trace["determinism"],
                      "cases": [{"case_id": case["case_id"], "first_divergence_stage": case["first_divergence_stage"],
                                 "hard_findings": case["hard_findings"]} for case in trace["cases"]]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
