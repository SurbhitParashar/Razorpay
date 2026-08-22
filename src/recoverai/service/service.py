from __future__ import annotations

from recoverai.agent.orchestrator import RecoveryAgent
from recoverai.recovery.models import RecoveryAction
from recoverai.service.schemas import (
    RecoveryRequestSchema,
    RecoveryResponseSchema,
)


class RecoveryService:
    def __init__(self, agent: RecoveryAgent) -> None:
        self.agent = agent

    def recover(
        self,
        request: RecoveryRequestSchema,
    ) -> RecoveryResponseSchema:
        execution = self.agent.execute(
            payment_id=request.payment_id,
            payment_amount_inr=request.amount_inr,
            recovery_probability=request.recovery_probability,
            attempt_number=request.attempt_number,
        )

        decision = execution.decision

        return RecoveryResponseSchema(
            payment_id=request.payment_id,
            decision=decision.action,
            execution_status=execution.result.status,
            recovered_amount_inr=execution.result.recovered_amount_inr,
            expected_net_value_inr=decision.expected_net_value_inr,
            reason=execution.result.reason
            if decision.action is RecoveryAction.RECOVER
            else decision.reason,
            payment_link=execution.result.payment_link,
        )
