"""Application layer tests — use cases with real database."""

import pytest

from emomcp.infrastructure.sqlite_repositories import (
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
from emomcp.application.use_cases import (
    EmotionUseCases,
    NeurotransmitterUseCases,
    FunnelUseCases,
    MarketingUseCases,
    HealthUseCases,
)


@pytest.fixture
def emotion_uc(db):
    return EmotionUseCases(
        emotions=SqliteEmotionRepository(db),
        nt_links=SqliteEmotionNeurotransmitterRepository(db),
        nts=SqliteNeurotransmitterRepository(db),
        triggers=SqliteTriggerWordRepository(db),
        funnel_strategies=SqliteFunnelEmotionStrategyRepository(db),
        channel_fits=SqliteEmotionChannelFitRepository(db),
        ctas=SqliteCTAPatternRepository(db),
        colors=SqliteColorPsychologyRepository(db),
    )


@pytest.fixture
def nt_uc(db):
    return NeurotransmitterUseCases(
        nts=SqliteNeurotransmitterRepository(db),
        similarities=SqliteNeurotransmitterSimilarityRepository(db),
        pathways=SqliteNeurotransmitterPathwayRepository(db),
        nt_links=SqliteEmotionNeurotransmitterRepository(db),
        emotions=SqliteEmotionRepository(db),
    )


@pytest.fixture
def funnel_uc(db):
    return FunnelUseCases(
        stages=SqliteFunnelStageRepository(db),
        strategies=SqliteFunnelEmotionStrategyRepository(db),
        templates=SqliteFunnelTemplateRepository(db),
        template_steps=SqliteFunnelTemplateStepRepository(db),
        emotions=SqliteEmotionRepository(db),
        channels=SqliteMarketingChannelRepository(db),
        ctas=SqliteCTAPatternRepository(db),
        colors=SqliteColorPsychologyRepository(db),
    )


@pytest.fixture
def marketing_uc(db):
    return MarketingUseCases(
        channels=SqliteMarketingChannelRepository(db),
        channel_fits=SqliteEmotionChannelFitRepository(db),
        triggers=SqliteTriggerWordRepository(db),
        colors=SqliteColorPsychologyRepository(db),
        archetypes=SqliteBuyerArchetypeRepository(db),
        objections=SqliteObjectionHandlingRepository(db),
        emotions=SqliteEmotionRepository(db),
    )


# ─── EmotionUseCases ───

class TestEmotionUseCases:
    def test_get_existing(self, emotion_uc):
        result = emotion_uc.get(1)
        assert result is not None
        assert result.name_en == "Happiness"
        assert result.name_ru == "Радость"
        assert result.valence == "positive"

    def test_get_not_found(self, emotion_uc):
        assert emotion_uc.get(99999) is None

    def test_get_by_name(self, emotion_uc):
        result = emotion_uc.get_by_name("Love")
        assert result is not None
        assert result.id == 13

    def test_get_by_name_ru(self, emotion_uc):
        result = emotion_uc.get_by_name("Страх")
        assert result is not None
        assert result.name_en == "Fear"

    def test_get_by_name_not_found(self, emotion_uc):
        assert emotion_uc.get_by_name("NonexistentEmotion") is None

    def test_list_all(self, emotion_uc):
        emotions = emotion_uc.list_emotions()
        assert len(emotions) >= 40

    def test_list_by_valence(self, emotion_uc):
        positive = emotion_uc.list_emotions(valence="positive")
        assert all(e.valence == "positive" for e in positive)

    def test_list_micro(self, emotion_uc):
        micro = emotion_uc.list_emotions(is_micro=True)
        assert all(e.is_micro for e in micro)

    def test_search(self, emotion_uc):
        results = emotion_uc.search("fear")
        assert len(results) > 0
        assert any("fear" in e.name_en.lower() for e in results)

    def test_get_detail_has_nt_profile(self, emotion_uc):
        result = emotion_uc.get(13)  # Love
        assert result is not None
        assert len(result.neurotransmitter_profile) >= 3
        nt_names = [l.neurotransmitter_name for l in result.neurotransmitter_profile]
        assert "Oxytocin" in nt_names
        assert "Dopamine" in nt_names

    def test_get_detail_has_triggers(self, emotion_uc):
        result = emotion_uc.get(4)  # Fear
        assert result is not None
        assert len(result.trigger_words) > 0

    def test_get_marketing_profile(self, emotion_uc):
        result = emotion_uc.get_marketing_profile(4)
        assert result is not None
        assert result.emotion.name_en == "Fear"
        assert len(result.neurotransmitter_profile) > 0
        assert len(result.triggers) > 0
        assert len(result.colors) > 0

    def test_get_marketing_profile_not_found(self, emotion_uc):
        assert emotion_uc.get_marketing_profile(99999) is None


# ─── NeurotransmitterUseCases ───

class TestNeurotransmitterUseCases:
    def test_get_existing(self, nt_uc):
        result = nt_uc.get(2)
        assert result is not None
        assert result.name == "Dopamine"

    def test_get_by_name(self, nt_uc):
        result = nt_uc.get_by_name("Serotonin")
        assert result is not None
        assert result.id == 1

    def test_get_not_found(self, nt_uc):
        assert nt_uc.get(999) is None

    def test_list_all(self, nt_uc):
        nts = nt_uc.list_all()
        assert len(nts) == 12

    def test_get_similarities(self, nt_uc):
        sims = nt_uc.get_similarities(3)  # Adrenaline
        assert len(sims) > 0
        # Should include Norepinephrine (high similarity)
        partner_names = [s.partner_name for s in sims]
        assert "Norepinephrine" in partner_names

    def test_get_detail_has_similarities(self, nt_uc):
        result = nt_uc.get(1)  # Serotonin
        assert result is not None
        assert len(result.similarities) > 0

    def test_get_detail_has_pathways(self, nt_uc):
        result = nt_uc.get(2)  # Dopamine
        assert result is not None
        assert len(result.pathways) > 0

    def test_get_detail_has_linked_emotions(self, nt_uc):
        result = nt_uc.get(2)  # Dopamine
        assert result is not None
        assert len(result.linked_emotions) > 0


# ─── FunnelUseCases ───

class TestFunnelUseCases:
    def test_list_stages(self, funnel_uc):
        stages = funnel_uc.list_stages()
        assert len(stages) == 8
        assert stages[0].code == "awareness"
        assert stages[-1].code == "reactivation"

    def test_get_stage_strategy(self, funnel_uc):
        result = funnel_uc.get_stage_strategy("awareness")
        assert result is not None
        assert result.stage.code == "awareness"
        assert len(result.strategies) >= 5
        assert len(result.ctas) > 0
        assert result.strategies[0].effectiveness >= result.strategies[-1].effectiveness

    def test_get_stage_strategy_not_found(self, funnel_uc):
        assert funnel_uc.get_stage_strategy("nonexistent") is None

    def test_list_templates(self, funnel_uc):
        templates = funnel_uc.list_templates()
        assert len(templates) >= 6

    def test_list_templates_by_vertical(self, funnel_uc):
        result = funnel_uc.list_templates(vertical="e-commerce")
        assert len(result) > 0

    def test_get_template(self, funnel_uc):
        result = funnel_uc.get_template(1)
        assert result is not None
        assert result.code == "ecom_flash"
        assert len(result.steps) == 4
        assert result.steps[0].step_order == 1
        assert result.steps[0].expected_conv_rate > 0

    def test_get_template_not_found(self, funnel_uc):
        assert funnel_uc.get_template(999) is None


# ─── MarketingUseCases ───

class TestMarketingUseCases:
    def test_list_channels(self, marketing_uc):
        channels = marketing_uc.list_channels()
        assert len(channels) >= 10

    def test_list_channels_by_type(self, marketing_uc):
        channels = marketing_uc.list_channels(channel_type="paid_social")
        assert all(c.channel_type == "paid_social" for c in channels)

    def test_list_archetypes(self, marketing_uc):
        archetypes = marketing_uc.list_archetypes()
        assert len(archetypes) == 7
        codes = [a.code for a in archetypes]
        assert "dopamine_chaser" in codes

    def test_get_archetype_by_nt(self, marketing_uc):
        a = marketing_uc.get_archetype_by_nt("Adrenaline")
        assert a is not None
        assert a.urgency_response >= 0.9

    def test_get_archetype_by_nt_not_found(self, marketing_uc):
        assert marketing_uc.get_archetype_by_nt("Nonexistent") is None

    def test_list_objections(self, marketing_uc):
        objections = marketing_uc.list_objections()
        assert len(objections) >= 10
        assert all(o.counter_emotion_name_ru for o in objections)

    def test_search_objections(self, marketing_uc):
        results = marketing_uc.list_objections(query="дорого")
        assert len(results) > 0
        assert "Слишком дорого" in results[0].objection_ru

    def test_list_colors(self, marketing_uc):
        colors = marketing_uc.list_colors()
        assert len(colors) >= 10

    def test_list_colors_by_stage(self, marketing_uc):
        colors = marketing_uc.list_colors(stage="trust")
        assert len(colors) > 0
        color_names = [c.color for c in colors]
        assert "Blue" in color_names or "Green" in color_names

    def test_list_colors_by_industry(self, marketing_uc):
        colors = marketing_uc.list_colors(industry="luxury")
        assert len(colors) > 0
