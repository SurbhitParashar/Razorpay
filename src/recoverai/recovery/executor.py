from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from recoverai.recovery.action import PaymentLinkProvider
from recoverai.recovery.audit import RecoveryAuditEvent
from recoverai.recovery.gateway import RecoveryGateway
from recoverai.recovery.models import (
    RecoveryAction,
    RecoveryRequest,
    RecoveryResult,
    RecoveryStatus,
)
from recoverai.recovery.outcome import (
    RecoveryOutcome,
    RecoveryOutcomeStatus,
)
from recoverai.state.store import (
    RecoveryStateStore,
    StoredPaymentLink,
    StoredRecovery,
    StoredRecoveryOutcome,
)


@dataclass(frozen=True, slots=True)
class ExecutionConfig:
    max_retries: int
    max_recovery_amount_inr: Decimal
    dry_run: bool


class RecoveryExecutor:
    def __init__(
        self,
        gateway: RecoveryGateway,
        config: ExecutionConfig,
        state_store: RecoveryStateStore | None = None,
        payment_link_provider: PaymentLinkProvider | None = None,
    ) -> None:
        self.gateway = gateway
        self.config = config
        self.state_store = state_store
        self.payment_link_provider = payment_link_provider
        self._completed: set[str] = set()
        self._created_payment_links: dict[str, str] = {}
        self.audit_events: list[RecoveryAuditEvent] = []

    def execute(self, request: RecoveryRequest) -> RecoveryResult:
        idempotency_key = f"recoverai:{request.payment_id}"

        if request.payment_id in self._completed:
            return self._record(
                request,
                RecoveryAction.IDEMPOTENT_NOOP,
                RecoveryStatus.SKIPPED,
                Decimal("0"),
                "Payment already recovered.",
            )

        if request.payment_id in self._created_payment_links:
            return self._record(
                request,
                RecoveryAction.IDEMPOTENT_NOOP,
                RecoveryStatus.SKIPPED,
                Decimal("0"),
                "Payment link already created.",
                payment_link=self._created_payment_links[request.payment_id],
            )

        if self.state_store is not None:
            stored = self.state_store.get_recovery(idempotency_key)

            if stored is not None:
                self._completed.add(request.payment_id)

                return self._record(
                    request,
                    RecoveryAction.IDEMPOTENT_NOOP,
                    RecoveryStatus.SKIPPED,
                    Decimal("0"),
                    "Payment already recovered.",
                )

            stored_payment_link = self.state_store.get_payment_link(idempotency_key)

            if stored_payment_link is not None:
                self._created_payment_links[request.payment_id] = stored_payment_link.url

                return self._record(
                    request,
                    RecoveryAction.IDEMPOTENT_NOOP,
                    RecoveryStatus.SKIPPED,
                    Decimal("0"),
                    "Payment link already created.",
                    payment_link=stored_payment_link.url,
                )

        if request.recovery_probability < request.threshold:
            return self._record(
                request,
                RecoveryAction.NO_ACTION,
                RecoveryStatus.SKIPPED,
                Decimal("0"),
                "Recovery probability below threshold.",
            )

        if request.amount_inr > self.config.max_recovery_amount_inr:
            return self._record(
                request,
                RecoveryAction.STOPPED,
                RecoveryStatus.SKIPPED,
                Decimal("0"),
                "Recovery amount exceeds configured safety limit.",
            )

        if request.attempt_number > self.config.max_retries:
            return self._record(
                request,
                RecoveryAction.STOPPED,
                RecoveryStatus.SKIPPED,
                Decimal("0"),
                "Maximum recovery attempts exceeded.",
            )

        if self.payment_link_provider is None:
            return self._execute_gateway_recovery(request, idempotency_key)

        return self._execute_payment_link(
            request,
            idempotency_key,
        )

    def record_recovery_outcome(
        self,
        payment_id: str,
        status: RecoveryOutcomeStatus,
        recovered_amount_inr: Decimal,
        reason: str,
    ) -> RecoveryOutcome:
        if recovered_amount_inr < Decimal("0"):
            raise ValueError("Recovered amount cannot be negative.")

        idempotency_key = f"recoverai:{payment_id}:outcome"

        if self.state_store is not None:
            stored = self.state_store.get_recovery_outcome(idempotency_key)

            if stored is not None:
                return RecoveryOutcome(
                    payment_id=stored.payment_id,
                    status=RecoveryOutcomeStatus(stored.status),
                    recovered_amount_inr=stored.recovered_amount_inr,
                    reason=stored.reason,
                )

        if status is not RecoveryOutcomeStatus.PAID:
            recovered_amount_inr = Decimal("0")

        outcome = RecoveryOutcome(
            payment_id=payment_id,
            status=status,
            recovered_amount_inr=recovered_amount_inr,
            reason=reason,
        )

        if self.state_store is not None:
            self.state_store.save_recovery_outcome(
                StoredRecoveryOutcome(
                    payment_id=payment_id,
                    idempotency_key=idempotency_key,
                    status=status.value,
                    recovered_amount_inr=recovered_amount_inr,
                    reason=reason,
                )
            )

        return outcome

    def _execute_payment_link(
        self,
        request: RecoveryRequest,
        idempotency_key: str,
    ) -> RecoveryResult:
        if self.config.dry_run:
            dry_run_link = f"https://example.test/recover/{request.payment_id}"
            self._created_payment_links[request.payment_id] = dry_run_link

            if self.state_store is not None:
                self.state_store.save_payment_link(
                    StoredPaymentLink(
                        payment_id=request.payment_id,
                        idempotency_key=idempotency_key,
                        status=RecoveryStatus.SUCCESS.value,
                        amount_inr=request.amount_inr,
                        url=dry_run_link,
                        reason="Dry-run payment-link recovery approved.",
                    )
                )

            return self._record(
                request,
                RecoveryAction.CREATE_PAYMENT_LINK,
                RecoveryStatus.SUCCESS,
                Decimal("0"),
                "Dry-run payment-link recovery approved.",
                payment_link=dry_run_link,
            )

        if self.payment_link_provider is None:
            raise RuntimeError("Payment-link provider is not configured.")

        try:
            link = self.payment_link_provider.create_payment_link(
                payment_id=request.payment_id,
                amount_inr=request.amount_inr,
                idempotency_key=idempotency_key,
            )
        except Exception as exc:
            return self._record(
                request,
                RecoveryAction.CREATE_PAYMENT_LINK,
                RecoveryStatus.FAILED,
                Decimal("0"),
                f"Payment-link creation failed: {exc}",
            )

        self._created_payment_links[request.payment_id] = link.url

        if self.state_store is not None:
            self.state_store.save_payment_link(
                StoredPaymentLink(
                    payment_id=request.payment_id,
                    idempotency_key=idempotency_key,
                    status=RecoveryStatus.SUCCESS.value,
                    amount_inr=request.amount_inr,
                    url=link.url,
                    reason="Recovery payment link created.",
                )
            )

        return self._record(
            request,
            RecoveryAction.CREATE_PAYMENT_LINK,
            RecoveryStatus.SUCCESS,
            Decimal("0"),
            "Recovery payment link created.",
            payment_link=link.url,
        )

    def _execute_gateway_recovery(
        self,
        request: RecoveryRequest,
        idempotency_key: str,
    ) -> RecoveryResult:
        if self.config.dry_run:
            self._completed.add(request.payment_id)

            return self._record(
                request,
                RecoveryAction.RECOVER,
                RecoveryStatus.SUCCESS,
                request.amount_inr,
                "Dry-run recovery approved.",
            )

        status = self.gateway.recover(
            payment_id=request.payment_id,
            amount_inr=request.amount_inr,
            idempotency_key=idempotency_key,
        )

        if status is RecoveryStatus.SUCCESS:
            self._completed.add(request.payment_id)

            if self.state_store is not None:
                self.state_store.save_recovery(
                    StoredRecovery(
                        payment_id=request.payment_id,
                        idempotency_key=idempotency_key,
                        status=status.value,
                        recovered_amount_inr=request.amount_inr,
                        reason="Gateway execution completed.",
                    )
                )

        return self._record(
            request,
            RecoveryAction.RECOVER,
            status,
            request.amount_inr if status is RecoveryStatus.SUCCESS else Decimal("0"),
            "Gateway execution completed.",
        )

    def _record(
        self,
        request: RecoveryRequest,
        action: RecoveryAction,
        status: RecoveryStatus,
        recovered_amount: Decimal,
        reason: str,
        payment_link: str | None = None,
    ) -> RecoveryResult:
        self.audit_events.append(
            RecoveryAuditEvent.create(
                payment_id=request.payment_id,
                action=action,
                status=status,
                amount_inr=recovered_amount,
                attempt_number=request.attempt_number,
                reason=reason,
            )
        )

        return RecoveryResult(
            payment_id=request.payment_id,
            action=action,
            status=status,
            recovered_amount_inr=recovered_amount,
            attempt_number=request.attempt_number,
            reason=reason,
            payment_link=payment_link,
        )
