"""Quality gate: structured element extraction as pre-reasoning validation.

Borrowed from Legal-Skills-Chinese structured-element-extraction.
Before entering downstream reasoning, all legal elements must be extracted
and validated:
  - Every constitutive element has at least one fact
  - No element is missing
  - All facts are traceable to source
  - Element list is complete (no gaps)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class GateCheck:
    check_name: str
    passed: bool
    message: str
    severity: str = "BLOCK"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QualityGateResult:
    passed: bool
    checks: list[GateCheck] = field(default_factory=list)
    missing_elements: list[str] = field(default_factory=list)
    untraceable_facts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": [c.to_dict() for c in self.checks],
            "missing_elements": self.missing_elements,
            "untraceable_facts": self.untraceable_facts,
        }


def run_quality_gate(
    elements: list[dict[str, Any]],
    facts: list[dict[str, Any]],
) -> QualityGateResult:
    """Run quality gate before reasoning.

    Args:
        elements: List of constitutive elements, each with element_id and required flag.
        facts: List of facts, each with fact_key, element_ref, and source_ref.

    Returns:
        QualityGateResult with pass/fail and detailed checks.
    """
    checks: list[GateCheck] = []
    missing_elements: list[str] = []
    untraceable_facts: list[str] = []

    # 1. Every element must have at least one fact
    element_ids = {e.get("element_id", e.get("id", "")) for e in elements}
    fact_element_refs = {f.get("element_ref", f.get("element_id", "")) for f in facts}

    for eid in element_ids:
        if eid and eid not in fact_element_refs:
            missing_elements.append(eid)
            checks.append(GateCheck(
                f"element_coverage:{eid}", False,
                f"構成要件 '{eid}' 缺少對應事實",
            ))
        else:
            checks.append(GateCheck(
                f"element_coverage:{eid}", True,
                f"構成要件 '{eid}' 已有對應事實",
            ))

    # 2. All facts must be traceable (have source_ref)
    for f in facts:
        fid = f.get("fact_key", f.get("id", "unknown"))
        if not f.get("source_ref") and not f.get("source_excerpt"):
            untraceable_facts.append(fid)
            checks.append(GateCheck(
                f"traceability:{fid}", False,
                f"事實 '{fid}' 缺少來源追溯",
            ))
        else:
            checks.append(GateCheck(
                f"traceability:{fid}", True,
                f"事實 '{fid}' 有來源追溯",
            ))

    # 3. No empty element list
    if not elements:
        checks.append(GateCheck("element_list", False, "構成要件清單為空"))
    else:
        checks.append(GateCheck("element_list", True, f"構成要件清單有 {len(elements)} 項"))

    passed = all(c.passed for c in checks)
    return QualityGateResult(
        passed=passed,
        checks=checks,
        missing_elements=missing_elements,
        untraceable_facts=untraceable_facts,
    )