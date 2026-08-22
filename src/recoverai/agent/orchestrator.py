from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from recoverai.agent.decision import RecoveryDecision
from recoverai.recovery.executor import RecoveryExecutor
from recoverai.recovery.models import (
    RecoveryAction,
    RecoveryRequest,
    RecoveryResult,
)
from recoverai.recovery.policy import RecoveryPolicy


@dataclass(frozen=True, slots=True)
class AgentExecution:
    decision: RecoveryDecision
    result: RecoveryResult


class RecoveryAgent:
    def __init__(
        self,
        policy: RecoveryPolicy,
        executor: RecoveryExecutor,
    ) -> None:
        self.policy = policy
        self.executor = executor

    def decide(
        self,
        payment_id: str,
        payment_amount_inr: Decimal,
        recovery_probability: float,
    ) -> RecoveryDecision:
        expected_net_value = self.policy.expected_net_value(
            recovery_probability=recovery_probability,
            payment_amount_inr=payment_amount_inr,
        )

        if not self.policy.should_intervene(recovery_probability):
            return RecoveryDecision(
                payment_id=payment_id,
                probability=recovery_probability,
                threshold=self.policy.threshold,
                action=RecoveryAction.NO_ACTION,
                expected_net_value_inr=expected_net_value,
                reason="Recovery probability below intervention threshold.",
            )

        if expected_net_value <= Decimal("0"):
            return RecoveryDecision(
                payment_id=payment_id,
                probability=recovery_probability,
                threshold=self.policy.threshold,
                action=RecoveryAction.NO_ACTION,
                expected_net_value_inr=expected_net_value,
                reason="Expected recovery value does not cover intervention cost.",
            )

        return RecoveryDecision(
            payment_id=payment_id,
            probability=recovery_probability,
            threshold=self.policy.threshold,
            action=RecoveryAction.RECOVER,
            expected_net_value_inr=expected_net_value,
            reason="Recovery probability and expected economic value justify intervention.",
        )

    def execute(
        self,
        payment_id: str,
        payment_amount_inr: Decimal,
        recovery_probability: float,
        attempt_number: int,
    ) -> AgentExecution:
        decision = self.decide(
            payment_id=payment_id,
            payment_amount_inr=payment_amount_inr,
            recovery_probability=recovery_probability,
        )

        request = RecoveryRequest(
            payment_id=payment_id,
            amount_inr=payment_amount_inr,
            recovery_probability=recovery_probability,
            threshold=self.policy.threshold,
            attempt_number=attempt_number,
        )

        result = self.executor.execute(request)

        return AgentExecution(
            decision=decision,
            result=result,
        )
