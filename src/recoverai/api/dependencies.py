from __future__ import annotations

from functools import lru_cache

from recoverai.agent.orchestrator import RecoveryAgent
from recoverai.api.config import RecoverySettings
from recoverai.recovery.action import (
    FakePaymentLinkProvider,
    PaymentLinkProvider,
)
from recoverai.recovery.executor import ExecutionConfig, RecoveryExecutor
from recoverai.recovery.gateway import FakeRecoveryGateway
from recoverai.recovery.policy import RecoveryPolicy
from recoverai.recovery.razorpay import RazorpayPaymentLinkProvider
from recoverai.service.service import RecoveryService
from recoverai.state.sqlite import SQLiteRecoveryStateStore


@lru_cache(maxsize=1)
def get_settings() -> RecoverySettings:
    return RecoverySettings.from_environment()


@lru_cache(maxsize=1)
def get_recovery_service() -> RecoveryService:
    settings = get_settings()

    policy = RecoveryPolicy(
        threshold=settings.threshold,
        intervention_cost_inr=settings.intervention_cost_inr,
    )

    gateway = FakeRecoveryGateway()
    payment_link_provider: PaymentLinkProvider

    if settings.razorpay_key_id and settings.razorpay_key_secret:
        payment_link_provider = RazorpayPaymentLinkProvider(
            key_id=settings.razorpay_key_id,
            key_secret=settings.razorpay_key_secret,
        )
    else:
        payment_link_provider = FakePaymentLinkProvider()

    state_store = SQLiteRecoveryStateStore(
        settings.state_database_path,
    )

    executor = RecoveryExecutor(
        gateway=gateway,
        config=ExecutionConfig(
            max_retries=settings.max_retries,
            max_recovery_amount_inr=settings.max_recovery_amount_inr,
            dry_run=settings.dry_run,
        ),
        state_store=state_store,
        payment_link_provider=payment_link_provider,
    )

    agent = RecoveryAgent(
        policy=policy,
        executor=executor,
    )

    return RecoveryService(agent=agent)
