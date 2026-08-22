from __future__ import annotations

from decimal import Decimal
from typing import Protocol

from recoverai.recovery.models import RecoveryStatus


class RecoveryGateway(Protocol):
    def recover(
        self,
        payment_id: str,
        amount_inr: Decimal,
        idempotency_key: str,
    ) -> RecoveryStatus: ...


class FakeRecoveryGateway:
    def __init__(self, should_succeed: bool = True) -> None:
        self.should_succeed = should_succeed
        self.calls: list[str] = []

    def recover(
        self,
        payment_id: str,
        amount_inr: Decimal,
        idempotency_key: str,
    ) -> RecoveryStatus:
        self.calls.append(idempotency_key)

        if self.should_succeed:
            return RecoveryStatus.SUCCESS

        return RecoveryStatus.FAILED
