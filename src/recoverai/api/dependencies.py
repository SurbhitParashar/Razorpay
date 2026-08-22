from __future__ import annotations

from decimal import Decimal
from functools import lru_cache

from recoverai.agent.orchestrator import RecoveryAgent
from recoverai.recovery.executor import ExecutionConfig, RecoveryExecutor
from recoverai.recovery.gateway import FakeRecoveryGateway
from recoverai.recovery.policy import RecoveryPolicy
from recoverai.service.service import RecoveryService


@lru_cache(maxsize=1)
def get_recovery_service() -> RecoveryService:
    policy = RecoveryPolicy(
        threshold=0.5,
        intervention_cost_inr=Decimal("5.00"),
    )

    gateway = FakeRecoveryGateway()

    config = ExecutionConfig(
        max_retries=3,
        max_recovery_amount_inr=Decimal("100000.00"),
        dry_run=False,
    )

    executor = RecoveryExecutor(
        gateway=gateway,
        config=config,
    )

    agent = RecoveryAgent(
        policy=policy,
        executor=executor,
    )

    return RecoveryService(agent=agent)
