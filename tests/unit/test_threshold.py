from decimal import Decimal

import numpy as np

from recoverai.ml.threshold import evaluate_threshold, select_threshold


def test_threshold_calculates_recovery_economics() -> None:
    probabilities = np.array([0.9, 0.8, 0.4, 0.2])
    actual = np.array([1, 1, 0, 1])
    amounts = np.array([1000.0, 2000.0, 3000.0, 4000.0])

    result = evaluate_threshold(
        probabilities=probabilities,
        actual_recovery=actual,
        payment_amounts=amounts,
        threshold=0.5,
        intervention_cost_inr=Decimal("5"),
    )

    assert result.intervention_count == 2
    assert result.actual_recoveries == 2
    assert result.false_positives == 0
    assert result.recovered_revenue_inr == Decimal("3000.0")
    assert result.intervention_cost_inr == Decimal("10")
    assert result.net_recovered_revenue_inr == Decimal("2990.0")


def test_threshold_selection_uses_validation_economics() -> None:
    probabilities = np.array([0.95, 0.8, 0.6, 0.3])
    actual = np.array([1, 1, 0, 0])
    amounts = np.array([1000.0, 2000.0, 5000.0, 10000.0])
    thresholds = np.array([0.5, 0.7, 0.9])

    result = select_threshold(
        probabilities=probabilities,
        actual_recovery=actual,
        payment_amounts=amounts,
        thresholds=thresholds,
        intervention_cost_inr=Decimal("5"),
    )

    assert result.threshold == 0.7
