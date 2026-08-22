from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from recoverai.recovery.models import RecoveryAction


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    payment_id: str
    probability: float
    threshold: float
    action: RecoveryAction
    expected_net_value_inr: Decimal
    reason: str
