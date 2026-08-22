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
    ) -> None:
        self.gateway = gateway
        self.config = config
        self._completed: set[str] = set()
        self.audit_events: list[RecoveryAuditEvent] = []

    def execute(self, request: RecoveryRequest) -> RecoveryResult:
        if request.payment_id in self._completed:
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

        idempotency_key = f"recoverai:{request.payment_id}"

        status = self.gateway.recover(
            payment_id=request.payment_id,
            amount_inr=request.amount_inr,
            idempotency_key=idempotency_key,
        )

        if status is RecoveryStatus.SUCCESS:
            self._completed.add(request.payment_id)

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
