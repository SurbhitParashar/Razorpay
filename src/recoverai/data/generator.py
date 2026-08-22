from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class GenerationConfig:
    seed: int = 42
    n_events: int = 50_000
    n_merchants: int = 250
    n_customers: int = 10_000
    start_date: datetime = datetime(2026, 1, 1, tzinfo=UTC)
    end_date: datetime = datetime(2026, 12, 31, tzinfo=UTC)


PAYMENT_METHODS = np.array(
    ["card", "upi", "netbanking", "wallet"],
    dtype=object,
)

FAILURE_PROFILES = {
    "TIMEOUT": {
        "reason": "Payment timed out",
        "category": "transient",
        "base_probability": 0.82,
    },
    "BANK_UNAVAILABLE": {
        "reason": "Bank service temporarily unavailable",
        "category": "transient",
        "base_probability": 0.78,
    },
    "INSUFFICIENT_FUNDS": {
        "reason": "Insufficient funds",
        "category": "customer_action_required",
        "base_probability": 0.28,
    },
    "AUTHENTICATION_FAILED": {
        "reason": "Payment authentication failed",
        "category": "payment_method",
        "base_probability": 0.38,
    },
    "RISK_REVIEW": {
        "reason": "Payment requires additional risk review",
        "category": "risk_review",
        "base_probability": 0.12,
    },
}


def _sigmoid(value: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-value))


def generate_dataset(config: GenerationConfig) -> pd.DataFrame:
    rng = np.random.default_rng(config.seed)

    merchant_ids = np.array(
        [f"merchant_{index:04d}" for index in range(config.n_merchants)],
        dtype=object,
    )

    customer_ids = np.array(
        [f"customer_{index:05d}" for index in range(config.n_customers)],
        dtype=object,
    )

    merchant_baseline_failure = rng.beta(2.0, 35.0, config.n_merchants)

    customer_tenure = rng.integers(30, 1_500, config.n_customers)
    customer_success_rate = rng.beta(9.0, 1.5, config.n_customers)
    customer_avg_amount = rng.lognormal(
        mean=np.log(1_500),
        sigma=0.7,
        size=config.n_customers,
    )

    merchant_index = rng.integers(0, config.n_merchants, config.n_events)
    customer_index = rng.integers(0, config.n_customers, config.n_events)

    start_timestamp = int(config.start_date.timestamp())
    end_timestamp = int(config.end_date.timestamp())

    timestamps = pd.to_datetime(
        rng.integers(
            start_timestamp,
            end_timestamp,
            config.n_events,
        ),
        unit="s",
        utc=True,
    )

    amount = np.round(
        rng.lognormal(mean=np.log(1_800), sigma=0.9, size=config.n_events),
        2,
    )

    payment_method = rng.choice(
        PAYMENT_METHODS,
        size=config.n_events,
        p=[0.28, 0.52, 0.14, 0.06],
    )

    attempt_number = rng.choice(
        [1, 2, 3],
        size=config.n_events,
        p=[0.76, 0.19, 0.05],
    )

    failure_codes = rng.choice(
        list(FAILURE_PROFILES),
        size=config.n_events,
        p=[0.34, 0.22, 0.22, 0.16, 0.06],
    )

    failure_reason = np.array(
        [FAILURE_PROFILES[code]["reason"] for code in failure_codes],
        dtype=object,
    )

    failure_category = np.array(
        [FAILURE_PROFILES[code]["category"] for code in failure_codes],
        dtype=object,
    )

    merchant_failure_rate_24h = np.clip(
        merchant_baseline_failure[merchant_index] + rng.normal(0.0, 0.025, config.n_events),
        0.001,
        0.35,
    )

    customer_success = customer_success_rate[customer_index]

    customer_avg = customer_avg_amount[customer_index]

    previous_failures = rng.poisson(
        lam=np.clip((1.0 - customer_success) * 4.0, 0.1, 4.0),
        size=config.n_events,
    )

    days_since_last_success = rng.integers(
        0,
        45,
        size=config.n_events,
    )

    amount_vs_customer_avg = amount / customer_avg

    hour_of_day = timestamps.hour.to_numpy()
    day_of_week = timestamps.dayofweek.to_numpy()

    base_recovery_probability = np.array(
        [FAILURE_PROFILES[code]["base_probability"] for code in failure_codes]
    )

    logit = (
        np.log(base_recovery_probability / (1.0 - base_recovery_probability))
        + 1.5 * (customer_success - 0.75)
        - 0.55 * (attempt_number - 1)
        - 0.10 * previous_failures
        - 0.45 * (amount_vs_customer_avg - 1.0)
        + 1.10 * (merchant_failure_rate_24h > 0.10)
        + 0.25 * (payment_method == "upi")
        - 0.30 * ((hour_of_day < 7) | (hour_of_day > 22))
    )

    recovery_probability = np.clip(
        _sigmoid(logit),
        0.01,
        0.99,
    )

    recovered = rng.random(config.n_events) < recovery_probability

    recovered_amount = np.where(
        recovered,
        amount,
        0.0,
    )

    time_to_recovery = np.where(
        recovered,
        rng.integers(5, 1_440, size=config.n_events),
        np.nan,
    )

    return pd.DataFrame(
        {
            "payment_id": [f"pay_{index:07d}" for index in range(config.n_events)],
            "merchant_id": merchant_ids[merchant_index],
            "customer_id": customer_ids[customer_index],
            "order_id": [f"order_{index:07d}" for index in range(config.n_events)],
            "amount_inr": amount,
            "attempt_number": attempt_number,
            "payment_method": payment_method,
            "failure_code": failure_codes,
            "failure_reason": failure_reason,
            "failure_category": failure_category,
            "customer_tenure_days": customer_tenure[customer_index],
            "customer_success_rate": np.round(customer_success, 4),
            "customer_avg_amount_inr": np.round(customer_avg, 2),
            "days_since_last_success": days_since_last_success,
            "previous_failures_30d": previous_failures,
            "hour_of_day": hour_of_day,
            "day_of_week": day_of_week,
            "merchant_failure_rate_24h": np.round(
                merchant_failure_rate_24h,
                4,
            ),
            "amount_vs_customer_avg": np.round(
                amount_vs_customer_avg,
                4,
            ),
            "occurred_at": timestamps,
            "recovered": recovered,
            "recovered_amount_inr": np.round(
                recovered_amount,
                2,
            ),
            "time_to_recovery_minutes": time_to_recovery,
        }
    )


def save_dataset(
    dataframe: pd.DataFrame,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)
