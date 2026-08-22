from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, slots=True)
class ThresholdMetrics:
    threshold: float
    intervention_rate: float
    intervention_count: int
    precision: float
    recall: float
    recovered_revenue_inr: Decimal
    attempted_revenue_inr: Decimal
    actual_recoveries: int
    false_positives: int
    intervention_cost_inr: Decimal
    net_recovered_revenue_inr: Decimal


@dataclass(frozen=True, slots=True)
class ThresholdSelection:
    threshold: float
    metrics: ThresholdMetrics


def evaluate_threshold(
    probabilities: NDArray[np.float64],
    actual_recovery: NDArray[np.int_],
    payment_amounts: NDArray[np.float64],
    threshold: float,
    intervention_cost_inr: Decimal,
) -> ThresholdMetrics:
    interventions = probabilities >= threshold

    intervention_count = int(interventions.sum())

    if intervention_count == 0:
        return ThresholdMetrics(
            threshold=threshold,
            intervention_rate=0.0,
            intervention_count=0,
            precision=0.0,
            recall=0.0,
            recovered_revenue_inr=Decimal("0"),
            attempted_revenue_inr=Decimal("0"),
            actual_recoveries=0,
            false_positives=0,
            intervention_cost_inr=Decimal("0"),
            net_recovered_revenue_inr=Decimal("0"),
        )

    selected_actual = actual_recovery[interventions]
    selected_amounts = payment_amounts[interventions]

    actual_recoveries = int(selected_actual.sum())
    false_positives = intervention_count - actual_recoveries

    total_actual_recoveries = int(actual_recovery.sum())

    precision = actual_recoveries / intervention_count
    recall = actual_recoveries / total_actual_recoveries if total_actual_recoveries else 0.0

    attempted_revenue = Decimal(str(selected_amounts.sum()))

    recovered_mask = selected_actual == 1
    recovered_revenue = Decimal(str(selected_amounts[recovered_mask].sum()))

    intervention_cost = intervention_cost_inr * intervention_count

    net_recovered_revenue = recovered_revenue - intervention_cost

    return ThresholdMetrics(
        threshold=threshold,
        intervention_rate=intervention_count / len(probabilities),
        intervention_count=intervention_count,
        precision=precision,
        recall=recall,
        recovered_revenue_inr=recovered_revenue,
        attempted_revenue_inr=attempted_revenue,
        actual_recoveries=actual_recoveries,
        false_positives=false_positives,
        intervention_cost_inr=intervention_cost,
        net_recovered_revenue_inr=net_recovered_revenue,
    )


def select_threshold(
    probabilities: NDArray[np.float64],
    actual_recovery: NDArray[np.int_],
    payment_amounts: NDArray[np.float64],
    thresholds: NDArray[np.float64],
    intervention_cost_inr: Decimal,
) -> ThresholdSelection:
    candidates = [
        evaluate_threshold(
            probabilities=probabilities,
            actual_recovery=actual_recovery,
            payment_amounts=payment_amounts,
            threshold=float(threshold),
            intervention_cost_inr=intervention_cost_inr,
        )
        for threshold in thresholds
    ]

    best = max(
        candidates,
        key=lambda metrics: (
            metrics.net_recovered_revenue_inr,
            metrics.precision,
            -metrics.intervention_count,
        ),
    )

    return ThresholdSelection(
        threshold=best.threshold,
        metrics=best,
    )
