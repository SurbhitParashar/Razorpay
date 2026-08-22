from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = [
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
]

CATEGORICAL_FEATURES = [
    "payment_method",
    "failure_code",
    "failure_category",
]


def build_pipeline(
    max_iter: int = 1_000,
    class_weight: str = "balanced",
    random_state: int = 42,
) -> Pipeline:
    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "one_hot",
                OneHotEncoder(
                    handle_unknown="ignore",
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    model = LogisticRegression(
        max_iter=max_iter,
        class_weight=class_weight,
        random_state=random_state,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )
