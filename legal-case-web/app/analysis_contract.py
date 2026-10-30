"""Formal-case compatibility fields for facts, candidates and questions.

This module is deliberately additive.  The existing rule/status fields remain
the runtime compatibility surface; these helpers make their provenance and
meaning explicit without making a legal conclusion.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


ASSERTION_CLASSES = {"ASSERTED", "ADMITTED", "DENIED", "INFERRED", "UNKNOWN"}
SOURCE_TYPES = {"PARTY_STATEMENT", "EVIDENCE", "SYSTEM_INFERENCE", "UNKNOWN"}
VERIFICATION_STATUSES = {"VERIFIED", "UNVERIFIED", "UNKNOWN"}


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _source_type(fact: dict[str, Any]) -> str:
    current = _text(fact.get("source_type"))
    if current in SOURCE_TYPES:
        return current
    if fact.get("fact_status") == "當事人陳述":
        return "PARTY_STATEMENT"
    if fact.get("evidence_refs"):
        return "EVIDENCE"
    if fact.get("machine_status") == "INFERENCE":
        return "SYSTEM_INFERENCE"
    return "UNKNOWN"


def decorate_fact(
    raw: dict[str, Any], *, case_id: str = "", revision_id: int | None = None
) -> dict[str, Any]:
    """Return an additive, provenance-preserving fact representation."""

    fact = deepcopy(raw)
    supplied_class = _text(fact.get("assertion_class"))
    if supplied_class in ASSERTION_CLASSES:
        assertion_class = supplied_class
    elif fact.get("machine_status") == "UNKNOWN" or fact.get("assertion_status") == "UNKNOWN":
        assertion_class = "UNKNOWN"
    else:
        # A source statement is an assertion, not a verified objective fact.
        assertion_class = "ASSERTED"

    supplied_verification = _text(fact.get("verification_status"))
    if supplied_verification in VERIFICATION_STATUSES:
        verification_status = supplied_verification
    elif fact.get("machine_status") == "UNKNOWN":
        verification_status = "UNKNOWN"
    elif fact.get("assertion_status") == "VERIFIED_EVIDENCE":
        verification_status = "VERIFIED"
    else:
        verification_status = "UNVERIFIED"

    fact["source_type"] = _source_type(fact)
    fact["assertion_class"] = assertion_class
    fact["verification_status"] = verification_status
    fact["fact_key_status"] = "CLASSIFIED" if _text(fact.get("fact_key")) else "UNCLASSIFIED"
    fact["provenance"] = {
        "source_ref": fact.get("source_ref", ""),
        "source_excerpt": fact.get("source_excerpt", ""),
        "source_start": fact.get("source_start"),
        "source_end": fact.get("source_end"),
    }
    if case_id and revision_id not in (None, 0):
        fact["case_id"] = case_id
    if revision_id not in (None, 0):
        fact["revision_id"] = revision_id
    return fact


def decorate_facts(
    raw: list[dict[str, Any]], *, case_id: str = "", revision_id: int | None = None
) -> list[dict[str, Any]]:
    """以 ``decorate_fact`` 統一裝飾事實清單（單一契約入口）。

    建案與每個會重建 facts 的更新路徑都必須走這裡，否則同一份摘要會因
    入口不同而缺少 ``fact_key_status``／``provenance`` 等契約欄位。
    """
    return [
        decorate_fact(item, case_id=case_id, revision_id=revision_id)
        for item in raw
        if isinstance(item, dict)
    ]


def _candidate_status(candidate: dict[str, Any]) -> str:
    if candidate.get("candidate_eligibility") == "HINT_ONLY":
        return "LOW_CONFIDENCE"
    if candidate.get("unknown_elements") or candidate.get("unknown_fact_keys"):
        return "UNRESOLVED"
    if candidate.get("candidate_eligibility") == "ELIGIBLE_CANDIDATE":
        return "PRIMARY"
    return "UNRESOLVED"


def decorate_candidate(
    raw: dict[str, Any], *, case_id: str = "", revision_id: int | None = None
) -> dict[str, Any]:
    """Expose candidate/readiness/review dimensions without changing legacy keys."""

    candidate = deepcopy(raw)
    unknown = list(candidate.get("unknown_fact_keys") or [])
    unknown.extend(item for item in candidate.get("unknown_elements") or [] if item not in unknown)
    candidate["candidate_status"] = _candidate_status(candidate)
    candidate["readiness_status"] = "NEEDS_FACTS" if unknown else "READY_FOR_REVIEW"
    candidate["candidate_review_status"] = candidate.get("candidate_review_status") or "PENDING"
    candidate["route_status"] = deepcopy(candidate.get("legal_route_states") or {})
    reasons = list(candidate.get("status_reasons") or [])
    if unknown and "unknown_requirements" not in reasons:
        reasons.append("unknown_requirements")
    if candidate.get("candidate_eligibility") == "HINT_ONLY" and "related_or_hint_route" not in reasons:
        reasons.append("related_or_hint_route")
    candidate["status_change_reason"] = reasons
    candidate["fact_refs"] = {
        "supporting": list(candidate.get("supporting_fact_refs") or []),
        "contradicting": list(candidate.get("contradicting_fact_refs") or []),
        "unknown": unknown,
    }
    candidate["evidence_refs"] = list(candidate.get("evidence_refs") or [])
    if case_id and revision_id not in (None, 0):
        candidate["case_id"] = case_id
    if revision_id not in (None, 0):
        candidate["revision_id"] = revision_id
    return candidate


def _question_type(kind: str) -> str:
    return {
        "core": "CORE",
        "distinguishing": "CANDIDATE_DISTINCTION",
        "supplemental": "CONDITIONAL_FOLLOW_UP",
        "reinforce": "EVIDENCE_CHECK",
        "precedent": "EVIDENCE_CHECK",
    }.get(kind, "GENERAL")


def decorate_question(
    raw: dict[str, Any], *, case_id: str = "", revision_id: int | None = None
) -> dict[str, Any]:
    question = deepcopy(raw)
    meta = deepcopy(question.get("meta") or {})
    targets = [item for item in meta.get("legal_targets") or [] if item != "ALL_ROUTES"]
    question["contract"] = {
        "question_id": question.get("id", ""),
        "case_id": case_id,
        "revision_id": revision_id,
        "gap_id": meta.get("fact_target", ""),
        "candidate_ids": targets,
        "element_ids": list(meta.get("target_elements") or []),
        "question_type": _question_type(str(question.get("kind", ""))),
        "evidence_refs": list(meta.get("evidence_to_verify") or []),
        "follow_up_condition": meta.get("trigger_condition", "always"),
    }
    question["meta"] = meta
    return question


def apply_analysis_contract(case: dict[str, Any], *, revision_id: int | None = None) -> dict[str, Any]:
    """Decorate an existing case in place and return it for workflow chaining."""

    case_id = _text(case.get("case_id"))
    gate1 = case.get("gate1")
    if isinstance(gate1, dict):
        gate1["facts"] = [
            decorate_fact(item, case_id=case_id, revision_id=revision_id)
            for item in gate1.get("facts", [])
            if isinstance(item, dict)
        ]
    case["candidates"] = [
        decorate_candidate(item, case_id=case_id, revision_id=revision_id)
        for item in case.get("candidates", [])
        if isinstance(item, dict)
    ]
    case["questions"] = [
        decorate_question(item, case_id=case_id, revision_id=revision_id)
        for item in case.get("questions", [])
        if isinstance(item, dict)
    ]
    case["analysis_contract"] = {
        "contract_version": "legal-pipeline-v1",
        "case_id": case_id,
        "revision_id": revision_id if revision_id is not None else 0,
        "provenance_preserved": True,
        "legacy_fields_preserved": True,
    }
    return case
