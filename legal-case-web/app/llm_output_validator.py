"""LLM output schema validation (expert strategy §1.8).

All LLM output must pass schema validation before it can be used.
Output must include source_ref for every claim.  Forbidden conclusions
are blocked.  This is a hard gate.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .forbidden_conclusions import scan_forbidden_conclusions


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "errors": self.errors, "warnings": self.warnings}


# Required fields for LLM candidate analysis output
CANDIDATE_OUTPUT_SCHEMA = {
    "required": ["candidates", "source_refs"],
    "candidate_required": ["offense_id", "status", "reason", "source_refs"],
    "allowed_status": {"NEED_REVIEW", "ACTIVE", "LOWERED", "REJECTED"},
}

# Required fields for LLM question generation output
QUESTION_OUTPUT_SCHEMA = {
    "required": ["questions", "source_refs"],
    "question_required": ["question_text", "target_fact", "element_ref", "source_refs"],
}


def validate_candidate_output(output: dict[str, Any]) -> ValidationResult:
    """Validate LLM candidate analysis output against schema."""
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(output, dict):
        return ValidationResult(valid=False, errors=["output must be a dict"], warnings=[])

    # Check required top-level fields
    for field in CANDIDATE_OUTPUT_SCHEMA["required"]:
        if field not in output:
            errors.append(f"missing required field: {field}")

    candidates = output.get("candidates", [])
    if not isinstance(candidates, list):
        errors.append("candidates must be a list")
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    for i, cand in enumerate(candidates):
        if not isinstance(cand, dict):
            errors.append(f"candidate[{i}] must be a dict")
            continue
        for field in CANDIDATE_OUTPUT_SCHEMA["candidate_required"]:
            if field not in cand:
                errors.append(f"candidate[{i}] missing required field: {field}")
        status = cand.get("status")
        if status and status not in CANDIDATE_OUTPUT_SCHEMA["allowed_status"]:
            errors.append(f"candidate[{i}] invalid status: {status}")
        # Check source_refs
        refs = cand.get("source_refs", [])
        if not refs:
            warnings.append(f"candidate[{i}] has no source_refs (traceability gap)")
        # Check for forbidden conclusions in reason text
        reason = cand.get("reason", "")
        if isinstance(reason, str):
            violations = scan_forbidden_conclusions(reason)
            if violations:
                errors.append(f"candidate[{i}] contains forbidden conclusion: {violations[0]['description']}")

    # Check top-level source_refs
    top_refs = output.get("source_refs", [])
    if not top_refs:
        warnings.append("output has no top-level source_refs")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def validate_question_output(output: dict[str, Any]) -> ValidationResult:
    """Validate LLM question generation output against schema."""
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(output, dict):
        return ValidationResult(valid=False, errors=["output must be a dict"], warnings=[])

    for field in QUESTION_OUTPUT_SCHEMA["required"]:
        if field not in output:
            errors.append(f"missing required field: {field}")

    questions = output.get("questions", [])
    if not isinstance(questions, list):
        errors.append("questions must be a list")
        return ValidationResult(valid=False, errors=errors, warnings=warnings)

    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            errors.append(f"question[{i}] must be a dict")
            continue
        for field in QUESTION_OUTPUT_SCHEMA["question_required"]:
            if field not in q:
                errors.append(f"question[{i}] missing required field: {field}")
        refs = q.get("source_refs", [])
        if not refs:
            warnings.append(f"question[{i}] has no source_refs (traceability gap)")
        text = q.get("question_text", "")
        if isinstance(text, str):
            violations = scan_forbidden_conclusions(text)
            if violations:
                errors.append(f"question[{i}] contains forbidden conclusion: {violations[0]['description']}")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)


def validate_json_output(raw_text: str) -> tuple[bool, Any, str]:
    """Parse and validate raw LLM text output as JSON.

    Returns (success, parsed_data, error_message).
    """
    if not isinstance(raw_text, str) or not raw_text.strip():
        return False, None, "empty input"
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        return False, None, f"JSON parse error: {e}"
    return True, data, ""