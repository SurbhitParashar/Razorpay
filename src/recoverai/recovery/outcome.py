from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class RecoveryOutcomeStatus(StrEnum):
    PAID = "paid"
    UNPAID = "unpaid"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass(frozen=True, slots=True)
class RecoveryOutcome:
    payment_id: str
    status: RecoveryOutcomeStatus
    recovered_amount_inr: Decimal
    reason: str
