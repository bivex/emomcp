"""FastAPI application factory — wires infrastructure to use cases to routes."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from ..infrastructure.config import load_config
from ..infrastructure.sqlite_repositories import (
    DatabaseConnection,
    SqliteEmotionRepository,
    SqliteNeurotransmitterRepository,
    SqliteEmotionNeurotransmitterRepository,
    SqliteNeurotransmitterSimilarityRepository,
    SqliteNeurotransmitterPathwayRepository,
    SqliteFunnelStageRepository,
    SqliteFunnelEmotionStrategyRepository,
    SqliteMarketingChannelRepository,
    SqliteEmotionChannelFitRepository,
    SqliteTriggerWordRepository,
    SqliteColorPsychologyRepository,
    SqliteCTAPatternRepository,
    SqliteBuyerArchetypeRepository,
    SqliteFunnelTemplateRepository,
    SqliteFunnelTemplateStepRepository,
    SqliteObjectionHandlingRepository,
)
from ..application.use_cases import (
    EmotionUseCases,
    NeurotransmitterUseCases,
    FunnelUseCases,
    MarketingUseCases,
    HealthUseCases,
)
from .routes.emotions import create_emotions_router
from .routes.neurotransmitters import create_neurotransmitters_router
from .routes.funnels import create_funnels_router
from .routes.marketing import create_marketing_router
from .routes.health import create_health_router


def create_app(config: dict | None = None) -> FastAPI:
    if config is None:
        config = load_config()

    logging.basicConfig(
        level=config["logging"]["level"],
        format=config["logging"]["format"],
    )

    app = FastAPI(
        title="emomcp",
        version="0.1.0",
        description="Emotions, neurochemistry, and marketing funnels API",
    )

    db = DatabaseConnection(config["database"]["path"])

    # Wire repositories (adapters)
    emotion_repo = SqliteEmotionRepository(db)
    nt_repo = SqliteNeurotransmitterRepository(db)
    nt_link_repo = SqliteEmotionNeurotransmitterRepository(db)
    similarity_repo = SqliteNeurotransmitterSimilarityRepository(db)
    pathway_repo = SqliteNeurotransmitterPathwayRepository(db)
    stage_repo = SqliteFunnelStageRepository(db)
    strategy_repo = SqliteFunnelEmotionStrategyRepository(db)
    channel_repo = SqliteMarketingChannelRepository(db)
    fit_repo = SqliteEmotionChannelFitRepository(db)
    trigger_repo = SqliteTriggerWordRepository(db)
    color_repo = SqliteColorPsychologyRepository(db)
    cta_repo = SqliteCTAPatternRepository(db)
    archetype_repo = SqliteBuyerArchetypeRepository(db)
    template_repo = SqliteFunnelTemplateRepository(db)
    step_repo = SqliteFunnelTemplateStepRepository(db)
    objection_repo = SqliteObjectionHandlingRepository(db)

    # Wire use cases (application layer)
    emotion_uc = EmotionUseCases(
        emotions=emotion_repo, nt_links=nt_link_repo, nts=nt_repo,
        triggers=trigger_repo, funnel_strategies=strategy_repo,
        channel_fits=fit_repo, ctas=cta_repo, colors=color_repo,
    )
    nt_uc = NeurotransmitterUseCases(
        nts=nt_repo, similarities=similarity_repo, pathways=pathway_repo,
        nt_links=nt_link_repo, emotions=emotion_repo,
    )
    funnel_uc = FunnelUseCases(
        stages=stage_repo, strategies=strategy_repo, templates=template_repo,
        template_steps=step_repo, emotions=emotion_repo, channels=channel_repo,
        ctas=cta_repo, colors=color_repo,
    )
    marketing_uc = MarketingUseCases(
        channels=channel_repo, channel_fits=fit_repo, triggers=trigger_repo,
        colors=color_repo, archetypes=archetype_repo, objections=objection_repo,
        emotions=emotion_repo,
    )
    health_uc = HealthUseCases(
        db_path=config["database"]["path"],
        conn=db.raw_connection,
    )

    # Wire routes (presentation layer)
    app.include_router(create_emotions_router(emotion_uc), prefix="/api/v1")
    app.include_router(create_neurotransmitters_router(nt_uc), prefix="/api/v1")
    app.include_router(create_funnels_router(funnel_uc), prefix="/api/v1")
    app.include_router(create_marketing_router(marketing_uc), prefix="/api/v1")
    app.include_router(create_health_router(health_uc))

    @app.on_event("shutdown")
    def _shutdown() -> None:
        db.close()

    return app
