from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from recoverai.domain.enums import PaymentMethod


class PaymentEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: str = Field(min_length=1)
    merchant_id: str = Field(min_length=1)
    customer_id: str = Field(min_length=1)
    order_id: str = Field(min_length=1)

    amount_inr: Decimal = Field(gt=0, decimal_places=2)

    attempt_number: int = Field(ge=1)

    payment_method: PaymentMethod

    failure_code: str = Field(min_length=1)
    failure_reason: str = Field(min_length=1)

    occurred_at: datetime
