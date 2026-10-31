"""Tests for agent verification loop skeleton."""

from __future__ import annotations

from app.agent_loop import AgentLoopRun, ErrorPattern, LoopDecision, StepObservation
from app.mcp_verification import VerificationStatus


def test_fail_closed_on_mcp_unavailable():
    run = AgentLoopRun(task_id="t1")
    run.observe(
        StepObservation(
            action="search_taiwan_laws",
            ok=False,
            mcp_status=VerificationStatus.MCP_UNAVAILABLE.value,
        )
    )
    d = run.verify_and_decide()
    assert d == LoopDecision.FAIL_CLOSED


def test_legal_cite_without_mcp_record_fails_closed():
    run = AgentLoopRun(task_id="t2")
    run.observe(StepObservation(action="draft", ok=True))
    d = run.verify_and_decide(require_mcp_when_legal_cite=True, legal_cite_present=True)
    assert d == LoopDecision.FAIL_CLOSED


def test_tests_failed_retry():
    run = AgentLoopRun(task_id="t3")
    run.observe(StepObservation(action="pytest", ok=False, exit_code=1))
    d = run.verify_and_decide(tests_passed=False)
    assert d == LoopDecision.RETRY


def test_pass_still_not_legal_proof():
    run = AgentLoopRun(task_id="t4")
    run.observe(
        StepObservation(
            action="search_taiwan_laws",
            ok=True,
            mcp_status=VerificationStatus.VERIFIED.value,
        )
    )
    d = run.verify_and_decide()
    assert d == LoopDecision.PASS
    assert "人工" in run.to_dict()["disclaimer"]


def test_sediment_requires_human_flag():
    run = AgentLoopRun(task_id="t5")
    run.propose_sediment(
        ErrorPattern(
            pattern_id="fabricated-cite",
            description="無 MCP 卻寫條文",
            proposed_skill_or_test="strengthen search-taiwan-laws skill",
        )
    )
    assert run.error_patterns[0].approved_for_sediment is False
