from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from recoverai.api.dependencies import get_recovery_service
from recoverai.service.schemas import (
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
