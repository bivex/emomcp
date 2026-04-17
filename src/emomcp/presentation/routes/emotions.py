"""Emotions API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ...application.use_cases import EmotionUseCases
from ...application.dto import EmotionOut, EmotionDetailOut, EmotionMarketingProfileOut


def create_emotions_router(uc: EmotionUseCases) -> APIRouter:
    router = APIRouter(tags=["emotions"])

    @router.get("/emotions", response_model=list[EmotionOut])
    def list_emotions(
        valence: str | None = Query(None, description="Filter by valence: positive/negative/neutral/ambivalent"),
        activation: str | None = Query(None, description="Filter by activation: high/medium/low"),
        is_micro: bool | None = Query(None, description="Filter micro-expressions"),
        q: str | None = Query(None, description="Search by name"),
    ):
        if q:
            return uc.search(q)
        return uc.list_emotions(valence=valence, activation=activation, is_micro=is_micro)

    @router.get("/emotions/{emotion_id}", response_model=EmotionDetailOut)
    def get_emotion(emotion_id: int):
        result = uc.get(emotion_id)
        if not result:
            raise HTTPException(404, "Emotion not found")
        return result

    @router.get("/emotions/by-name/{name}", response_model=EmotionDetailOut)
    def get_emotion_by_name(name: str):
        result = uc.get_by_name(name)
        if not result:
            raise HTTPException(404, "Emotion not found")
        return result

    @router.get("/emotions/{emotion_id}/marketing", response_model=EmotionMarketingProfileOut)
    def get_emotion_marketing(emotion_id: int):
        result = uc.get_marketing_profile(emotion_id)
        if not result:
            raise HTTPException(404, "Emotion not found")
        return result

    return router
