"""Marketing API routes — channels, triggers, colors, archetypes, objections."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ...application.use_cases import MarketingUseCases
from ...application.dto import (
    ChannelOut,
    BuyerArchetypeOut,
    ObjectionOut,
    ColorPsychologyOut,
)


def create_marketing_router(uc: MarketingUseCases) -> APIRouter:
    router = APIRouter(tags=["marketing"])

    @router.get("/marketing/channels", response_model=list[ChannelOut])
    def list_channels(channel_type: str | None = Query(None)):
        return uc.list_channels(channel_type=channel_type)

    @router.get("/marketing/archetypes", response_model=list[BuyerArchetypeOut])
    def list_archetypes():
        return uc.list_archetypes()

    @router.get("/marketing/archetypes/by-nt/{nt}", response_model=BuyerArchetypeOut)
    def get_archetype_by_nt(nt: str):
        result = uc.get_archetype_by_nt(nt)
        if not result:
            raise HTTPException(404, "No archetype found for this neurotransmitter")
        return result

    @router.get("/marketing/objections", response_model=list[ObjectionOut])
    def list_objections(q: str | None = Query(None, description="Search objections")):
        return uc.list_objections(query=q)

    @router.get("/marketing/colors", response_model=list[ColorPsychologyOut])
    def list_colors(
        stage: str | None = Query(None, description="Filter by funnel stage code"),
        industry: str | None = Query(None, description="Filter by industry keyword"),
    ):
        return uc.list_colors(stage=stage, industry=industry)

    return router
