from decimal import Decimal
from pathlib import Path

import pytest

from recoverai.recovery.action import FakePaymentLinkProvider, PaymentLink
from recoverai.recovery.executor import ExecutionConfig, RecoveryExecutor
from recoverai.recovery.gateway import FakeRecoveryGateway
from recoverai.recovery.models import (
    RecoveryAction,
    RecoveryRequest,
    RecoveryStatus,
)
from recoverai.state.sqlite import SQLiteRecoveryStateStore


class FailingPaymentLinkProvider:
    def create_payment_link(
        self,
        payment_id: str,
        amount_inr: Decimal,
        idempotency_key: str,
    ) -> PaymentLink:
        raise RuntimeError("provider unavailable")


def build_request(payment_id: str = "pay_link_001") -> RecoveryRequest:
    return RecoveryRequest(
        payment_id=payment_id,
        amount_inr=Decimal("1500.00"),
        recovery_probability=0.95,
        threshold=0.5,
        attempt_number=1,
    )


def build_config() -> ExecutionConfig:
    return ExecutionConfig(
        max_retries=3,
        max_recovery_amount_inr=Decimal("10000.00"),
        dry_run=False,
    )


def test_executor_gateway_behavior_remains_unchanged() -> None:
    gateway = FakeRecoveryGateway(should_succeed=True)
    executor = RecoveryExecutor(
        gateway=gateway,
        config=build_config(),
    )

    result = executor.execute(build_request("pay_gateway_001"))

    assert result.action is RecoveryAction.RECOVER
    assert result.status is RecoveryStatus.SUCCESS
    assert result.recovered_amount_inr == Decimal("1500.00")
    assert result.payment_link is None
    assert gateway.calls == ["recoverai:pay_gateway_001"]


def test_executor_payment_link_does_not_count_recovered_revenue() -> None:
    gateway = FakeRecoveryGateway(should_succeed=True)
    provider = FakePaymentLinkProvider()
    executor = RecoveryExecutor(
        gateway=gateway,
        config=build_config(),
        payment_link_provider=provider,
    )

    result = executor.execute(build_request("pay_link_001"))

    assert result.action is RecoveryAction.CREATE_PAYMENT_LINK
    assert result.status is RecoveryStatus.SUCCESS
    assert result.recovered_amount_inr == Decimal("0")
    assert result.payment_link == "https://example.test/recover/pay_link_001"
    assert provider.calls == ["recoverai:pay_link_001"]
    assert gateway.calls == []


def test_executor_payment_link_is_idempotent_in_memory() -> None:
    gateway = FakeRecoveryGateway(should_succeed=True)
    provider = FakePaymentLinkProvider()
    executor = RecoveryExecutor(
        gateway=gateway,
        config=build_config(),
        payment_link_provider=provider,
    )
    request = build_request("pay_link_idempotent_001")

    first = executor.execute(request)
    second = executor.execute(request)

    assert first.status is RecoveryStatus.SUCCESS
    assert second.action is RecoveryAction.IDEMPOTENT_NOOP
    assert second.status is RecoveryStatus.SKIPPED
    assert second.recovered_amount_inr == Decimal("0")
    assert second.payment_link == "https://example.test/recover/pay_link_idempotent_001"
    assert provider.calls == ["recoverai:pay_link_idempotent_001"]
    assert gateway.calls == []


def test_executor_payment_link_idempotency_survives_restart(tmp_path: Path) -> None:
    database = tmp_path / "recovery.db"
    request = build_request("pay_link_restart_001")
    first_gateway = FakeRecoveryGateway(should_succeed=True)
    first_provider = FakePaymentLinkProvider()
    first_executor = RecoveryExecutor(
        gateway=first_gateway,
        config=build_config(),
        state_store=SQLiteRecoveryStateStore(str(database)),
        payment_link_provider=first_provider,
    )

    first = first_executor.execute(request)

    second_gateway = FakeRecoveryGateway(should_succeed=True)
    second_provider = FakePaymentLinkProvider()
    second_executor = RecoveryExecutor(
        gateway=second_gateway,
        config=build_config(),
        state_store=SQLiteRecoveryStateStore(str(database)),
        payment_link_provider=second_provider,
    )

    second = second_executor.execute(request)

    assert first.status is RecoveryStatus.SUCCESS
    assert second.action is RecoveryAction.IDEMPOTENT_NOOP
    assert second.status is RecoveryStatus.SKIPPED
    assert second.recovered_amount_inr == Decimal("0")
    assert second.payment_link == "https://example.test/recover/pay_link_restart_001"
    assert first_provider.calls == ["recoverai:pay_link_restart_001"]
    assert second_provider.calls == []
    assert first_gateway.calls == []
    assert second_gateway.calls == []


def test_executor_payment_link_provider_failure_is_surfaced() -> None:
    gateway = FakeRecoveryGateway(should_succeed=True)
    executor = RecoveryExecutor(
        gateway=gateway,
        config=build_config(),
        payment_link_provider=FailingPaymentLinkProvider(),
    )

    result = executor.execute(build_request("pay_link_failed_001"))

    assert result.action is RecoveryAction.CREATE_PAYMENT_LINK
    assert result.status is RecoveryStatus.FAILED
    assert result.recovered_amount_inr == Decimal("0")
    assert result.payment_link is None
    assert "provider unavailable" in result.reason
    assert gateway.calls == []


def test_failing_payment_link_provider_matches_protocol() -> None:
    provider = FailingPaymentLinkProvider()

    with pytest.raises(RuntimeError, match="provider unavailable"):
        provider.create_payment_link(
            payment_id="pay_link_protocol_001",
            amount_inr=Decimal("1500.00"),
            idempotency_key="recoverai:pay_link_protocol_001",
        )
