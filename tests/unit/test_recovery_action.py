from decimal import Decimal

from recoverai.recovery.action import FakePaymentLinkProvider


def test_fake_payment_link_provider_creates_idempotent_link() -> None:
    provider = FakePaymentLinkProvider()

    link = provider.create_payment_link(
        payment_id="pay_action_001",
        amount_inr=Decimal("1500.00"),
        idempotency_key="recoverai:pay_action_001",
    )

    assert link.payment_id == "pay_action_001"
    assert link.amount_inr == Decimal("1500.00")
    assert link.url == "https://example.test/recover/pay_action_001"
    assert link.idempotency_key == "recoverai:pay_action_001"
    assert provider.calls == ["recoverai:pay_action_001"]

    repeated_link = provider.create_payment_link(
        payment_id="pay_action_001",
        amount_inr=Decimal("1500.00"),
        idempotency_key="recoverai:pay_action_001",
    )

    assert repeated_link == link
    assert provider.calls == ["recoverai:pay_action_001"]
