from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


def recovery_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    del request

    return JSONResponse(
        status_code=502,
        content={
            "error": "recovery_execution_failed",
            "detail": str(exc),
        },
    )
