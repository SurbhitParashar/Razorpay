from decimal import Decimal

from recoverai.agent.orchestrator import RecoveryAgent
from recoverai.recovery.executor import ExecutionConfig, RecoveryExecutor
from recoverai.recovery.gateway import FakeRecoveryGateway
from recoverai.recovery.policy import RecoveryPolicy
from recoverai.service.schemas import RecoveryRequestSchema
from recoverai.service.service import RecoveryService


def build_service(
    *,
    dry_run: bool = False,
    gateway_success: bool = True,
) -> tuple[RecoveryService, FakeRecoveryGateway]:
    gateway = FakeRecoveryGateway(should_succeed=gateway_success)

    executor = RecoveryExecutor(
        gateway=gateway,
        config=ExecutionConfig(
            max_retries=2,
            max_recovery_amount_inr=Decimal("100000"),
            dry_run=dry_run,
        ),
    )

    policy = RecoveryPolicy(
        threshold=0.5,
        intervention_cost_inr=Decimal("5"),
    )

    agent = RecoveryAgent(
        policy=policy,
        executor=executor,
    )

    return RecoveryService(agent), gateway


def test_service_executes_recovery() -> None:
    service, gateway = build_service()

    response = service.recover(
        RecoveryRequestSchema(
            payment_id="pay_service_001",
            amount_inr=Decimal("1000.00"),
            recovery_probability=0.8,
            attempt_number=1,
        )
    )

    assert response.payment_id == "pay_service_001"
    assert response.decision == "create_payment_link"
    assert response.execution_status == "success"
    assert response.recovered_amount_inr == Decimal("1000.00")
    assert response.payment_link is None
    assert gateway.calls == ["recoverai:pay_service_001"]


def test_service_returns_no_action_below_threshold() -> None:
    service, gateway = build_service()

    response = service.recover(
        RecoveryRequestSchema(
            payment_id="pay_service_002",
            amount_inr=Decimal("1000.00"),
            recovery_probability=0.4,
            attempt_number=1,
        )
    )

    assert response.decision == "no_action"
    assert response.execution_status == "skipped"
    assert response.recovered_amount_inr == Decimal("0")
    assert gateway.calls == []


def test_service_surfaces_gateway_failure() -> None:
    service, gateway = build_service(
        gateway_success=False,
    )

    response = service.recover(
        RecoveryRequestSchema(
            payment_id="pay_service_003",
            amount_inr=Decimal("1000.00"),
            recovery_probability=0.8,
            attempt_number=1,
        )
    )

    assert response.decision == "create_payment_link"
    assert response.execution_status == "failed"
    assert response.recovered_amount_inr == Decimal("0")
    assert gateway.calls == ["recoverai:pay_service_003"]


def test_service_preserves_executor_safety_limit() -> None:
    service, gateway = build_service()

    response = service.recover(
        RecoveryRequestSchema(
            payment_id="pay_service_004",
            amount_inr=Decimal("150000.00"),
            recovery_probability=0.95,
            attempt_number=1,
        )
    )

    assert response.decision == "create_payment_link"
    assert response.execution_status == "skipped"
    assert response.recovered_amount_inr == Decimal("0")
    assert gateway.calls == []
