from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_predictions(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    threshold: float = 0.5,
) -> dict[str, float]:
    predictions = probabilities >= threshold

    return {
        "precision": float(
            precision_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "pr_auc": float(
            average_precision_score(
                y_true,
                probabilities,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                y_true,
                probabilities,
            )
        ),
        "brier_score": float(
            brier_score_loss(
                y_true,
                probabilities,
            )
        ),
    }


def evaluate_business_impact(
    dataframe: Any,
    probabilities: np.ndarray,
    threshold: float,
) -> dict[str, float]:
    intervention = probabilities >= threshold

    selected = dataframe.loc[intervention].copy()

    recovered_revenue = float(selected["recovered_amount_inr"].sum())

    attempted_revenue = float(selected["amount_inr"].sum())

    actual_recoveries = float(selected["recovered"].sum())

    false_positives = float((~selected["recovered"].astype(bool)).sum())

    return {
        "intervention_rate": float(intervention.mean()),
        "intervention_count": float(intervention.sum()),
        "recovered_revenue_inr": recovered_revenue,
        "attempted_revenue_inr": attempted_revenue,
        "actual_recoveries": actual_recoveries,
        "false_positives": false_positives,
    }
