"""Counterfactual reasoning (borrowed from Legal-Skills-Chinese counterfactual-reasoning).

Evaluates: 'If a certain fact/behavior did not exist, how would the legal
outcome differ?' Used for:
  - Causal determination (因果關係認定)
  - Responsibility allocation (責任比例分配)
  - Damage scope (損害範圍界定)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CounterfactualScenario:
    scenario_id: str
    removed_fact: str
    original_outcome: str
    counterfactual_outcome: str
    causal_link: bool  # True if removing the fact changes the outcome
    reasoning: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_counterfactual(
    fact_key: str,
    fact_value: Any,
    dependent_outcomes: list[str],
    independent_outcomes: list[str],
) -> CounterfactualScenario:
    """Evaluate a counterfactual scenario.

    Args:
        fact_key: The fact to hypothetically remove.
        fact_value: The fact's current value.
        dependent_outcomes: Outcomes that depend on this fact.
        independent_outcomes: Outcomes that do not depend on this fact.

    Returns:
        CounterfactualScenario with causal_link determination.
    """
    causal_link = len(dependent_outcomes) > 0
    original = f"事實 '{fact_key}' 存在 → {', '.join(dependent_outcomes + independent_outcomes)}"
    counterfactual = (
        f"若 '{fact_key}' 不存在 → {', '.join(independent_outcomes)}"
        if independent_outcomes
        else f"若 '{fact_key}' 不存在 → 無法認定"
    )
    reasoning = (
        f"移除 '{fact_key}' 後，{'、'.join(dependent_outcomes)} 將無法成立；"
        f"{'、'.join(independent_outcomes)} 不受影響。"
        if dependent_outcomes
        else f"移除 '{fact_key}' 後，所有結果均不受影響，因果連結不存在。"
    )
    return CounterfactualScenario(
        scenario_id=f"cf:{fact_key}",
        removed_fact=fact_key,
        original_outcome=original,
        counterfactual_outcome=counterfactual,
        causal_link=causal_link,
        reasoning=reasoning,
    )


def assess_causal_chain(facts: list[dict[str, Any]], outcome: str) -> list[CounterfactualScenario]:
    """Assess causal chain by testing each fact's counterfactual impact."""
    scenarios = []
    for f in facts:
        fk = f.get("fact_key", f.get("id", "unknown"))
        # Heuristic: if fact has element_refs, it's likely causal
        deps = f.get("dependent_outcomes", [outcome])
        indeps = f.get("independent_outcomes", [])
        scenarios.append(evaluate_counterfactual(fk, f.get("value"), deps, indeps))
    return scenarios