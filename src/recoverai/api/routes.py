from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from recoverai.api.dependencies import get_recovery_service
from recoverai.service.schemas import (
    RecoveryMetricsResponseSchema,
    RecoveryOutcomeRequestSchema,
    RecoveryOutcomeResponseSchema,
    RecoveryRequestSchema,
    RecoveryResponseSchema,
)
from recoverai.service.service import RecoveryService

router = APIRouter(prefix="/v1", tags=["recovery"])

RecoveryServiceDependency = Annotated[
    RecoveryService,
    Depends(get_recovery_service),
]


@router.post(
    "/recoveries",
    response_model=RecoveryResponseSchema,
)
def create_recovery(
    request: RecoveryRequestSchema,
    service: RecoveryServiceDependency,
) -> RecoveryResponseSchema:
    return service.recover(request)


@router.post(
    "/recovery-outcomes",
    response_model=RecoveryOutcomeResponseSchema,
)
def record_recovery_outcome(
    request: RecoveryOutcomeRequestSchema,
    service: RecoveryServiceDependency,
) -> RecoveryOutcomeResponseSchema:
    return service.record_recovery_outcome(request)


@router.get(
    "/recovery-metrics",
    response_model=RecoveryMetricsResponseSchema,
)
def get_recovery_metrics(
    service: RecoveryServiceDependency,
) -> RecoveryMetricsResponseSchema:
    return service.get_recovery_metrics()
