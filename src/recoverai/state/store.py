from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True, slots=True)
class StoredRecovery:
    payment_id: str
    idempotency_key: str
    status: str
    recovered_amount_inr: Decimal
    reason: str


@dataclass(frozen=True, slots=True)
class StoredPaymentLink:
    payment_id: str
    idempotency_key: str
    status: str
    amount_inr: Decimal
    url: str
    reason: str


@dataclass(frozen=True, slots=True)
class StoredRecoveryOutcome:
    payment_id: str
    idempotency_key: str
    status: str
    recovered_amount_inr: Decimal
    reason: str


class RecoveryStateStore(Protocol):
    def get_recovery(
        self,
        idempotency_key: str,
    ) -> StoredRecovery | None: ...

    def save_recovery(
        self,
        recovery: StoredRecovery,
    ) -> None: ...

    def get_payment_link(
        self,
        idempotency_key: str,
    ) -> StoredPaymentLink | None: ...

    def save_payment_link(
        self,
        payment_link: StoredPaymentLink,
    ) -> None: ...

    def get_recovery_outcome(
        self,
        idempotency_key: str,
    ) -> StoredRecoveryOutcome | None: ...

    def save_recovery_outcome(
        self,
        outcome: StoredRecoveryOutcome,
    ) -> None: ...
