"""Unit tests for stage2 modules: mcp_verification, competing_hypotheses, traceability."""

from __future__ import annotations

from app.competing_hypotheses import (
    CompetingHypotheses,
    FactRef,
    Hypothesis,
    example_custody_property_set,
)
from app.mcp_verification import (
    VerificationStatus,
    append_record,
    build_record,
    classify_mcp_result,
    fail_closed_message,
)
from app.question_traceability import (
    check_orphan_questions_against_facts,
    check_question_traceability,
    build_trace_from_question,
)


def test_classify_mcp_unavailable():
    assert classify_mcp_result(tool_available=False, hit_count=0) == VerificationStatus.MCP_UNAVAILABLE


def test_classify_not_found():
    assert classify_mcp_result(tool_available=True, hit_count=0) == VerificationStatus.NOT_FOUND


def test_classify_version_unverified():
    st = classify_mcp_result(
        tool_available=True,
        hit_count=1,
        source_url="https://example.law",
        version_checked_for_event_date=False,
    )
    assert st == VerificationStatus.VERSION_UNVERIFIED


def test_classify_verified():
    st = classify_mcp_result(
        tool_available=True,
        hit_count=2,
        source_url="https://example.law",
        version_checked_for_event_date=True,
    )
    assert st == VerificationStatus.VERIFIED


def test_append_record():
    case: dict = {}
    rec = build_record(tool="search_taiwan_laws", status=VerificationStatus.NOT_FOUND, query="刑法 320")
    append_record(case, rec)
    assert len(case["mcp_verification_log"]) == 1
    assert case["mcp_verification_log"][0]["status"] == "NOT_FOUND"


def test_fail_closed_message():
    msg = fail_closed_message(VerificationStatus.MCP_UNAVAILABLE)
    assert "不得以模型記憶" in msg


def test_hypothesis_denied_not_false():
    f = FactRef("x", "DENIED")
    assert f.status == "DENIED"
    h = Hypothesis("h1", "test", supporting_facts=[f])
    d = h.to_dict()
    assert d["support_count_is_not_legal_proof"] is True


def test_example_competing_set():
    ch = example_custody_property_set()
    assert len(ch.hypotheses) >= 4
    assert ch.to_dict()["disclaimer"]


def test_trace_build_and_gaps():
    q = {"question_id": "q1", "target_fact": "f1", "element_id": "e1", "offense_id": "c1"}
    t = build_trace_from_question(q)
    assert t.target_fact == "f1"
    gaps = check_question_traceability([{"question_id": "q2"}])
    assert any(g.gap_type == "NO_FACT_LINK" for g in gaps)


def test_orphan_fact():
    gaps = check_orphan_questions_against_facts(
        [{"question_id": "q", "target_fact": "missing"}],
        {"known"},
    )
    assert gaps and gaps[0].gap_type == "ORPHAN_FACT_TARGET"
