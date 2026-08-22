from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from recoverai.recovery.models import RecoveryAction, RecoveryStatus


class RecoveryRequestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: str = Field(min_length=1)
    amount_inr: Decimal = Field(gt=0, decimal_places=2)
    recovery_probability: float = Field(ge=0.0, le=1.0)
    attempt_number: int = Field(ge=1)


class RecoveryResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: str
    decision: RecoveryAction
    execution_status: RecoveryStatus
    recovered_amount_inr: Decimal = Field(ge=0)
    expected_net_value_inr: Decimal
    reason: str
