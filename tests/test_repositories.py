"""Infrastructure layer tests — SQLite repository adapters."""

import pytest

from emomcp.infrastructure.sqlite_repositories import (
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


class TestEmotionRepository:
    def test_get_by_id(self, db):
        repo = SqliteEmotionRepository(db)
        e = repo.get_by_id(1)
        assert e is not None
        assert e.name_en == "Happiness"

    def test_get_by_id_not_found(self, db):
        repo = SqliteEmotionRepository(db)
        assert repo.get_by_id(99999) is None

    def test_get_by_name_en(self, db):
        repo = SqliteEmotionRepository(db)
        e = repo.get_by_name("Fear")
        assert e is not None
        assert e.id == 4

    def test_get_by_name_ru(self, db):
        repo = SqliteEmotionRepository(db)
        e = repo.get_by_name("Любовь")
        assert e is not None
        assert e.name_en == "Love"

    def test_get_by_name_case_insensitive(self, db):
        repo = SqliteEmotionRepository(db)
        e = repo.get_by_name("happiness")
        assert e is not None
        assert e.id == 1

    def test_list_all(self, db):
        repo = SqliteEmotionRepository(db)
        all_emotions = repo.list_all()
        assert len(all_emotions) >= 40

    def test_list_by_valence(self, db):
        repo = SqliteEmotionRepository(db)
        positive = repo.list_all(valence="positive")
        assert all(e.valence == "positive" for e in positive)
        assert len(positive) > 0

    def test_list_micro_only(self, db):
        repo = SqliteEmotionRepository(db)
        micro = repo.list_all(is_micro=True)
        assert all(e.is_micro for e in micro)
        assert len(micro) > 0

    def test_list_non_micro(self, db):
        repo = SqliteEmotionRepository(db)
        base = repo.list_all(is_micro=False)
        assert all(not e.is_micro for e in base)

    def test_list_combined_filters(self, db):
        repo = SqliteEmotionRepository(db)
        result = repo.list_all(valence="positive", activation="high")
        assert all(e.valence == "positive" and e.activation == "high" for e in result)

    def test_search(self, db):
        repo = SqliteEmotionRepository(db)
        results = repo.search("fear")
        assert len(results) > 0
        assert any("fear" in e.name_en.lower() for e in results)

    def test_search_ru(self, db):
        repo = SqliteEmotionRepository(db)
        results = repo.search("любовь")
        assert len(results) > 0

    def test_search_no_results(self, db):
        repo = SqliteEmotionRepository(db)
        assert repo.search("xyznonexistent123") == []


class TestNeurotransmitterRepository:
    def test_get_by_id(self, db):
        repo = SqliteNeurotransmitterRepository(db)
        nt = repo.get_by_id(2)
        assert nt is not None
        assert nt.name == "Dopamine"

    def test_get_by_name(self, db):
        repo = SqliteNeurotransmitterRepository(db)
        nt = repo.get_by_name("Serotonin")
        assert nt is not None
        assert nt.id == 1

    def test_list_all(self, db):
        repo = SqliteNeurotransmitterRepository(db)
        nts = repo.list_all()
        assert len(nts) == 12


class TestEmotionNeurotransmitterRepository:
    def test_get_profile(self, db):
        repo = SqliteEmotionNeurotransmitterRepository(db)
        links = repo.get_profile(13)  # Love
        assert len(links) >= 3
        names = [l.neurotransmitter_id for l in links]
        assert 9 in names  # Oxytocin

    def test_get_emotions_for_nt(self, db):
        repo = SqliteEmotionNeurotransmitterRepository(db)
        links = repo.get_emotions_for_nt(2)  # Dopamine
        assert len(links) > 0

    def test_profile_ordered_by_weight(self, db):
        repo = SqliteEmotionNeurotransmitterRepository(db)
        links = repo.get_profile(4)  # Fear
        weights = [abs(l.weight) for l in links]
        assert weights == sorted(weights, reverse=True)


class TestSimilarityRepository:
    def test_get_for_nt(self, db):
        repo = SqliteNeurotransmitterSimilarityRepository(db)
        sims = repo.get_for_nt(1)  # Serotonin
        assert len(sims) > 0
        assert all(s.nt_id_1 == 1 or s.nt_id_2 == 1 for s in sims)

    def test_get_pair(self, db):
        repo = SqliteNeurotransmitterSimilarityRepository(db)
        sim = repo.get_pair(3, 4)  # Adrenaline vs Norepinephrine
        assert sim is not None
        assert sim.tanimoto >= 0.5

    def test_get_pair_reverse(self, db):
        repo = SqliteNeurotransmitterSimilarityRepository(db)
        sim = repo.get_pair(4, 3)
        assert sim is not None

    def test_get_pair_nonexistent(self, db):
        repo = SqliteNeurotransmitterSimilarityRepository(db)
        assert repo.get_pair(1, 999) is None

    def test_list_all(self, db):
        repo = SqliteNeurotransmitterSimilarityRepository(db)
        all_sims = repo.list_all()
        assert len(all_sims) >= 10
        # Should be sorted descending
        tanimotos = [s.tanimoto for s in all_sims]
        assert tanimotos == sorted(tanimotos, reverse=True)


class TestPathwayRepository:
    def test_get_for_nt(self, db):
        repo = SqliteNeurotransmitterPathwayRepository(db)
        paths = repo.get_for_nt(2)  # Dopamine
        assert len(paths) > 0

    def test_list_all(self, db):
        repo = SqliteNeurotransmitterPathwayRepository(db)
        all_paths = repo.list_all()
        assert len(all_paths) >= 6


class TestFunnelStageRepository:
    def test_list_all(self, db):
        repo = SqliteFunnelStageRepository(db)
        stages = repo.list_all()
        assert len(stages) == 8
        assert stages[0].code == "awareness"

    def test_get_by_code(self, db):
        repo = SqliteFunnelStageRepository(db)
        s = repo.get_by_code("action")
        assert s is not None
        assert s.stage_order == 5

    def test_get_by_code_invalid(self, db):
        repo = SqliteFunnelStageRepository(db)
        assert repo.get_by_code("nonexistent") is None


class TestFunnelEmotionStrategyRepository:
    def test_get_for_stage(self, db):
        repo = SqliteFunnelEmotionStrategyRepository(db)
        strats = repo.get_for_stage(1)  # awareness
        assert len(strats) >= 5
        assert strats[0].effectiveness >= strats[-1].effectiveness

    def test_get_for_emotion(self, db):
        repo = SqliteFunnelEmotionStrategyRepository(db)
        strats = repo.get_for_emotion(5)  # Surprise
        assert len(strats) > 0


class TestMarketingChannelRepository:
    def test_list_all(self, db):
        repo = SqliteMarketingChannelRepository(db)
        channels = repo.list_all()
        assert len(channels) >= 10

    def test_list_by_type(self, db):
        repo = SqliteMarketingChannelRepository(db)
        paid = repo.list_all(channel_type="paid_social")
        assert all(c.channel_type == "paid_social" for c in paid)

    def test_get_by_id(self, db):
        repo = SqliteMarketingChannelRepository(db)
        ch = repo.get_by_id(1)
        assert ch is not None
        assert "Meta" in ch.name


class TestEmotionChannelFitRepository:
    def test_get_for_emotion(self, db):
        repo = SqliteEmotionChannelFitRepository(db)
        fits = repo.get_for_emotion(4)  # Fear
        assert len(fits) > 0
        assert fits[0].fitness >= fits[-1].fitness

    def test_get_for_channel(self, db):
        repo = SqliteEmotionChannelFitRepository(db)
        fits = repo.get_for_channel(1)  # Meta
        assert len(fits) > 0


class TestTriggerWordRepository:
    def test_get_for_emotion(self, db):
        repo = SqliteTriggerWordRepository(db)
        triggers = repo.get_for_emotion(4)  # Fear
        assert len(triggers) > 0
        categories = [t.category for t in triggers]
        assert "scarcity" in categories

    def test_get_for_emotion_and_category(self, db):
        repo = SqliteTriggerWordRepository(db)
        triggers = repo.get_for_emotion_and_category(4, "fomo")
        assert len(triggers) > 0


class TestColorPsychologyRepository:
    def test_list_all(self, db):
        repo = SqliteColorPsychologyRepository(db)
        colors = repo.list_all()
        assert len(colors) >= 10

    def test_get_for_stage(self, db):
        repo = SqliteColorPsychologyRepository(db)
        colors = repo.get_for_stage("trust")
        assert len(colors) > 0

    def test_get_for_industry(self, db):
        repo = SqliteColorPsychologyRepository(db)
        colors = repo.get_for_industry("finance")
        assert len(colors) > 0


class TestCTAPatternRepository:
    def test_get_for_stage(self, db):
        repo = SqliteCTAPatternRepository(db)
        ctas = repo.get_for_stage(5)  # action
        assert len(ctas) > 0

    def test_get_for_emotion(self, db):
        repo = SqliteCTAPatternRepository(db)
        ctas = repo.get_for_emotion(4)  # Fear
        assert len(ctas) > 0


class TestBuyerArchetypeRepository:
    def test_list_all(self, db):
        repo = SqliteBuyerArchetypeRepository(db)
        archetypes = repo.list_all()
        assert len(archetypes) == 7

    def test_get_by_nt(self, db):
        repo = SqliteBuyerArchetypeRepository(db)
        a = repo.get_by_nt("Dopamine")
        assert a is not None
        assert a.urgency_response >= 0.9

    def test_get_by_nt_case_insensitive(self, db):
        repo = SqliteBuyerArchetypeRepository(db)
        a = repo.get_by_nt("dopamine")
        assert a is not None

    def test_get_by_nt_not_found(self, db):
        repo = SqliteBuyerArchetypeRepository(db)
        assert repo.get_by_nt("NonExistentNT") is None


class TestFunnelTemplateRepository:
    def test_list_all(self, db):
        repo = SqliteFunnelTemplateRepository(db)
        templates = repo.list_all()
        assert len(templates) >= 6

    def test_get_by_id(self, db):
        repo = SqliteFunnelTemplateRepository(db)
        t = repo.get_by_id(1)
        assert t is not None
        assert t.code == "ecom_flash"

    def test_get_by_code(self, db):
        repo = SqliteFunnelTemplateRepository(db)
        t = repo.get_by_code("saas_trial")
        assert t is not None

    def test_filter_by_vertical(self, db):
        repo = SqliteFunnelTemplateRepository(db)
        result = repo.list_all(vertical="e-commerce")
        assert len(result) > 0


class TestFunnelTemplateStepRepository:
    def test_get_for_template(self, db):
        repo = SqliteFunnelTemplateStepRepository(db)
        steps = repo.get_for_template(1)  # e-com flash
        assert len(steps) == 4
        assert steps[0].step_order == 1


class TestObjectionHandlingRepository:
    def test_list_all(self, db):
        repo = SqliteObjectionHandlingRepository(db)
        objections = repo.list_all()
        assert len(objections) >= 10

    def test_search(self, db):
        repo = SqliteObjectionHandlingRepository(db)
        results = repo.search("expensive")
        assert len(results) > 0

    def test_search_ru(self, db):
        repo = SqliteObjectionHandlingRepository(db)
        results = repo.search("дорого")
        assert len(results) > 0
