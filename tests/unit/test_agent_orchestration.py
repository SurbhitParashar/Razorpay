from decimal import Decimal

from recoverai.agent.orchestrator import RecoveryAgent
from recoverai.recovery.executor import ExecutionConfig, RecoveryExecutor
from recoverai.recovery.gateway import FakeRecoveryGateway
from recoverai.recovery.models import RecoveryAction, RecoveryStatus
from recoverai.recovery.policy import RecoveryPolicy


def build_agent(
    *,
    dry_run: bool = True,
    should_succeed: bool = True,
) -> tuple[RecoveryAgent, FakeRecoveryGateway]:
    gateway = FakeRecoveryGateway(should_succeed=should_succeed)

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

    return RecoveryAgent(policy=policy, executor=executor), gateway


def test_agent_recommends_recovery_for_profitable_payment() -> None:
    agent, _ = build_agent()

    decision = agent.decide(
        payment_id="pay_001",
        payment_amount_inr=Decimal("1000"),
        recovery_probability=0.8,
    )

    assert decision.action is RecoveryAction.RECOVER
    assert decision.expected_net_value_inr == Decimal("795.0")


def test_agent_recommends_no_action_below_threshold() -> None:
    agent, _ = build_agent()

    decision = agent.decide(
        payment_id="pay_002",
        payment_amount_inr=Decimal("1000"),
        recovery_probability=0.4,
    )

    assert decision.action is RecoveryAction.NO_ACTION


def test_agent_recommends_no_action_when_economics_are_negative() -> None:
    agent, _ = build_agent()

    decision = agent.decide(
        payment_id="pay_003",
        payment_amount_inr=Decimal("5"),
        recovery_probability=0.5,
    )

    assert decision.action is RecoveryAction.NO_ACTION
    assert decision.expected_net_value_inr == Decimal("-2.5")


def test_agent_executes_through_executor() -> None:
    agent, gateway = build_agent(dry_run=False)

    execution = agent.execute(
        payment_id="pay_004",
        payment_amount_inr=Decimal("1000"),
        recovery_probability=0.8,
        attempt_number=1,
    )

    assert execution.decision.action is RecoveryAction.RECOVER
    assert execution.result.status is RecoveryStatus.SUCCESS
    assert execution.result.recovered_amount_inr == Decimal("1000")
    assert gateway.calls == ["recoverai:pay_004"]


def test_agent_preserves_executor_idempotency() -> None:
    agent, gateway = build_agent(dry_run=False)

    first = agent.execute(
        payment_id="pay_005",
        payment_amount_inr=Decimal("1000"),
        recovery_probability=0.8,
        attempt_number=1,
    )

    second = agent.execute(
        payment_id="pay_005",
        payment_amount_inr=Decimal("1000"),
        recovery_probability=0.8,
        attempt_number=1,
    )

    assert first.result.status is RecoveryStatus.SUCCESS
    assert second.result.action is RecoveryAction.IDEMPOTENT_NOOP
    assert len(gateway.calls) == 1


def test_agent_keeps_executor_safety_limit() -> None:
    agent, gateway = build_agent(dry_run=False)

    execution = agent.execute(
        payment_id="pay_006",
        payment_amount_inr=Decimal("150000"),
        recovery_probability=0.9,
        attempt_number=1,
    )

    assert execution.decision.action is RecoveryAction.RECOVER
    assert execution.result.action is RecoveryAction.STOPPED
    assert execution.result.status is RecoveryStatus.SKIPPED
    assert gateway.calls == []
