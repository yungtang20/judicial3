from __future__ import annotations

from copy import deepcopy

import pytest

from app import documents
from app.documents import DocumentError, brief_text, build_interview, roc_text
from app.domain import make_case
from app.question_bank import QuestionBank


def _case():
    case = make_case({
        "event_time": "2026年10月27日10時",
        "location": "臺北市中正區虛擬路1號",
        "summary": "甲將乙的皮夾拿走。",
        "case_kind": "WITH_VICTIM",
    }, QuestionBank())
    case["case_numbers"] = {"proof_number": "TEST-001"}
    return case


def test_roc_year_and_brief_limit():
    assert roc_text("2026年10月27日") == "民國115年10月27日"
    text = brief_text(_case())
    assert "民國115年" in text
    assert len(text) <= 500


def test_brief_rejects_over_limit_without_truncating():
    case = _case()
    case["intake"]["summary"] = "甲" * 501
    with pytest.raises(DocumentError, match="超過 500 字"):
        brief_text(case)


def test_interview_fails_closed_when_actual_render_exceeds_eight_pages(monkeypatch):
    case = _case()
    case["revision"] = 1
    case["answers"]["victim"] = {"T-V001-01": "虛構回答"}
    monkeypatch.setattr(documents, "_page_count", lambda _path: 9)
    with pytest.raises(DocumentError, match="超過 8 頁"):
        build_interview(case, "victim")
