from decimal import Decimal

import pytest

from recoverai.recovery.outcome import (
    RecoveryOutcome,
    RecoveryOutcomeStatus,
)


def test_paid_outcome_records_recovered_revenue() -> None:
    outcome = RecoveryOutcome(
        payment_id="pay_outcome_001",
        status=RecoveryOutcomeStatus.PAID,
        recovered_amount_inr=Decimal("1500.00"),
        reason="Customer completed recovery payment.",
    )

    assert outcome.status is RecoveryOutcomeStatus.PAID
    assert outcome.recovered_amount_inr == Decimal("1500.00")


def test_unpaid_outcome_has_zero_recovered_revenue() -> None:
    outcome = RecoveryOutcome(
        payment_id="pay_outcome_002",
        status=RecoveryOutcomeStatus.UNPAID,
        recovered_amount_inr=Decimal("0"),
        reason="Customer did not complete payment.",
    )

    assert outcome.status is RecoveryOutcomeStatus.UNPAID
    assert outcome.recovered_amount_inr == Decimal("0")


def test_recovery_outcome_is_immutable() -> None:
    outcome = RecoveryOutcome(
        payment_id="pay_outcome_003",
        status=RecoveryOutcomeStatus.PAID,
        recovered_amount_inr=Decimal("100"),
        reason="Paid.",
    )

    with pytest.raises(AttributeError):
        outcome.recovered_amount_inr = Decimal("200")  # type: ignore[misc]
