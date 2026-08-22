from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from recoverai.recovery.outcome import (
    RecoveryOutcome,
    RecoveryOutcomeStatus,
)


@dataclass(frozen=True, slots=True)
class RecoveryMetrics:
    attempted_count: int
    successful_recovery_count: int
    failed_recovery_count: int
    recovered_revenue_inr: Decimal
    recovery_rate: float


def calculate_recovery_metrics(
    outcomes: Sequence[RecoveryOutcome],
) -> RecoveryMetrics:
    attempted_count = len(outcomes)

    successful_recovery_count = sum(
        outcome.status is RecoveryOutcomeStatus.PAID for outcome in outcomes
    )

    failed_recovery_count = sum(
        outcome.status
        in {
            RecoveryOutcomeStatus.UNPAID,
            RecoveryOutcomeStatus.FAILED,
            RecoveryOutcomeStatus.EXPIRED,
        }
        for outcome in outcomes
    )

    recovered_revenue_inr = sum(
        (outcome.recovered_amount_inr for outcome in outcomes),
        Decimal("0"),
    )

    recovery_rate = successful_recovery_count / attempted_count if attempted_count > 0 else 0.0

    return RecoveryMetrics(
        attempted_count=attempted_count,
        successful_recovery_count=successful_recovery_count,
        failed_recovery_count=failed_recovery_count,
        recovered_revenue_inr=recovered_revenue_inr,
        recovery_rate=recovery_rate,
    )
