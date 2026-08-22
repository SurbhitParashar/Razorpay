import numpy as np
import pandas as pd

from recoverai.ml.evaluate import evaluate_predictions
from recoverai.ml.features import build_features
from recoverai.ml.train import build_pipeline


def test_feature_contract_excludes_future_outcomes() -> None:
    dataframe = pd.DataFrame(
        {
            "amount_inr": [100.0, 200.0],
            "attempt_number": [1, 2],
            "customer_tenure_days": [100, 200],
            "customer_success_rate": [0.9, 0.8],
            "customer_avg_amount_inr": [100.0, 200.0],
            "days_since_last_success": [1, 3],
            "previous_failures_30d": [0, 2],
            "hour_of_day": [10, 20],
            "day_of_week": [1, 4],
            "merchant_failure_rate_24h": [0.05, 0.12],
            "amount_vs_customer_avg": [1.0, 1.0],
            "payment_method": ["upi", "card"],
            "failure_code": ["TIMEOUT", "BANK_UNAVAILABLE"],
            "failure_category": ["transient", "transient"],
            "recovered": [1, 0],
            "recovered_amount_inr": [100.0, 0.0],
            "time_to_recovery_minutes": [10, np.nan],
        }
    )

    features = build_features(dataframe)

    assert "recovered_amount_inr" not in features.X.columns
    assert "time_to_recovery_minutes" not in features.X.columns


def test_model_pipeline_can_train() -> None:
    dataframe = pd.DataFrame(
        {
            "amount_inr": [100.0, 200.0, 300.0, 400.0],
            "attempt_number": [1, 1, 2, 3],
            "customer_tenure_days": [100, 200, 300, 400],
            "customer_success_rate": [0.9, 0.8, 0.7, 0.6],
            "customer_avg_amount_inr": [100.0, 200.0, 300.0, 400.0],
            "days_since_last_success": [1, 2, 3, 4],
            "previous_failures_30d": [0, 1, 2, 3],
            "hour_of_day": [10, 11, 12, 13],
            "day_of_week": [1, 2, 3, 4],
            "merchant_failure_rate_24h": [0.05, 0.06, 0.07, 0.08],
            "amount_vs_customer_avg": [1.0, 1.0, 1.0, 1.0],
            "payment_method": ["upi", "card", "upi", "card"],
            "failure_code": [
                "TIMEOUT",
                "BANK_UNAVAILABLE",
                "TIMEOUT",
                "BANK_UNAVAILABLE",
            ],
            "failure_category": [
                "transient",
                "transient",
                "transient",
                "transient",
            ],
            "recovered": [1, 1, 0, 0],
        }
    )

    features = build_features(dataframe)

    model = build_pipeline()
    model.fit(features.X, features.y)

    probabilities = model.predict_proba(features.X)[:, 1]

    assert len(probabilities) == len(dataframe)
    assert np.all((probabilities >= 0) & (probabilities <= 1))


def test_evaluation_returns_required_metrics() -> None:
    y_true = np.array([0, 1, 1, 0])
    probabilities = np.array([0.1, 0.8, 0.7, 0.2])

    metrics = evaluate_predictions(
        y_true,
        probabilities,
    )

    assert set(metrics) == {
        "precision",
        "recall",
        "pr_auc",
        "roc_auc",
        "brier_score",
    }
