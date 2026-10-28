"""Compile a reviewed question-family Markdown template into a long-table JSON draft.

The Markdown file remains the human-editable source.  The generated JSON is a
deterministic, design-only artifact and is never loaded by the runtime question
pipeline unless a separate integration change explicitly enables it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


MAIN_SECTION_ROLES = {
    "三、被害人筆錄": "victim",
    "四、涉嫌人筆錄": "suspect",
    "五、證人筆錄": "witness_review_only",
}

SOURCE_ROLE_MAP = {
    "被害人": "victim",
    "涉嫌人": "suspect",
    "證人": "witness_review_only",
}

ALL_TEMPLATE_ROLES = ["victim", "suspect", "witness_review_only"]

FACT_TARGET_BY_ID = {
    "V01": "event_sequence",
    "V02": "event_time",
    "V03": "event_place",
    "V04": "party_relationship",
    "V05": "precipitating_events",
    "V06": "alleged_conduct_sequence",
    "V07": "force_method",
    "V08": "instrument_used",
    "V09": "targeted_body_area_and_frequency",
    "V10": "conduct_duration_and_cessation",
    "V11": "participant_conduct",
    "V12": "witness_presence",
    "V13": "contemporaneous_statements",
    "V14": "victim_response",
    "V15": "injury_description",
    "V16": "medical_treatment_and_causation",
    "V17": "medical_documentation",
    "V18": "recovery_and_functional_impact",
    "V19": "injury_or_scene_images",
    "V20": "surveillance_or_recordings",
    "V21": "property_damage",
    "V22": "prior_conflicts",
    "V23": "suspect_identification_timing",
    "V24": "post_event_contact_or_compensation",
    "V25": "complaint_intent",
    "V26": "additional_evidence_or_information",
    "S01": "presence_and_activity",
    "S02": "party_relationship",
    "S03": "precipitating_events",
    "S04": "event_sequence",
    "S05": "alleged_conduct_sequence",
    "S06": "instrument_used",
    "S07": "targeted_body_area_and_frequency",
    "S08": "intent_at_time",
    "S09": "injury_causation_and_knowledge",
    "S10": "victim_conduct_and_response",
    "S11": "participant_and_witness_presence",
    "S12": "intoxication_or_substance_state",
    "S13": "post_event_actions",
    "S14": "response_to_allegation",
    "S15": "exculpatory_facts_and_evidence",
    "S16": "recordings_or_documents",
    "S17": "settlement_or_compensation_intent",
    "S18": "additional_information",
    "W01": "witness_relationship",
    "W02": "witness_vantage_point",
    "W03": "event_sequence",
    "W04": "heard_statements",
    "W05": "personal_knowledge_basis",
    "W06": "precipitating_events",
    "W07": "observed_conduct_and_instrument",
    "W08": "observed_injury",
    "W09": "participant_and_witness_presence",
    "W10": "post_event_response",
    "W11": "recordings_or_surveillance",
    "W12": "additional_information",
    "E1-1": "party_relationship_and_cohabitation",
    "E1-2": "prior_domestic_abuse_pattern",
    "E1-3": "child_or_family_witness_presence",
    "E1-4": "victim_current_safety",
    "E1-5": "protection_order_status",
    "E1-6": "prior_conflicts",
    "E3-1": "participant_conduct",
    "E3-2": "prior_agreement_or_contact",
    "E3-3": "nonparticipant_or_encouragement_conduct",
    "E3-4": "serious_injury_or_death_causation",
    "E4-1": "activity_at_time",
    "E4-2": "scene_conditions",
    "E4-3": "injury_causation_sequence",
    "E4-4": "precautions_and_attention",
    "E4-5": "other_party_contribution",
    "E5-1": "attack_location_frequency_force",
    "E5-2": "contemporaneous_statements_and_demeanor",
    "E5-3": "cessation_reason",
    "E5-4": "intent_at_time",
    "E5-5": "consequence_awareness",
    "E6-1": "public_official_identity",
    "E6-2": "official_duty_status",
}


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _module_roles(source_roles: str) -> list[str]:
    if source_roles == "全部":
        return list(ALL_TEMPLATE_ROLES)
    roles = []
    for source_role in source_roles.split("、"):
        role = SOURCE_ROLE_MAP.get(source_role.strip())
        if role is None:
            raise ValueError(f"unsupported source role: {source_role}")
        if role not in roles:
            roles.append(role)
    return roles


def _element_type(fact_target: str) -> str:
    if any(token in fact_target for token in ("intent", "awareness", "intoxication")):
        return "mental_state"
    if "causation" in fact_target or "contribution" in fact_target:
        return "causation"
    if any(token in fact_target for token in ("injury", "death", "impact", "damage")):
        return "result"
    if any(token in fact_target for token in ("evidence", "documentation", "recording", "images", "surveillance")):
        return "evidence"
    if any(token in fact_target for token in ("relationship", "identity", "presence", "vantage")):
        return "identity_or_relationship"
    if any(token in fact_target for token in ("complaint", "settlement", "protection_order", "safety")):
        return "procedure_or_protection"
    if any(token in fact_target for token in ("conduct", "force", "instrument", "attack", "activity", "response")):
        return "conduct"
    return "context"


def _legal_targets(fixture: dict, question_id: str, applicability_codes: list[str]) -> list[str]:
    overrides = fixture.get("question_route_overrides", {})
    if question_id in overrides:
        return list(overrides[question_id])
    route_map = fixture.get("source_applicability_route_map", {})
    targets: list[str] = []
    for code in applicability_codes:
        mapped = route_map.get(code)
        if not isinstance(mapped, list) or not mapped:
            raise ValueError(f"missing exact route mapping for {question_id}/{code}")
        for route_id in mapped:
            if route_id not in targets:
                targets.append(route_id)
    return targets


def _precondition_ids(fixture: dict, question_id: str, module_id: str | None = None) -> list[str]:
    if module_id is not None:
        condition_ids = fixture.get("module_precondition_ids", {}).get(module_id, [])
    else:
        condition_ids = fixture.get("question_precondition_ids", {}).get(question_id, [])
    registry = fixture.get("precondition_registry", {})
    unknown = [condition_id for condition_id in condition_ids if condition_id not in registry]
    if unknown:
        raise ValueError(f"unknown precondition ids for {question_id}: {unknown}")
    return list(condition_ids)


def compile_template(source: Path, fixture: dict, common_fixture: dict | None = None) -> dict:
    source_bytes = source.read_bytes()
    lines = source_bytes.decode("utf-8").splitlines()
    current_role: str | None = None
    current_module: str | None = None
    current_module_trigger: str | None = None
    records: list[dict] = []
    gap_rows: list[tuple[str, str, int]] = []
    in_gap_section = False

    module_heading = re.compile(r"^###\s+((?:[A-Z]+-)?E\d+)\s+(.+?)（觸發：(.+)）$")
    main_row = re.compile(r"^(?:[A-Z]+-)?[VSW]\d+$")
    module_row = re.compile(r"^(?:[A-Z]+-)?E\d+-\d+$")
    ownership_by_family = (common_fixture or {}).get("family_common_ownership", {})
    common_ownership = ownership_by_family.get(fixture["family_id"], {})
    fact_target_by_id = fixture.get("fact_target_by_id", FACT_TARGET_BY_ID)

    for line_number, line in enumerate(lines, start=1):
        if line.startswith("## "):
            heading = line[3:].strip()
            in_gap_section = heading.startswith("七、要件缺口檢查表")
            current_role = next(
                (role for marker, role in MAIN_SECTION_ROLES.items() if heading.startswith(marker)),
                None,
            )
            current_module = None
            current_module_trigger = None
            continue

        module_match = module_heading.match(line)
        if module_match:
            current_role = None
            current_module = module_match.group(1)
            current_module_trigger = module_match.group(3).strip()
            continue

        if not line.startswith("|"):
            continue
        cells = _cells(line)
        if in_gap_section and len(cells) == 2:
            if cells[0] not in {"要件", "---"} and not cells[0].startswith("---"):
                gap_rows.append((cells[0], cells[1], line_number))
            continue
        question_id = cells[0] if cells else ""
        if main_row.fullmatch(question_id):
            if current_role is None or len(cells) != 6:
                raise ValueError(f"invalid main question row at line {line_number}")
            text, element_label, source_layer, applicability, precondition = cells[1:]
            fact_target = fact_target_by_id.get(question_id)
            if fact_target is None:
                raise ValueError(f"missing fact_target mapping for {question_id}")
            applicability_codes = [item.strip() for item in applicability.split("、")]
            preconditions = [] if precondition == "—" else [precondition]
            precondition_ids = _precondition_ids(fixture, question_id)
            if bool(preconditions) != bool(precondition_ids):
                raise ValueError(f"precondition mapping mismatch for {question_id}")
            common_owner_ids = list(common_ownership.get(question_id, []))
            records.append({
                "id": question_id,
                "text": text,
                "family_id": fixture["family_id"],
                "target_interview_roles": [current_role],
                "fact_target": fact_target,
                "element_type": _element_type(fact_target),
                "element_label": element_label,
                "layer": "family_skeleton" if source_layer == "核心" else "element_supplement",
                "required_or_optional": "REQUIRED" if source_layer == "核心" else "OPTIONAL",
                "preconditions": preconditions,
                "precondition_ids": precondition_ids,
                "source_applicability_codes": applicability_codes,
                "legal_targets": _legal_targets(fixture, question_id, applicability_codes),
                "legal_target_mapping_status": fixture["route_mapping_status"],
                "runtime_enabled": False,
                "common_owner_ids": common_owner_ids,
                "materialization_policy": "REUSE_COMMON_LAYER" if common_owner_ids else "FAMILY_CANDIDATE",
                "review_status": fixture["review_status"],
                "provenance": {"source": fixture["source_markdown"], "line": line_number},
            })
        elif module_row.fullmatch(question_id):
            if current_module is None or current_module_trigger is None or len(cells) != 3:
                raise ValueError(f"invalid module question row at line {line_number}")
            text, source_roles = cells[1:]
            fact_target = fact_target_by_id.get(question_id)
            if fact_target is None:
                raise ValueError(f"missing fact_target mapping for {question_id}")
            applicability_codes = [current_module]
            common_owner_ids = list(common_ownership.get(question_id, []))
            records.append({
                "id": question_id,
                "text": text,
                "family_id": fixture["family_id"],
                "target_interview_roles": _module_roles(source_roles),
                "fact_target": fact_target,
                "element_type": _element_type(fact_target),
                "element_label": "條件分支補強",
                "layer": "conditional_module",
                "required_or_optional": "CONDITIONAL",
                "preconditions": [current_module_trigger],
                "precondition_ids": _precondition_ids(fixture, question_id, current_module),
                "source_applicability_codes": applicability_codes,
                "legal_targets": _legal_targets(fixture, question_id, applicability_codes),
                "legal_target_mapping_status": fixture["route_mapping_status"],
                "runtime_enabled": False,
                "common_owner_ids": common_owner_ids,
                "materialization_policy": "REUSE_COMMON_LAYER" if common_owner_ids else "FAMILY_CANDIDATE",
                "review_status": fixture["review_status"],
                "provenance": {"source": fixture["source_markdown"], "line": line_number},
            })

    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate question ids in source template")
    missing = sorted(set(fact_target_by_id) - set(ids))
    extra = sorted(set(ids) - set(fact_target_by_id))
    if missing or extra:
        raise ValueError(f"question id mapping mismatch: missing={missing}, extra={extra}")
    unknown_ownership_ids = sorted(set(common_ownership) - set(ids))
    if unknown_ownership_ids:
        raise ValueError(f"common ownership references unknown family ids: {unknown_ownership_ids}")

    records_by_id = {record["id"]: record for record in records}
    coverage_requirements = []
    for index, (element_label, source_refs, line_number) in enumerate(gap_rows, start=1):
        resolved_ids: list[str] = []
        for source_ref in (item.strip() for item in source_refs.split("、")):
            if re.fullmatch(r"(?:[A-Z]+-)?E\d+", source_ref):
                matches = [question_id for question_id in records_by_id if question_id.startswith(source_ref + "-")]
            else:
                matches = [source_ref] if source_ref in records_by_id else []
            if not matches:
                raise ValueError(f"unresolved Gate 2 question reference: {source_ref}")
            for question_id in matches:
                if question_id not in resolved_ids:
                    resolved_ids.append(question_id)
        roles = sorted({
            role
            for question_id in resolved_ids
            for role in records_by_id[question_id]["target_interview_roles"]
        })
        fact_targets = list(dict.fromkeys(
            records_by_id[question_id]["fact_target"] for question_id in resolved_ids
        ))
        coverage_requirements.append({
            "id": f"{fixture.get('coverage_id_prefix', fixture['family_id'] + '_gap')}_{index:02d}",
            "element_label": element_label,
            "source_refs": [item.strip() for item in source_refs.split("、")],
            "question_ids": resolved_ids,
            "target_interview_roles": roles,
            "fact_targets": fact_targets,
            "review_status": fixture["review_status"],
            "provenance": {"source": fixture["source_markdown"], "line": line_number},
        })

    return {
        "schema_version": "question-family-master-v1-draft",
        "document_status": fixture["document_status"],
        "runtime_enabled": False,
        "review_status": fixture["review_status"],
        "family_id": fixture["family_id"],
        "fixture_id": fixture["fixture_id"],
        "source_markdown": fixture["source_markdown"],
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "precondition_registry": fixture["precondition_registry"],
        "record_count": len(records),
        "common_overlap_count": sum(bool(record["common_owner_ids"]) for record in records),
        "records": records,
        "coverage_requirement_count": len(coverage_requirements),
        "coverage_requirements": coverage_requirements,
    }


def _payload(compiled: dict) -> str:
    return json.dumps(compiled, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile a question-family Markdown template")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--common-fixture", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    common_fixture = json.loads(args.common_fixture.read_text(encoding="utf-8"))
    payload = _payload(compile_template(args.source, fixture, common_fixture))
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != payload:
            raise SystemExit("question family master is missing or stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
