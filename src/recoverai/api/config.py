from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal


def _decimal_env(name: str, default: str) -> Decimal:
    value = os.getenv(name, default)
    return Decimal(value)


def _int_env(name: str, default: str) -> int:
    return int(os.getenv(name, default))


def _bool_env(name: str, default: str) -> bool:
    value = os.getenv(name, default).strip().lower()
    if value not in {"true", "false"}:
        raise ValueError(f"{name} must be true or false.")
    return value == "true"


@dataclass(frozen=True, slots=True)
class RecoverySettings:
    threshold: float = 0.5
    intervention_cost_inr: Decimal = Decimal("5.00")
    max_retries: int = 3
    max_recovery_amount_inr: Decimal = Decimal("100000.00")
    dry_run: bool = False
    state_database_path: str = "data/recoverai.db"
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""

    @classmethod
    def from_environment(cls) -> RecoverySettings:
        return cls(
            threshold=float(os.getenv("RECOVERAI_THRESHOLD", "0.5")),
            intervention_cost_inr=_decimal_env(
                "RECOVERAI_INTERVENTION_COST_INR",
                "5.00",
            ),
            max_retries=_int_env("RECOVERAI_MAX_RETRIES", "3"),
            max_recovery_amount_inr=_decimal_env(
                "RECOVERAI_MAX_RECOVERY_AMOUNT_INR",
                "100000.00",
            ),
            dry_run=_bool_env("RECOVERAI_DRY_RUN", "false"),
            state_database_path=os.getenv(
                "RECOVERAI_STATE_DATABASE_PATH",
                "data/recoverai.db",
            ),
            razorpay_key_id=os.getenv("RAZORPAY_KEY_ID", ""),
            razorpay_key_secret=os.getenv("RAZORPAY_KEY_SECRET", ""),
        )
