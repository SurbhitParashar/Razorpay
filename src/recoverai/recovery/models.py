from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class RecoveryAction(StrEnum):
    RECOVER = "recover"
    CREATE_PAYMENT_LINK = "create_payment_link"
    NO_ACTION = "no_action"
    IDEMPOTENT_NOOP = "idempotent_noop"
    STOPPED = "stopped"


class RecoveryStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True, slots=True)
class RecoveryRequest:
    payment_id: str
    amount_inr: Decimal
    recovery_probability: float
    threshold: float
    attempt_number: int


@dataclass(frozen=True, slots=True)
class RecoveryResult:
    payment_id: str
    action: RecoveryAction
    status: RecoveryStatus
    recovered_amount_inr: Decimal
    attempt_number: int
    reason: str
