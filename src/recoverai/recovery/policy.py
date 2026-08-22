from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class RecoveryPolicy:
    threshold: float
    intervention_cost_inr: Decimal

    def should_intervene(self, recovery_probability: float) -> bool:
        return recovery_probability >= self.threshold

    def expected_net_value(
        self,
        recovery_probability: float,
        payment_amount_inr: Decimal,
    ) -> Decimal:
        expected_recovery = Decimal(str(recovery_probability)) * payment_amount_inr
        return expected_recovery - self.intervention_cost_inr
