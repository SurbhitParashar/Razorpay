from __future__ import annotations

from decimal import Decimal

import razorpay

from recoverai.recovery.action import PaymentLink


class RazorpayPaymentLinkProvider:
    def __init__(
        self,
        key_id: str,
        key_secret: str,
    ) -> None:
        self.client = razorpay.Client(
            auth=(key_id, key_secret),
        )

    def create_payment_link(
        self,
        payment_id: str,
        amount_inr: Decimal,
        idempotency_key: str,
    ) -> PaymentLink:
        response = self.client.payment_link.create(
            {
                "amount": int(amount_inr * 100),
                "currency": "INR",
                "reference_id": payment_id,
                "description": f"RecoverAI recovery for {payment_id}",
                "reminder_enable": True,
            }
        )

        return PaymentLink(
            payment_id=payment_id,
            amount_inr=amount_inr,
            url=response["short_url"],
            idempotency_key=idempotency_key,
        )
