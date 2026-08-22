from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "payment_id",
    "merchant_id",
    "customer_id",
    "order_id",
    "amount_inr",
    "attempt_number",
    "payment_method",
    "failure_code",
    "failure_reason",
    "failure_category",
    "customer_tenure_days",
    "customer_success_rate",
    "customer_avg_amount_inr",
    "days_since_last_success",
    "previous_failures_30d",
    "hour_of_day",
    "day_of_week",
    "merchant_failure_rate_24h",
    "amount_vs_customer_avg",
    "occurred_at",
    "recovered",
    "recovered_amount_inr",
    "time_to_recovery_minutes",
}


def validate_dataset(path: Path) -> None:
    dataframe = pd.read_csv(path)

    missing = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if dataframe.empty:
        raise ValueError("Dataset must not be empty.")

    if dataframe["payment_id"].duplicated().any():
        raise ValueError("payment_id must be unique.")

    if (dataframe["amount_inr"] <= 0).any():
        raise ValueError("amount_inr must be positive.")

    if not dataframe["attempt_number"].between(1, 3).all():
        raise ValueError("attempt_number must be between 1 and 3.")

    if not dataframe["customer_success_rate"].between(0, 1).all():
        raise ValueError("customer_success_rate must be between 0 and 1.")

    if not dataframe["merchant_failure_rate_24h"].between(0, 1).all():
        raise ValueError("merchant_failure_rate_24h must be between 0 and 1.")

    if not dataframe["recovered_amount_inr"].ge(0).all():
        raise ValueError("recovered_amount_inr must be non-negative.")

    invalid_recovery_amount = dataframe["recovered_amount_inr"] > dataframe["amount_inr"]

    if invalid_recovery_amount.any():
        raise ValueError("recovered_amount_inr cannot exceed amount_inr.")

    inconsistent_recovery = dataframe["recovered"] != dataframe["recovered_amount_inr"].gt(0)

    if inconsistent_recovery.any():
        raise ValueError("recovered and recovered_amount_inr are inconsistent.")
