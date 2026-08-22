from __future__ import annotations

from recoverai.agent.orchestrator import RecoveryAgent
from recoverai.metrics.recovery import calculate_recovery_metrics
from recoverai.recovery.models import RecoveryAction
from recoverai.recovery.outcome import (
    RecoveryOutcome,
    RecoveryOutcomeStatus,
)
from recoverai.service.schemas import (
    RecoveryMetricsResponseSchema,
    RecoveryOutcomeRequestSchema,
    RecoveryOutcomeResponseSchema,
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

    def record_recovery_outcome(
        self,
        request: RecoveryOutcomeRequestSchema,
    ) -> RecoveryOutcomeResponseSchema:
        outcome = self.agent.executor.record_recovery_outcome(
            payment_id=request.payment_id,
            status=request.status,
            recovered_amount_inr=request.recovered_amount_inr,
            reason=request.reason,
        )

        return RecoveryOutcomeResponseSchema(
            payment_id=outcome.payment_id,
            status=outcome.status,
            recovered_amount_inr=outcome.recovered_amount_inr,
            reason=outcome.reason,
        )

    def get_recovery_metrics(self) -> RecoveryMetricsResponseSchema:
        if self.agent.executor.state_store is None:
            outcomes = []
        else:
            stored_outcomes = self.agent.executor.state_store.list_recovery_outcomes()

            outcomes = [
                RecoveryOutcome(
                    payment_id=outcome.payment_id,
                    status=RecoveryOutcomeStatus(outcome.status),
                    recovered_amount_inr=outcome.recovered_amount_inr,
                    reason=outcome.reason,
                )
                for outcome in stored_outcomes
            ]

        metrics = calculate_recovery_metrics(outcomes)

        return RecoveryMetricsResponseSchema(
            attempted_count=metrics.attempted_count,
            successful_recovery_count=metrics.successful_recovery_count,
            failed_recovery_count=metrics.failed_recovery_count,
            recovered_revenue_inr=metrics.recovered_revenue_inr,
            recovery_rate=metrics.recovery_rate,
        )
