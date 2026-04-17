"""Health check route."""

from __future__ import annotations

from fastapi import APIRouter

from ...application.use_cases import HealthUseCases
from ...application.dto import HealthOut


def create_health_router(uc: HealthUseCases) -> APIRouter:
    router = APIRouter(tags=["health"])

    @router.get("/health", response_model=HealthOut)
    def health_check():
        return uc.check()

    return router
