"""Funnels API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ...application.use_cases import FunnelUseCases
from ...application.dto import (
    FunnelStageOut,
    StageStrategyOut,
    FunnelTemplateOut,
    FunnelTemplateDetailOut,
)


def create_funnels_router(uc: FunnelUseCases) -> APIRouter:
    router = APIRouter(tags=["funnels"])

    @router.get("/funnels/stages", response_model=list[FunnelStageOut])
    def list_stages():
        return uc.list_stages()

    @router.get("/funnels/stages/{stage_code}/strategy", response_model=StageStrategyOut)
    def get_stage_strategy(stage_code: str):
        result = uc.get_stage_strategy(stage_code)
        if not result:
            raise HTTPException(404, "Funnel stage not found")
        return result

    @router.get("/funnels/templates", response_model=list[FunnelTemplateOut])
    def list_templates(vertical: str | None = Query(None)):
        return uc.list_templates(vertical=vertical)

    @router.get("/funnels/templates/{template_id}", response_model=FunnelTemplateDetailOut)
    def get_template(template_id: int):
        result = uc.get_template(template_id)
        if not result:
            raise HTTPException(404, "Funnel template not found")
        return result

    return router
