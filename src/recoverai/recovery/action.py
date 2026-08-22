from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True, slots=True)
class PaymentLink:
    payment_id: str
    amount_inr: Decimal
    url: str
    idempotency_key: str


class PaymentLinkProvider(Protocol):
    def create_payment_link(
        self,
        payment_id: str,
        amount_inr: Decimal,
        idempotency_key: str,
    ) -> PaymentLink: ...


class FakePaymentLinkProvider:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self._links: dict[str, PaymentLink] = {}

    def create_payment_link(
        self,
        payment_id: str,
        amount_inr: Decimal,
        idempotency_key: str,
    ) -> PaymentLink:
        if idempotency_key in self._links:
            return self._links[idempotency_key]

        self.calls.append(idempotency_key)

        link = PaymentLink(
            payment_id=payment_id,
            amount_inr=amount_inr,
            url=f"https://example.test/recover/{payment_id}",
            idempotency_key=idempotency_key,
        )

        self._links[idempotency_key] = link
        return link
