from decimal import Decimal
from pathlib import Path

from recoverai.recovery.executor import ExecutionConfig, RecoveryExecutor
from recoverai.recovery.gateway import FakeRecoveryGateway
from recoverai.recovery.models import (
    RecoveryAction,
    RecoveryRequest,
    RecoveryStatus,
)
from recoverai.state.sqlite import SQLiteRecoveryStateStore


def test_executor_preserves_idempotency_across_instances(
    tmp_path: Path,
) -> None:
    database = tmp_path / "recovery.db"

    request = RecoveryRequest(
        payment_id="pay_restart_001",
        amount_inr=Decimal("1500.00"),
        recovery_probability=0.95,
        threshold=0.5,
        attempt_number=1,
    )

    config = ExecutionConfig(
        max_retries=3,
        max_recovery_amount_inr=Decimal("10000.00"),
        dry_run=False,
    )

    first_gateway = FakeRecoveryGateway(should_succeed=True)

    first_executor = RecoveryExecutor(
        gateway=first_gateway,
        config=config,
        state_store=SQLiteRecoveryStateStore(str(database)),
    )

    first_result = first_executor.execute(request)

    assert first_result.action is RecoveryAction.RECOVER
    assert first_result.status is RecoveryStatus.SUCCESS
    assert first_gateway.calls == ["recoverai:pay_restart_001"]

    second_gateway = FakeRecoveryGateway(should_succeed=True)

    second_executor = RecoveryExecutor(
        gateway=second_gateway,
        config=config,
        state_store=SQLiteRecoveryStateStore(str(database)),
    )

    second_result = second_executor.execute(request)

    assert second_result.action is RecoveryAction.IDEMPOTENT_NOOP
    assert second_result.status is RecoveryStatus.SKIPPED
    assert second_result.recovered_amount_inr == Decimal("0")
    assert second_gateway.calls == []
