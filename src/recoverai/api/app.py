from __future__ import annotations

from fastapi import FastAPI

from recoverai.api.routes import router

app = FastAPI(
    title="RecoverAI",
    version="0.1.0",
    description="AI-powered revenue recovery service.",
)

app.include_router(router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
