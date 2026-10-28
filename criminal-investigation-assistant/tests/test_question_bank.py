from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from app.question_bank import QuestionBank, QuestionBankError
from app.domain import _classify_route_element, _route_element_key, _route_element_questions


ROOT = Path(__file__).resolve().parents[1]


def test_compiler_check_is_clean_and_deterministic():
    command = [sys.executable, "-X", "utf8", "tools/compile_questions.py", "--check"]
    first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert first.stdout == second.stdout


def test_exactly_fifteen_families_and_three_roles():
    bank = QuestionBank()
    families = bank.families()
    assert len(families) == 15
    assert all(item["question_count"] >= 18 for item in families)
    for family in families:
        roles = {
            record["role"] for record in bank.bank["records"]
            if record["family_id"] == family["family_id"]
        }
        assert roles == {"victim", "suspect", "witness"}


def test_records_are_normalized_and_not_marked_human_legal_approved():
    bank = QuestionBank()
    for record in bank.bank["records"]:
        assert isinstance(record["legal_target_route_id"], str)
        assert isinstance(record["precondition_id"], str)
        assert record["legal_review_status"] != "HUMAN_LEGAL_APPROVED"
        assert record["text"].count("？") <= 1


def test_runtime_loader_rejects_unexpected_report(tmp_path: Path):
    runtime = tmp_path / "data" / "runtime"
    runtime.mkdir(parents=True)
    for name in ("question_bank.json", "source_manifest.json", "route_coverage.json"):
        (runtime / name).write_bytes((ROOT / "data" / "runtime" / name).read_bytes())
    (runtime / "INVENTORY_REPORT.md").write_text("audit", encoding="utf-8")
    with pytest.raises(QuestionBankError, match="unexpected runtime data"):
        QuestionBank(runtime)


def test_no_audit_or_review_source_is_allowlisted():
    lock = json.loads((ROOT / "data" / "runtime" / "source_manifest.json").read_text(encoding="utf-8"))
    for source in lock["sources"]:
        parts = {part.lower() for part in Path(source["path"]).parts}
        assert not parts.intersection({"audit", "review", "evidence"})


def test_all_310_snapshot_child_routes_have_three_role_draft_coverage():
    bank = QuestionBank()
    records = bank.coverage["records"]
    snapshot = [record for record in records if record["route_resolution_status"] == "SNAPSHOT_CHILD_ROUTE"]
    child_ids = {record["route_id"] for record in snapshot}
    assert bank.coverage["snapshot_parent_count"] == 44
    assert bank.coverage["snapshot_child_count"] == 310
    assert len(child_ids) == 310
    assert len(snapshot) == 930
    for child_id in child_ids:
        assert {record["role"] for record in snapshot if record["route_id"] == child_id} == {
            "victim", "suspect", "witness",
        }


def test_four_extension_routes_remain_blocked_not_counted_as_snapshot_children():
    bank = QuestionBank()
    blocked = [record for record in bank.coverage["records"] if record["coverage_status"] == "BLOCKED"]
    assert {record["route_id"] for record in blocked} == {
        "firearms", "organized_crime", "money_laundering", "stolen_goods",
    }
    assert all(record["route_resolution_status"] == "BLOCKED_NO_FORMAL_CROSSWALK" for record in blocked)


def test_child_route_index_exposes_fact_elements_and_source_fields():
    bank = QuestionBank()
    children = bank.child_routes("theft")
    assert len(children) == 4
    assert all(child["fact_elements"] for child in children)
    assert all(child["law_name"] and child["article_no"] for child in children)
    assert all(child["law_last_amended"] == "2026-07-22" for child in children)
    assert all(child["law_effective_date"] == "NOT_SEPARATELY_REPORTED" for child in children)
    assert all(child["law_pcode"] == "C0000001" for child in children)
    assert all(child["article_verification_status"] == "OFFICIAL_CURRENT_ARTICLE_EXISTS" for child in children)
    assert all(child["article_verified_at"].startswith("2026-10-28") for child in children)
    assert all(len(child["source_version"]) == 16 for child in children)


def test_all_snapshot_routes_have_official_current_article_existence_verification():
    bank = QuestionBank()
    snapshot_parents = {
        record["parent_route_id"] for record in bank.bank["records"]
        if record.get("route_resolution_status") == "SNAPSHOT_CHILD_ROUTE"
    }
    children = [
        child for parent in snapshot_parents for child in bank.child_routes(parent)
        if child["route_resolution_status"] == "SNAPSHOT_CHILD_ROUTE"
    ]
    assert len(children) == 310
    assert all(child["article_verification_status"] == "OFFICIAL_CURRENT_ARTICLE_EXISTS" for child in children)


def test_official_article_corrections_overlay_does_not_mutate_snapshot_contract():
    bank = QuestionBank()
    aggravated = next(child for child in bank.child_routes("aggravated_theft") if child["route_id"] == "aggravated_theft_321")
    complaint = next(child for child in bank.child_routes("injury") if child["route_id"] == "injury_287_complaint")
    liberty = next(child for child in bank.child_routes("liberty") if child["route_id"] == "liberty_302_1_aggravated_deprivation")
    assert any("結夥三人以上" in element for element in aggravated["fact_elements"])
    assert any("行為人是否為公務員" in element for element in complaint["fact_elements"])
    assert any("第一款至第四款" in element for element in liberty["fact_elements"])
    assert {aggravated["correction_status"], complaint["correction_status"], liberty["correction_status"]} == {
        "OFFICIAL_ARTICLE_CORRECTED"
    }


def test_second_batch_official_article_corrections_are_applied():
    bank = QuestionBank()
    expected_phrases = {
        ("forgery", "forgery_218_official_seal"): "如屬盜用",
        ("privacy", "privacy_315_2_profit_facilitation_distribution"): "製造、散布",
        ("privacy", "privacy_319_1_nonconsensual_sexual_image"): "意圖營利、散布",
        ("privacy", "privacy_319_2_coerced_sexual_image"): "意圖營利、散布",
        ("fraud", "fraud_339_4_aggravated"): "政府機關或公務員",
        ("computer", "computer_362_malware"): "實際用於犯本章之罪",
    }
    for (parent, route_id), phrase in expected_phrases.items():
        child = next(item for item in bank.child_routes(parent) if item["route_id"] == route_id)
        assert child["correction_status"] == "OFFICIAL_ARTICLE_CORRECTED"
        assert any(phrase in element for element in child["fact_elements"])


def test_third_batch_official_article_corrections_are_applied():
    bank = QuestionBank()
    expected_phrases = {
        ("drugs", "drugs_4_manufacture_transport_sale"): "專供製造、施用毒品之器具",
        ("drugs", "drugs_5_possession_intent_sale"): "專供製造、施用毒品之器具",
        ("drugs", "drugs_6_force_use"): "非法方法使人施用",
        ("drugs", "drugs_9_aggravation"): "成年人對未成年人販賣毒品",
        ("sexual", "sexual_227_1_youth_mitigation"): "十八歲以下",
        ("trafficking", "trafficking_29_sexual_exploitation"): "是否另有意圖營利",
        ("trafficking", "trafficking_30_forced_labor"): "是否另有意圖營利",
        ("trafficking", "trafficking_31_exploitative_labor_crime"): "是否另有意圖營利",
        ("trafficking", "trafficking_32_organ_removal"): "是否另有意圖營利",
        ("juvenile", "juvenile_27_65_74_criminal"): "被害人訴訟參與不適用",
    }
    for (parent, route_id), phrase in expected_phrases.items():
        child = next(item for item in bank.child_routes(parent) if item["route_id"] == route_id)
        assert child["correction_status"] == "OFFICIAL_ARTICLE_CORRECTED"
        assert any(phrase in element for element in child["fact_elements"])

    force_use = next(item for item in bank.child_routes("drugs") if item["route_id"] == "drugs_6_force_use")
    assert not any("死亡或重傷" in element for element in force_use["fact_elements"])


def test_fourth_batch_official_article_corrections_are_applied():
    bank = QuestionBank()
    expected_phrases = {
        ("disorder", "disorder_150_group_violence"): "公眾或交通往來",
        ("securities", "securities_201_securities"): "行使偽造或變造",
        ("securities", "securities_201_1_payment_card"): "行使偽造或變造",
        ("securities", "securities_202_stamp"): "塗抹註銷符號",
        ("securities", "securities_203_ticket"): "行使偽造或變造客票",
        ("obscenity", "obscenity_234_public_act"): "是否另有意圖營利",
        ("marriage", "marriage_240_consenting_abduction"): "是否另有營利",
        ("marriage", "marriage_241_abduction"): "和誘未滿十六歲",
        ("graves_religion", "graves_247_body"): "對遺骨、遺髮",
        ("gambling", "gambling_269_lottery"): "未經政府允准而發行彩票",
    }
    for (parent, route_id), phrase in expected_phrases.items():
        child = next(item for item in bank.child_routes(parent) if item["route_id"] == route_id)
        assert child["correction_status"] == "OFFICIAL_ARTICLE_CORRECTED"
        assert any(phrase in element for element in child["fact_elements"])

    insult = next(item for item in bank.child_routes("obstruction") if item["route_id"] == "obstruction_140_insult_official")
    assert any("妨害公務之主觀目的" in element for element in insult["fact_elements"])
    assert any("足以影響公務員執行公務" in element for element in insult["fact_elements"])
    assert not any("公然侮辱職務" in element for element in insult["fact_elements"])


def test_constitutional_narrowing_and_invalidated_route_are_fail_closed():
    bank = QuestionBank()
    insult = next(item for item in bank.child_routes("obstruction") if item["route_id"] == "obstruction_140_insult_official")
    assert insult["constitutional_status"] == "CONSTITUTIONALLY_NARROWED"
    assert insult["constitutional_decision"] == "113年憲判字第5號"

    snapshot = json.loads((ROOT / "legal_sources" / "routes.snapshot.json").read_text(encoding="utf-8"))
    obstruction = next(item for item in snapshot["routes"] if item["id"] == "obstruction")
    excluded = next(item for item in obstruction["excluded_routes"] if item["id"] == "obstruction_141_1_false_statement")
    assert excluded["status"] == "UNCONSTITUTIONAL_INVALIDATED"
    assert not any(item["route_id"].startswith("obstruction_141_1") for item in bank.child_routes("obstruction"))


def test_every_child_route_fact_element_has_same_role_question_type_coverage():
    bank = QuestionBank()
    records = [
        item for item in bank.bank["records"]
        if item.get("route_resolution_status") == "SNAPSHOT_CHILD_ROUTE"
    ]
    question_types = {}
    for record in records:
        question_types.setdefault((record["legal_target_route_id"], record["role"]), set()).add(record["element_type"])
    missing = []
    seen = set()
    for record in records:
        key = (record["legal_target_route_id"], record["role"])
        if key in seen:
            continue
        seen.add(key)
        for element in record.get("route_fact_elements", []):
            element_type = _classify_route_element(element)
            if element_type not in question_types[key]:
                missing.append((record["legal_target_route_id"], record["role"], element_type, element))
    assert missing == []


def test_every_snapshot_fact_element_has_a_direct_route_question_mapping_for_all_roles():
    bank = QuestionBank()
    parent_ids = {
        record["parent_route_id"] for record in bank.bank["records"]
        if record.get("route_resolution_status") == "SNAPSHOT_CHILD_ROUTE"
    }
    children = [child for parent in parent_ids for child in bank.child_routes(parent)]
    expected_keys = {
        _route_element_key(child["route_id"], element)
        for child in children for element in child["fact_elements"]
    }
    candidate = {
        "child_routes": [
            {
                "route_id": child["route_id"],
                "name": child["name"],
                "element_gaps": [
                    {
                        "element": element,
                        "element_type": _classify_route_element(element),
                        "route_element_key": _route_element_key(child["route_id"], element),
                        "status": "UNKNOWN",
                    }
                    for element in child["fact_elements"]
                ],
            }
            for child in children
        ]
    }
    for role in ("victim", "suspect", "witness"):
        questions = _route_element_questions({"active_role": role, "candidates": [candidate]})
        covered_keys = {key for question in questions for key in question["route_element_keys"]}
        assert covered_keys == expected_keys
        assert all(question["text"].count("？") == 1 for question in questions)
        assert all(question["requirement"] == "CONDITIONAL" for question in questions)


def test_company_templates_are_semantically_split_and_hash_locked():
    bank = QuestionBank()
    assert len(bank.template_questions("victim")) == 30
    assert len(bank.template_questions("suspect")) == 29
    assert len(bank.template_questions("transfer")) == 36
    for role in ("victim", "suspect", "transfer"):
        for question in bank.template_questions(role):
            assert question["editorial_status"] == "COMPANY_VERBATIM_LOCKED"
            assert question["updates_candidate_facts"] is False
            assert question["text"].count("？") <= 1


def test_conditional_procedure_modules_are_fail_closed_until_activated():
    bank = QuestionBank()
    inactive = bank.questions(role="victim", route_ids=["injury"], active_preconditions={"NONE"})
    active = bank.questions(
        role="victim",
        route_ids=["injury"],
        active_preconditions={"NONE", "DOMESTIC_RELATIONSHIP_CONFIRMED"},
    )
    assert not any(item["question_id"].startswith("M-DV-") for item in inactive)
    assert any(item["question_id"].startswith("M-DV-") for item in active)
