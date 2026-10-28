import json
import re
from pathlib import Path

from tools.question_family_compiler import compile_template
from tools.question_common_compiler import compile_common
from tools.question_family_docs import FAMILY_FILES, build_outputs


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "question_family_catalog.json"
FIXTURE_PATH = ROOT / "data" / "question_family_fixtures" / "injury_family.json"
TEMPLATE_PATH = ROOT / "docs" / "family_templates" / "傷害家族問句樣板.md"
MASTER_PATH = ROOT / "data" / "question_family_master" / "injury_family_questions.json"
CROSSWALK_PATH = ROOT / "data" / "legal_route_crosswalk.json"
LEGAL_EVIDENCE_PATH = ROOT / "docs" / "evidence" / "injury_family_legal_verification_20261027.json"
COMMON_FIXTURE_PATH = ROOT / "data" / "question_family_fixtures" / "common_layer.json"
COMMON_MASTER_PATH = ROOT / "data" / "question_family_master" / "common_questions.json"
QUESTION_BANK_PATH = ROOT / "data" / "question_bank.json"
PROPERTY_FIXTURE_PATH = ROOT / "data" / "question_family_fixtures" / "property_family.json"
PROPERTY_TEMPLATE_PATH = ROOT / "docs" / "family_templates" / "catalog" / "財物取得與毀損家族.md"
PROPERTY_MASTER_PATH = ROOT / "data" / "question_family_master" / "property_family_questions.json"
PROPERTY_LEGAL_EVIDENCE_PATH = ROOT / "docs" / "evidence" / "property_family_legal_verification_20261027.json"


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _table_ids(markdown: str, prefix: str):
    return re.findall(rf"^\|\s*{prefix}\d+\s*\|", markdown, flags=re.MULTILINE)


def test_catalog_is_design_only_and_has_unique_family_ids():
    catalog = _read_json(CATALOG_PATH)
    families = catalog["family_layer"]

    assert catalog["document_status"] == "DESIGN_DRAFT"
    assert catalog["runtime_enabled"] is False
    assert catalog["review_status"] == "HUMAN_REVIEW_REQUIRED"
    family_ids = [family["family_id"] for family in families]
    assert len(family_ids) == len(set(family_ids))
    assert "human_violence" in family_ids
    assert catalog["folder_alignment"]["status"] == "UNKNOWN_REQUIRES_USER_OR_REPOSITORY_MAPPING"


def test_injury_fixture_matches_source_role_tables_and_modules():
    fixture = _read_json(FIXTURE_PATH)
    markdown = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert fixture["document_status"] == "DESIGN_DRAFT"
    assert fixture["runtime_enabled"] is False
    assert fixture["review_status"] == "HUMAN_REVIEW_REQUIRED"
    assert fixture["source_provenance"]["legal_verification"] == "PARTIAL_OFFICIAL_SOURCE_VERIFIED"
    assert fixture["supplement_modules"] == ["E1", "E3", "E4", "E5", "E6"]
    assert "對應要件" in markdown
    assert "層級" in markdown
    assert "適用" in markdown
    assert "前置條件" in markdown

    for role, metadata in fixture["role_tables"].items():
        ids = _table_ids(markdown, metadata["prefix"])
        assert len(ids) == metadata["expected_count"], role

    for module in fixture["supplement_modules"]:
        assert module in markdown


def test_family_fixture_keeps_witness_as_review_only():
    fixture = _read_json(FIXTURE_PATH)

    assert fixture["role_tables"]["witness"]["runtime_role"] == "witness_review_only"
    assert any("internal procedure" in note for note in fixture["notes"])


def test_compiled_injury_family_master_is_current_and_design_only():
    fixture = _read_json(FIXTURE_PATH)
    common_fixture = _read_json(COMMON_FIXTURE_PATH)
    master = _read_json(MASTER_PATH)

    assert master == compile_template(TEMPLATE_PATH, fixture, common_fixture)
    assert master["record_count"] == 78
    assert master["runtime_enabled"] is False
    assert all(record["runtime_enabled"] is False for record in master["records"])
    assert all(record["review_status"] == "HUMAN_REVIEW_REQUIRED" for record in master["records"])
    assert all(record["legal_targets"] for record in master["records"])
    assert all(
        record["legal_target_mapping_status"] == "DRAFT_EXACT_CHILD_ROUTE_MAPPING"
        for record in master["records"]
    )


def test_compiled_master_has_required_long_table_attributes_and_role_pairing():
    master = _read_json(MASTER_PATH)
    required = {
        "id",
        "text",
        "family_id",
        "target_interview_roles",
        "fact_target",
        "element_type",
        "layer",
        "required_or_optional",
        "preconditions",
        "precondition_ids",
        "legal_targets",
        "provenance",
        "review_status",
        "common_owner_ids",
        "materialization_policy",
    }
    ids = [record["id"] for record in master["records"]]

    assert len(ids) == len(set(ids))
    assert all(required <= record.keys() for record in master["records"])
    assert sum(record["layer"] == "conditional_module" for record in master["records"]) == 22

    by_target = {}
    for record in master["records"]:
        by_target.setdefault(record["fact_target"], set()).update(record["target_interview_roles"])
    assert by_target["event_sequence"] == {
        "victim",
        "suspect",
        "witness_review_only",
    }
    assert by_target["party_relationship"] == {"victim", "suspect"}
    causation = next(record for record in master["records"] if record["id"] == "S09")
    assert causation["element_type"] == "causation"


def test_compiled_legal_targets_are_existing_exact_child_routes():
    master = _read_json(MASTER_PATH)
    crosswalk = _read_json(CROSSWALK_PATH)
    parent_ids = {route["id"] for route in crosswalk["routes"]}
    child_ids = {
        child["id"]
        for route in crosswalk["routes"]
        for child in route.get("child_routes", [])
    }
    targets = {
        route_id
        for record in master["records"]
        for route_id in record["legal_targets"]
    }

    assert targets <= child_ids
    assert not targets & parent_ids
    assert "injury_277_general" in targets
    assert "injury_287_complaint" in targets
    assert "homicide_271_intentional" in targets
    assert "domestic_2_classification" in targets


def test_gate2_gap_table_compiles_to_valid_cross_role_coverage_matrix():
    master = _read_json(MASTER_PATH)
    record_ids = {record["id"] for record in master["records"]}

    assert master["coverage_requirement_count"] == 10
    assert all(set(requirement["question_ids"]) <= record_ids for requirement in master["coverage_requirements"])
    assert all(requirement["fact_targets"] for requirement in master["coverage_requirements"])

    conduct = next(
        requirement
        for requirement in master["coverage_requirements"]
        if requirement["element_label"] == "行為（傷害動作）"
    )
    assert set(conduct["target_interview_roles"]) == {
        "victim",
        "suspect",
        "witness_review_only",
    }
    group_fight = next(
        requirement
        for requirement in master["coverage_requirements"]
        if requirement["element_label"] == "共犯、聚眾"
    )
    assert {"E3-1", "E3-2", "E3-3", "E3-4"} <= set(group_fight["question_ids"])


def test_preconditions_have_stable_ids_and_remain_manual_or_human_gated():
    master = _read_json(MASTER_PATH)
    registry = master["precondition_registry"]

    for record in master["records"]:
        assert bool(record["preconditions"]) == bool(record["precondition_ids"])
        assert set(record["precondition_ids"]) <= registry.keys()

    evaluations = {entry["evaluation"] for entry in registry.values()}
    assert evaluations <= {
        "MANUAL_FACT_SELECTION",
        "MANUAL_MODULE_SELECTION",
        "HUMAN_LEGAL_REVIEW",
    }
    complaint = next(record for record in master["records"] if record["id"] == "V25")
    assert complaint["precondition_ids"] == ["complaint_requirement_applicability_review"]
    homicide_module = next(record for record in master["records"] if record["id"] == "E5-1")
    assert homicide_module["precondition_ids"] == ["possible_homicidal_intent_indicated"]


def test_legal_verification_is_partial_and_preserves_unknown_internal_procedure():
    fixture = _read_json(FIXTURE_PATH)
    evidence = _read_json(LEGAL_EVIDENCE_PATH)

    assert evidence["status"] == "PARTIAL_OFFICIAL_SOURCE_VERIFIED"
    assert evidence["runtime_legal_conclusion"] is False
    assert evidence["human_review_required"] is True
    assert fixture["source_provenance"]["legal_verification_evidence"] == (
        "docs/evidence/injury_family_legal_verification_20261027.json"
    )
    assert any("internal witness-oath" in item for item in evidence["not_verified"])
    assert any(source["pcode"] == "C0000001" and "10(4)" in source["verified_articles"] for source in evidence["sources"])
    assert any(source["pcode"] == "C0010001" and "196-1" in source["verified_articles"] for source in evidence["sources"])


def test_common_master_is_current_and_keeps_witness_review_only():
    fixture = _read_json(COMMON_FIXTURE_PATH)
    master = _read_json(COMMON_MASTER_PATH)

    assert master == compile_common(QUESTION_BANK_PATH, fixture)
    assert master["record_count"] == 40
    assert master["existing_runtime_record_count"] == 34
    assert master["review_only_record_count"] == 6
    witness = [record for record in master["records"] if record["target_interview_role"] == "witness_review_only"]
    assert len(witness) == 6
    assert all(record["runtime_enabled"] is False for record in witness)


def test_family_common_ownership_references_existing_common_ids():
    family_master = _read_json(MASTER_PATH)
    common_master = _read_json(COMMON_MASTER_PATH)
    common_ids = {record["id"] for record in common_master["records"]}
    overlaps = [record for record in family_master["records"] if record["common_owner_ids"]]

    assert family_master["common_overlap_count"] == 12
    assert len(overlaps) == 12
    assert all(set(record["common_owner_ids"]) <= common_ids for record in overlaps)
    assert all(record["materialization_policy"] == "REUSE_COMMON_LAYER" for record in overlaps)
    assert all(
        record["materialization_policy"] == "FAMILY_CANDIDATE"
        for record in family_master["records"]
        if not record["common_owner_ids"]
    )


def test_every_family_has_a_current_readable_markdown_file():
    catalog = _read_json(CATALOG_PATH)
    output_dir = ROOT / "docs" / "family_templates"
    expected_outputs = build_outputs(catalog, output_dir)

    assert len(FAMILY_FILES) == 12
    assert {family["family_id"] for family in catalog["family_layer"]} == set(FAMILY_FILES)
    for path, expected in expected_outputs.items():
        assert path.read_text(encoding="utf-8") == expected

    for family_id, relative_path in FAMILY_FILES.items():
        markdown = (output_dir / relative_path).read_text(encoding="utf-8")
        assert family_id in markdown
        assert "Human Gate" in markdown


def test_property_family_master_is_current_and_has_three_role_tables():
    fixture = _read_json(PROPERTY_FIXTURE_PATH)
    common_fixture = _read_json(COMMON_FIXTURE_PATH)
    master = _read_json(PROPERTY_MASTER_PATH)

    assert master == compile_template(PROPERTY_TEMPLATE_PATH, fixture, common_fixture)
    assert master["record_count"] == 70
    assert master["coverage_requirement_count"] == 10
    assert master["common_overlap_count"] == 9
    assert sum(record["id"].startswith("P-V") for record in master["records"]) == 18
    assert sum(record["id"].startswith("P-S") for record in master["records"]) == 14
    assert sum(record["id"].startswith("P-W") for record in master["records"]) == 10
    assert sum(record["layer"] == "conditional_module" for record in master["records"]) == 28
    assert all(record["runtime_enabled"] is False for record in master["records"])


def test_property_family_uses_only_existing_property_child_routes():
    master = _read_json(PROPERTY_MASTER_PATH)
    crosswalk = _read_json(CROSSWALK_PATH)
    property_parents = {"theft", "aggravated_theft", "embezzlement", "damage"}
    allowed = {
        child["id"]
        for route in crosswalk["routes"]
        if route["id"] in property_parents
        for child in route.get("child_routes", [])
    }
    targets = {
        route_id
        for record in master["records"]
        for route_id in record["legal_targets"]
    }

    assert targets <= allowed
    assert not any(route_id.startswith("robbery") for route_id in targets)
    assert "theft_320_1_movable" in targets
    assert "aggravated_theft_321" in targets
    assert "embezzlement_337_lost_property" in targets
    assert "damage_354_property" in targets


def test_property_common_ownership_and_gate2_references_are_valid():
    master = _read_json(PROPERTY_MASTER_PATH)
    common_master = _read_json(COMMON_MASTER_PATH)
    common_ids = {record["id"] for record in common_master["records"]}
    record_ids = {record["id"] for record in master["records"]}
    overlaps = [record for record in master["records"] if record["common_owner_ids"]]

    assert len(overlaps) == 9
    assert all(set(record["common_owner_ids"]) <= common_ids for record in overlaps)
    assert all(
        set(requirement["question_ids"]) <= record_ids
        for requirement in master["coverage_requirements"]
    )
    acquisition = next(
        requirement
        for requirement in master["coverage_requirements"]
        if requirement["element_label"] == "取得或接觸方式"
    )
    assert set(acquisition["target_interview_roles"]) == {
        "victim",
        "suspect",
        "witness_review_only",
    }


def test_property_legal_verification_is_official_but_partial():
    fixture = _read_json(PROPERTY_FIXTURE_PATH)
    evidence = _read_json(PROPERTY_LEGAL_EVIDENCE_PATH)

    assert fixture["source_provenance"]["legal_verification"] == "PARTIAL_OFFICIAL_SOURCE_VERIFIED"
    assert evidence["status"] == "PARTIAL_OFFICIAL_SOURCE_VERIFIED"
    assert evidence["runtime_legal_conclusion"] is False
    assert evidence["human_review_required"] is True
    verified = set(evidence["sources"][0]["verified_articles"])
    assert {"320", "321", "324", "335", "336", "337", "352", "357"} <= verified
    assert any("unlawful appropriation intent" in item for item in evidence["not_verified"])
