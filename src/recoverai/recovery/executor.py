from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from recoverai.recovery.audit import RecoveryAuditEvent
from recoverai.recovery.gateway import RecoveryGateway
from recoverai.recovery.models import (
    RecoveryAction,
    RecoveryRequest,
    RecoveryResult,
    RecoveryStatus,
)
from recoverai.state.store import RecoveryStateStore, StoredRecovery


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
    ) -> None:
        self.gateway = gateway
        self.config = config
        self.state_store = state_store
        self._completed: set[str] = set()
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
        )
