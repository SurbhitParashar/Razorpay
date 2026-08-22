from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from recoverai.recovery.models import RecoveryAction, RecoveryStatus
from recoverai.recovery.outcome import RecoveryOutcomeStatus


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
    payment_link: str | None = None


class RecoveryOutcomeRequestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: str = Field(min_length=1)
    status: RecoveryOutcomeStatus
    recovered_amount_inr: Decimal = Field(ge=0, decimal_places=2)
    reason: str = Field(min_length=1)


class RecoveryOutcomeResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: str
    status: RecoveryOutcomeStatus
    recovered_amount_inr: Decimal = Field(ge=0)
    reason: str


class RecoveryMetricsResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attempted_count: int
    successful_recovery_count: int
    failed_recovery_count: int
    recovered_revenue_inr: Decimal
    recovery_rate: float
