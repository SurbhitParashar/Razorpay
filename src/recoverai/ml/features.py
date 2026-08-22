from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

FEATURE_COLUMNS = [
    "amount_inr",
    "attempt_number",
    "customer_tenure_days",
    "customer_success_rate",
    "customer_avg_amount_inr",
    "days_since_last_success",
    "previous_failures_30d",
    "hour_of_day",
    "day_of_week",
    "merchant_failure_rate_24h",
    "amount_vs_customer_avg",
    "payment_method",
    "failure_code",
    "failure_category",
]


TARGET_COLUMN = "recovered"


@dataclass(frozen=True)
class FeatureSet:
    X: pd.DataFrame
    y: pd.Series


def build_features(dataframe: pd.DataFrame) -> FeatureSet:
    missing = set(FEATURE_COLUMNS + [TARGET_COLUMN]) - set(dataframe.columns)

    if missing:
        raise ValueError(f"Missing feature columns: {sorted(missing)}")

    X = dataframe[FEATURE_COLUMNS].copy()

    y = dataframe[TARGET_COLUMN].astype(int)

    return FeatureSet(X=X, y=y)
