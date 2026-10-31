"""Agent verification loop skeleton (pstack-inspired).

Execute → Observe → Verify → Decide → optional Sediment proposal.
Does not call external MCP by itself; callers inject outcomes.
Never treats support counts or tool HTTP 200 as legal proof.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from .mcp_verification import VerificationStatus, fail_closed_message


class LoopPhase(str, Enum):
    PLAN = "PLAN"
    EXECUTE = "EXECUTE"
    OBSERVE = "OBSERVE"
    VERIFY = "VERIFY"
    DECIDE = "DECIDE"
    SEDIMENT = "SEDIMENT"


class LoopDecision(str, Enum):
    PASS = "PASS"
    RETRY = "RETRY"
    FAIL_CLOSED = "FAIL_CLOSED"
    NEEDS_HUMAN = "NEEDS_HUMAN"


@dataclass
class StepObservation:
    action: str
    ok: bool
    detail: str = ""
    exit_code: int | None = None
    mcp_status: str | None = None
    artifacts: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ErrorPattern:
    pattern_id: str
    description: str
    count: int = 1
    last_seen: str = ""
    proposed_skill_or_test: str = ""
    approved_for_sediment: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentLoopRun:
    task_id: str
    phase: str = LoopPhase.PLAN.value
    observations: list[StepObservation] = field(default_factory=list)
    decision: str = LoopDecision.NEEDS_HUMAN.value
    decision_reason: str = ""
    error_patterns: list[ErrorPattern] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    finished_at: str = ""

    def observe(self, obs: StepObservation) -> None:
        self.phase = LoopPhase.OBSERVE.value
        self.observations.append(obs)

    def verify_and_decide(
        self,
        *,
        require_mcp_when_legal_cite: bool = False,
        legal_cite_present: bool = False,
        tests_passed: bool | None = None,
    ) -> LoopDecision:
        self.phase = LoopPhase.VERIFY.value
        for obs in self.observations:
            if obs.mcp_status == VerificationStatus.MCP_UNAVAILABLE.value:
                self.decision = LoopDecision.FAIL_CLOSED.value
                self.decision_reason = fail_closed_message(VerificationStatus.MCP_UNAVAILABLE)
                self.phase = LoopPhase.DECIDE.value
                self.finished_at = datetime.now(UTC).isoformat()
                return LoopDecision.FAIL_CLOSED

        if require_mcp_when_legal_cite and legal_cite_present:
            mcp_ok = any(
                o.mcp_status
                in {
                    VerificationStatus.VERIFIED.value,
                    VerificationStatus.VERSION_UNVERIFIED.value,
                    VerificationStatus.NEEDS_REVIEW.value,
                    VerificationStatus.NOT_FOUND.value,
                }
                for o in self.observations
            )
            if not mcp_ok:
                self.decision = LoopDecision.FAIL_CLOSED.value
                self.decision_reason = "出現法源引用但無 MCP 查證紀錄"
                self.phase = LoopPhase.DECIDE.value
                self.finished_at = datetime.now(UTC).isoformat()
                return LoopDecision.FAIL_CLOSED

        if tests_passed is False:
            self.decision = LoopDecision.RETRY.value
            self.decision_reason = "測試未通過，應修正後重跑，不得刪測"
            self.phase = LoopPhase.DECIDE.value
            self.finished_at = datetime.now(UTC).isoformat()
            return LoopDecision.RETRY

        if any(not o.ok for o in self.observations):
            self.decision = LoopDecision.NEEDS_HUMAN.value
            self.decision_reason = "存在失敗觀察，需人工或 RETRY"
            self.phase = LoopPhase.DECIDE.value
            self.finished_at = datetime.now(UTC).isoformat()
            return LoopDecision.NEEDS_HUMAN

        self.decision = LoopDecision.PASS.value
        self.decision_reason = "觀察通過工程檢查；法律結論仍須人工"
        self.phase = LoopPhase.DECIDE.value
        self.finished_at = datetime.now(UTC).isoformat()
        return LoopDecision.PASS

    def propose_sediment(self, pattern: ErrorPattern) -> None:
        self.phase = LoopPhase.SEDIMENT.value
        pattern.approved_for_sediment = False
        if not pattern.last_seen:
            pattern.last_seen = datetime.now(UTC).isoformat()
        self.error_patterns.append(pattern)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "phase": self.phase,
            "observations": [o.to_dict() for o in self.observations],
            "decision": self.decision,
            "decision_reason": self.decision_reason,
            "error_patterns": [e.to_dict() for e in self.error_patterns],
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "disclaimer": "PASS 僅表示工程驗證步驟完成，不表示法律結論成立。",
        }
