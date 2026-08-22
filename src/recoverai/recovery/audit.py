from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from recoverai.recovery.models import RecoveryAction, RecoveryStatus


@dataclass(frozen=True, slots=True)
class RecoveryAuditEvent:
    payment_id: str
    action: RecoveryAction
    status: RecoveryStatus
    amount_inr: Decimal
    attempt_number: int
    reason: str
    occurred_at: datetime

    @classmethod
    def create(
        cls,
        payment_id: str,
        action: RecoveryAction,
        status: RecoveryStatus,
        amount_inr: Decimal,
        attempt_number: int,
        reason: str,
    ) -> RecoveryAuditEvent:
        return cls(
            payment_id=payment_id,
            action=action,
            status=status,
            amount_inr=amount_inr,
            attempt_number=attempt_number,
            reason=reason,
            occurred_at=datetime.now(UTC),
        )
