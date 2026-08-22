from decimal import Decimal

from recoverai.metrics.recovery import calculate_recovery_metrics
from recoverai.recovery.outcome import (
    RecoveryOutcome,
    RecoveryOutcomeStatus,
)


def test_recovery_metrics_for_empty_outcomes() -> None:
    metrics = calculate_recovery_metrics([])

    assert metrics.attempted_count == 0
    assert metrics.successful_recovery_count == 0
    assert metrics.failed_recovery_count == 0
    assert metrics.recovered_revenue_inr == Decimal("0")
    assert metrics.recovery_rate == 0.0


def test_recovery_metrics_for_all_successful_outcomes() -> None:
    outcomes = [
        RecoveryOutcome(
            payment_id="pay_001",
            status=RecoveryOutcomeStatus.PAID,
            recovered_amount_inr=Decimal("1000"),
            reason="Paid.",
        ),
        RecoveryOutcome(
            payment_id="pay_002",
            status=RecoveryOutcomeStatus.PAID,
            recovered_amount_inr=Decimal("1500"),
            reason="Paid.",
        ),
    ]

    metrics = calculate_recovery_metrics(outcomes)

    assert metrics.attempted_count == 2
    assert metrics.successful_recovery_count == 2
    assert metrics.failed_recovery_count == 0
    assert metrics.recovered_revenue_inr == Decimal("2500")
    assert metrics.recovery_rate == 1.0


def test_recovery_metrics_for_mixed_outcomes() -> None:
    outcomes = [
        RecoveryOutcome(
            payment_id="pay_001",
            status=RecoveryOutcomeStatus.PAID,
            recovered_amount_inr=Decimal("1000"),
            reason="Paid.",
        ),
        RecoveryOutcome(
            payment_id="pay_002",
            status=RecoveryOutcomeStatus.UNPAID,
            recovered_amount_inr=Decimal("0"),
            reason="Not paid.",
        ),
        RecoveryOutcome(
            payment_id="pay_003",
            status=RecoveryOutcomeStatus.FAILED,
            recovered_amount_inr=Decimal("0"),
            reason="Failed.",
        ),
        RecoveryOutcome(
            payment_id="pay_004",
            status=RecoveryOutcomeStatus.EXPIRED,
            recovered_amount_inr=Decimal("0"),
            reason="Expired.",
        ),
    ]

    metrics = calculate_recovery_metrics(outcomes)

    assert metrics.attempted_count == 4
    assert metrics.successful_recovery_count == 1
    assert metrics.failed_recovery_count == 3
    assert metrics.recovered_revenue_inr == Decimal("1000")
    assert metrics.recovery_rate == 0.25


def test_recovery_metrics_sums_actual_recovered_revenue() -> None:
    outcomes = [
        RecoveryOutcome(
            payment_id="pay_005",
            status=RecoveryOutcomeStatus.PAID,
            recovered_amount_inr=Decimal("1250.50"),
            reason="Partial recovery.",
        ),
        RecoveryOutcome(
            payment_id="pay_006",
            status=RecoveryOutcomeStatus.PAID,
            recovered_amount_inr=Decimal("749.50"),
            reason="Paid.",
        ),
    ]

    metrics = calculate_recovery_metrics(outcomes)

    assert metrics.recovered_revenue_inr == Decimal("2000.00")
