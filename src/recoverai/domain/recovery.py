from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from recoverai.domain.enums import FailureCategory, RecoveryAction


class RecoveryOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: str = Field(min_length=1)

    failure_category: FailureCategory

    recovery_probability: float = Field(ge=0.0, le=1.0)

    recommended_action: RecoveryAction

    action_executed: bool

    recovered: bool

    recovered_amount_inr: Decimal = Field(ge=0, decimal_places=2)

    time_to_recovery_minutes: int | None = Field(default=None, ge=0)

    occurred_at: datetime
