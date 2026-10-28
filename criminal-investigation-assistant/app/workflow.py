from __future__ import annotations

from typing import Any

from .domain import (
    add_attachment_metadata,
    complete_gate2,
    confirm_answers,
    confirm_gate1,
    rebase_source_pack,
    set_case_numbers,
    start_suspect,
    update_gate1_facts,
    update_confirmed_answers,
    update_intake,
)
from .question_bank import QuestionBank


class Workflow:
    def __init__(self, bank: QuestionBank):
        self.bank = bank

    def apply(self, case: dict[str, Any], action: str, payload: dict[str, Any]) -> dict[str, Any]:
        source_current = (
            case.get("source_pins", {}).get("question_bank") == self.bank.fingerprint
            and case.get("source_pins", {}).get("company_templates") == self.bank.template_fingerprint
        )
        if action == "REBASE_SOURCE_PACK":
            return rebase_source_pack(case, self.bank)
        if not source_current:
            raise ValueError("案件來源版本已變更，請先更新來源版本並重新檢查")
        if action == "UPDATE_INTAKE":
            return update_intake(case, payload, self.bank)
        if action == "ADD_ATTACHMENT_METADATA":
            return add_attachment_metadata(case, payload)
        if action == "CONFIRM_GATE1":
            return confirm_gate1(case, self.bank)
        if action == "UPDATE_GATE1_FACTS":
            return update_gate1_facts(case, payload, self.bank)
        if action == "CONFIRM_ANSWERS":
            return confirm_answers(case, payload, self.bank)
        if action == "UPDATE_CONFIRMED_ANSWERS":
            return update_confirmed_answers(case, payload, self.bank)
        if action == "COMPLETE_GATE2":
            return complete_gate2(case, self.bank)
        if action == "SET_CASE_NUMBERS":
            return set_case_numbers(case, payload)
        if action == "START_SUSPECT":
            return start_suspect(case, self.bank, transfer=False)
        if action == "START_TRANSFER":
            return start_suspect(case, self.bank, transfer=True)
        raise ValueError(f"不支援的 action：{action}")
