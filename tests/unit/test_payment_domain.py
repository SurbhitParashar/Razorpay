from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from recoverai.domain import PaymentEvent, PaymentMethod


def test_payment_event_accepts_valid_data() -> None:
    event = PaymentEvent(
        payment_id="pay_001",
        merchant_id="merchant_001",
        customer_id="customer_001",
        order_id="order_001",
        amount_inr=Decimal("1499.00"),
        attempt_number=1,
        payment_method=PaymentMethod.UPI,
        failure_code="TIMEOUT",
        failure_reason="Payment timed out",
        occurred_at=datetime.now(UTC),
    )

    assert event.amount_inr == Decimal("1499.00")
    assert event.payment_method == PaymentMethod.UPI


def test_payment_event_rejects_negative_amount() -> None:
    with pytest.raises(ValidationError):
        PaymentEvent(
            payment_id="pay_001",
            merchant_id="merchant_001",
            customer_id="customer_001",
            order_id="order_001",
            amount_inr=Decimal("-1.00"),
            attempt_number=1,
            payment_method=PaymentMethod.UPI,
            failure_code="TIMEOUT",
            failure_reason="Payment timed out",
            occurred_at=datetime.now(UTC),
        )


def test_payment_event_rejects_unknown_fields() -> None:
    payload = {
        "payment_id": "pay_001",
        "merchant_id": "merchant_001",
        "customer_id": "customer_001",
        "order_id": "order_001",
        "amount_inr": Decimal("1499.00"),
        "attempt_number": 1,
        "payment_method": PaymentMethod.UPI,
        "failure_code": "TIMEOUT",
        "failure_reason": "Payment timed out",
        "occurred_at": datetime.now(UTC),
        "unexpected_field": "should_fail",
    }

    with pytest.raises(ValidationError):
        PaymentEvent.model_validate(payload)
