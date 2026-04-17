"""Neurotransmitters API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...application.use_cases import NeurotransmitterUseCases
from ...application.dto import NeurotransmitterOut, NeurotransmitterDetailOut


def create_neurotransmitters_router(uc: NeurotransmitterUseCases) -> APIRouter:
    router = APIRouter(tags=["neurotransmitters"])

    @router.get("/neurotransmitters", response_model=list[NeurotransmitterOut])
    def list_neurotransmitters():
        return uc.list_all()

    @router.get("/neurotransmitters/{nt_id}", response_model=NeurotransmitterDetailOut)
    def get_neurotransmitter(nt_id: int):
        result = uc.get(nt_id)
        if not result:
            raise HTTPException(404, "Neurotransmitter not found")
        return result

    @router.get("/neurotransmitters/by-name/{name}", response_model=NeurotransmitterDetailOut)
    def get_neurotransmitter_by_name(name: str):
        result = uc.get_by_name(name)
        if not result:
            raise HTTPException(404, "Neurotransmitter not found")
        return result

    return router
