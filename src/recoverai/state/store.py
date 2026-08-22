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


class RecoveryStateStore(Protocol):
    def get_recovery(
        self,
        idempotency_key: str,
    ) -> StoredRecovery | None: ...

    def save_recovery(
        self,
        recovery: StoredRecovery,
    ) -> None: ...
