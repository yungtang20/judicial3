"""Test case registry for integration testing (blueprint Phase 8).

Defines 12 standard test scenarios for criminal investigation:
  1. SINGLE_CRIME - basic constitutive elements
  2. MULTI_CRIME - multiple offenses in one case
  3. OFFENSE_CONFUSION - theft vs embezzlement vs lost property
  4. SUBJECTIVE_INTENT - intent, negligence, dolus eventualis
  5. DENIAL_CASE - denial ≠ fact non-existence
  6. CONFESSION_CASE - confession + corroborating evidence
  7. DIGITAL_CRIME - communications, accounts, IP, devices
  8. FINANCIAL_CRIME - accounts, third-party payment, virtual assets
  9. FAVORABLE_EVIDENCE - evidence favorable to suspect
  10. SPECIAL_CASES - juvenile, sexual, domestic violence, organized crime
  11. NO_VICTIM - transfer without victim
  12. MULTI_ACTOR - multiple suspects

Each scenario has:
  - case_summary: original case narrative
  - expected_facts: list of expected fact keys
  - expected_candidates: list of expected candidate offense IDs
  - must_preserve_alternatives: alternative directions that must not be dropped
  - core_issues: expected core issues
  - must_ask_questions: minimum question count
  - forbidden_conclusions: conclusions that must NOT appear
  - expected_document_checks: document format requirements
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class TestCase:
    scenario_id: str
    scenario_type: str
    case_summary: str
    expected_facts: list[str] = field(default_factory=list)
    expected_candidates: list[str] = field(default_factory=list)
    must_preserve_alternatives: list[str] = field(default_factory=list)
    core_issues: list[str] = field(default_factory=list)
    must_ask_min_questions: int = 0
    forbidden_conclusions: list[str] = field(default_factory=list)
    expected_document_checks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Standard test scenarios (blueprint Phase 8)
STANDARD_SCENARIOS: list[TestCase] = [
    TestCase(
        scenario_id="TC-001",
        scenario_type="SINGLE_CRIME",
        case_summary="被告甲於民國113年3月15日，在台北市中山區某便利商店，徒手拿取架上商品後未付款離開。",
        expected_facts=["event_time", "location", "behavior", "object"],
        expected_candidates=["theft"],
        must_preserve_alternatives=[],
        core_issues=["取得方式", "所有權移轉"],
        must_ask_min_questions=5,
        forbidden_conclusions=["被告竊取，構成竊盜"],
    ),
    TestCase(
        scenario_id="TC-002",
        scenario_type="OFFENSE_CONFUSION",
        case_summary="被告乙受託保管被害人丙之手機，後將手機變賣換取現金。",
        expected_facts=["event_time", "location", "behavior", "object", "possession_type"],
        expected_candidates=["theft", "embezzlement"],
        must_preserve_alternatives=["theft", "embezzlement"],
        core_issues=["持有方式", "所有權移轉", "保管約定"],
        must_ask_min_questions=8,
        forbidden_conclusions=["被告侵占，構成侵占"],
    ),
    TestCase(
        scenario_id="TC-003",
        scenario_type="DENIAL_CASE",
        case_summary="被告丁否認竊取被害人戊之財物，但監視器畫面顯示被告曾靠近被害人。",
        expected_facts=["event_time", "location", "behavior", "object"],
        expected_candidates=["theft"],
        must_preserve_alternatives=[],
        core_issues=["否認與證據矛盾"],
        must_ask_min_questions=6,
        forbidden_conclusions=["被告否認，排除犯罪"],
    ),
    TestCase(
        scenario_id="TC-004",
        scenario_type="CONFESSION_CASE",
        case_summary="被告己自白偷取被害人庚之財物，但無其他客觀證據。",
        expected_facts=["event_time", "location", "behavior", "object"],
        expected_candidates=["theft"],
        must_preserve_alternatives=[],
        core_issues=["自白補強"],
        must_ask_min_questions=5,
        forbidden_conclusions=["被告自白，犯罪成立"],
    ),
    TestCase(
        scenario_id="TC-005",
        scenario_type="DIGITAL_CRIME",
        case_summary="被告辛使用被害人壬之帳號登入系統，變更資料並轉帳。",
        expected_facts=["event_time", "behavior", "object", "digital_evidence"],
        expected_candidates=["computer_crime", "fraud"],
        must_preserve_alternatives=["computer_crime", "fraud"],
        core_issues=["帳號使用", "授權範圍"],
        must_ask_min_questions=8,
        forbidden_conclusions=["被告駭客，構成犯罪"],
    ),
    TestCase(
        scenario_id="TC-006",
        scenario_type="FINANCIAL_CRIME",
        case_summary="被告癸透過第三方支付平台轉帳至多個帳戶。",
        expected_facts=["event_time", "behavior", "financial_flow"],
        expected_candidates=["fraud", "money_laundering"],
        must_preserve_alternatives=["fraud", "money_laundering"],
        core_issues=["金流", "犯意"],
        must_ask_min_questions=8,
        forbidden_conclusions=["金流異常，構成洗錢"],
    ),
    TestCase(
        scenario_id="TC-007",
        scenario_type="FAVORABLE_EVIDENCE",
        case_summary="被告子被控竊盜，但有證人證明其當時在其他地點。",
        expected_facts=["event_time", "location", "behavior", "alibi"],
        expected_candidates=["theft"],
        must_preserve_alternatives=[],
        core_issues=["有利證據"],
        must_ask_min_questions=5,
        forbidden_conclusions=["有證人不在場，排除犯罪"],
    ),
    TestCase(
        scenario_id="TC-008",
        scenario_type="NO_VICTIM",
        case_summary="被告丑無被害人案件，涉及毒品持有。",
        expected_facts=["event_time", "location", "behavior", "object"],
        expected_candidates=["drugs"],
        must_preserve_alternatives=[],
        core_issues=["持有", "用途"],
        must_ask_min_questions=5,
        forbidden_conclusions=["持有毒品，構成犯罪"],
    ),
    TestCase(
        scenario_id="TC-009",
        scenario_type="MULTI_CRIME",
        case_summary="被告寅同時涉及竊盜與傷害。",
        expected_facts=["event_time", "location", "behavior", "object", "injury"],
        expected_candidates=["theft", "injury"],
        must_preserve_alternatives=[],
        core_issues=["一行為數罪", "競合"],
        must_ask_min_questions=10,
        forbidden_conclusions=["一行為數罪，全部成立"],
    ),
    TestCase(
        scenario_id="TC-010",
        scenario_type="SUBJECTIVE_INTENT",
        case_summary="被告卯在不確定的情況下拿取他人財物。",
        expected_facts=["event_time", "location", "behavior", "object", "intent"],
        expected_candidates=["theft"],
        must_preserve_alternatives=[],
        core_issues=["故意", "不確定故意"],
        must_ask_min_questions=6,
        forbidden_conclusions=["拿取財物，構成竊盜"],
    ),
]


def get_scenario(scenario_id: str) -> TestCase | None:
    for s in STANDARD_SCENARIOS:
        if s.scenario_id == scenario_id:
            return s
    return None


def get_scenarios_by_type(scenario_type: str) -> list[TestCase]:
    return [s for s in STANDARD_SCENARIOS if s.scenario_type == scenario_type]


def all_scenario_ids() -> list[str]:
    return [s.scenario_id for s in STANDARD_SCENARIOS]