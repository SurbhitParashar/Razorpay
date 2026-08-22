from datetime import UTC, datetime
from decimal import Decimal

from recoverai.domain import (
    FailureCategory,
    RecoveryAction,
    RecoveryOutcome,
)


def test_recovery_outcome_accepts_valid_probability() -> None:
    outcome = RecoveryOutcome(
        payment_id="pay_001",
        failure_category=FailureCategory.TRANSIENT,
        recovery_probability=0.82,
        recommended_action=RecoveryAction.RETRY_PAYMENT,
        action_executed=True,
        recovered=True,
        recovered_amount_inr=Decimal("1499.00"),
        time_to_recovery_minutes=12,
        occurred_at=datetime.now(UTC),
    )

    assert outcome.recovery_probability == 0.82
    assert outcome.recovered is True
