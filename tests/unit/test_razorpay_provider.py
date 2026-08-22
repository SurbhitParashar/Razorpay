from decimal import Decimal
from unittest.mock import Mock

from recoverai.recovery.razorpay import RazorpayPaymentLinkProvider


def test_razorpay_payment_link_provider_creates_link() -> None:
    provider = RazorpayPaymentLinkProvider(
        key_id="rzp_test_key",
        key_secret="test_secret",
    )

    provider.client.payment_link.create = Mock(
        return_value={
            "short_url": "https://rzp.io/i/test123",
        }
    )

    result = provider.create_payment_link(
        payment_id="pay_001",
        amount_inr=Decimal("1500.00"),
        idempotency_key="recoverai:pay_001",
    )

    provider.client.payment_link.create.assert_called_once_with(
        {
            "amount": 150000,
            "currency": "INR",
            "reference_id": "pay_001",
            "description": "RecoverAI recovery for pay_001",
            "reminder_enable": True,
        }
    )

    assert result.payment_id == "pay_001"
    assert result.amount_inr == Decimal("1500.00")
    assert result.url == "https://rzp.io/i/test123"
    assert result.idempotency_key == "recoverai:pay_001"
