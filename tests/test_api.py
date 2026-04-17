"""Presentation layer tests — HTTP API endpoints via TestClient."""

import pytest
from httpx import ASGITransport, AsyncClient

from emomcp.infrastructure.config import load_config
from emomcp.presentation.app import create_app


@pytest.fixture(scope="module")
def app():
    cfg = load_config()
    return create_app(cfg)


@pytest.fixture
def client(app):
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
class TestHealthEndpoint:
    async def test_health_returns_ok(self, client):
        r = await client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert len(data["tables"]) >= 20


@pytest.mark.asyncio
class TestEmotionEndpoints:
    async def test_list_emotions(self, client):
        r = await client.get("/api/v1/emotions")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 40

    async def test_list_emotions_filter_valence(self, client):
        r = await client.get("/api/v1/emotions", params={"valence": "positive"})
        assert r.status_code == 200
        data = r.json()
        assert all(e["valence"] == "positive" for e in data)

    async def test_list_emotions_filter_micro(self, client):
        r = await client.get("/api/v1/emotions", params={"is_micro": "true"})
        assert r.status_code == 200
        data = r.json()
        assert all(e["is_micro"] for e in data)

    async def test_search_emotions(self, client):
        r = await client.get("/api/v1/emotions", params={"q": "love"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) > 0
        assert any("Love" in e["name_en"] for e in data)

    async def test_get_emotion(self, client):
        r = await client.get("/api/v1/emotions/1")
        assert r.status_code == 200
        data = r.json()
        assert data["name_en"] == "Happiness"
        assert len(data["neurotransmitter_profile"]) > 0

    async def test_get_emotion_not_found(self, client):
        r = await client.get("/api/v1/emotions/99999")
        assert r.status_code == 404

    async def test_get_emotion_by_name(self, client):
        r = await client.get("/api/v1/emotions/by-name/Fear")
        assert r.status_code == 200
        data = r.json()
        assert data["name_en"] == "Fear"

    async def test_get_emotion_by_name_ru(self, client):
        r = await client.get("/api/v1/emotions/by-name/%D0%9B%D1%8E%D0%B1%D0%BE%D0%B2%D1%8C")
        assert r.status_code == 200
        data = r.json()
        assert data["name_en"] == "Love"

    async def test_get_emotion_by_name_not_found(self, client):
        r = await client.get("/api/v1/emotions/by-name/Nonexistent")
        assert r.status_code == 404

    async def test_get_emotion_marketing_profile(self, client):
        r = await client.get("/api/v1/emotions/4/marketing")
        assert r.status_code == 200
        data = r.json()
        assert data["emotion"]["name_en"] == "Fear"
        assert len(data["neurotransmitter_profile"]) > 0
        assert len(data["triggers"]) > 0
        assert len(data["colors"]) > 0

    async def test_get_emotion_marketing_not_found(self, client):
        r = await client.get("/api/v1/emotions/99999/marketing")
        assert r.status_code == 404


@pytest.mark.asyncio
class TestNeurotransmitterEndpoints:
    async def test_list_neurotransmitters(self, client):
        r = await client.get("/api/v1/neurotransmitters")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 12

    async def test_get_neurotransmitter(self, client):
        r = await client.get("/api/v1/neurotransmitters/2")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Dopamine"
        assert len(data["similarities"]) > 0
        assert len(data["pathways"]) > 0
        assert len(data["linked_emotions"]) > 0

    async def test_get_neurotransmitter_not_found(self, client):
        r = await client.get("/api/v1/neurotransmitters/999")
        assert r.status_code == 404

    async def test_get_neurotransmitter_by_name(self, client):
        r = await client.get("/api/v1/neurotransmitters/by-name/Oxytocin")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Oxytocin"
        assert data["molecular_weight"] > 1000  # peptide

    async def test_get_neurotransmitter_by_name_not_found(self, client):
        r = await client.get("/api/v1/neurotransmitters/by-name/Nonexistent")
        assert r.status_code == 404


@pytest.mark.asyncio
class TestFunnelEndpoints:
    async def test_list_stages(self, client):
        r = await client.get("/api/v1/funnels/stages")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 8
        codes = [s["code"] for s in data]
        assert codes == ["awareness", "interest", "desire", "trust",
                         "action", "retention", "advocacy", "reactivation"]

    async def test_get_stage_strategy(self, client):
        r = await client.get("/api/v1/funnels/stages/awareness/strategy")
        assert r.status_code == 200
        data = r.json()
        assert data["stage"]["code"] == "awareness"
        assert len(data["strategies"]) >= 5
        assert len(data["ctas"]) > 0
        # Strategies sorted by effectiveness desc
        effs = [s["effectiveness"] for s in data["strategies"]]
        assert effs == sorted(effs, reverse=True)

    async def test_get_stage_strategy_not_found(self, client):
        r = await client.get("/api/v1/funnels/stages/nonexistent/strategy")
        assert r.status_code == 404

    async def test_list_templates(self, client):
        r = await client.get("/api/v1/funnels/templates")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 6

    async def test_list_templates_by_vertical(self, client):
        r = await client.get("/api/v1/funnels/templates", params={"vertical": "saas"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) > 0

    async def test_get_template(self, client):
        r = await client.get("/api/v1/funnels/templates/1")
        assert r.status_code == 200
        data = r.json()
        assert data["code"] == "ecom_flash"
        assert len(data["steps"]) == 4
        assert data["steps"][0]["stage_name_ru"] == "Внимание"

    async def test_get_template_not_found(self, client):
        r = await client.get("/api/v1/funnels/templates/999")
        assert r.status_code == 404


@pytest.mark.asyncio
class TestMarketingEndpoints:
    async def test_list_channels(self, client):
        r = await client.get("/api/v1/marketing/channels")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 10

    async def test_list_channels_by_type(self, client):
        r = await client.get("/api/v1/marketing/channels", params={"channel_type": "owned"})
        assert r.status_code == 200
        data = r.json()
        assert all(c["channel_type"] == "owned" for c in data)

    async def test_list_archetypes(self, client):
        r = await client.get("/api/v1/marketing/archetypes")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 7
        # Verify urgency ordering
        urgencies = [a["urgency_response"] for a in data]
        assert urgencies == sorted(urgencies, reverse=True)

    async def test_get_archetype_by_nt(self, client):
        r = await client.get("/api/v1/marketing/archetypes/by-nt/Dopamine")
        assert r.status_code == 200
        data = r.json()
        assert data["name_ru"] == "Охотник за новизной"

    async def test_get_archetype_by_nt_not_found(self, client):
        r = await client.get("/api/v1/marketing/archetypes/by-nt/Nonexistent")
        assert r.status_code == 404

    async def test_list_objections(self, client):
        r = await client.get("/api/v1/marketing/objections")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 10

    async def test_search_objections(self, client):
        r = await client.get("/api/v1/marketing/objections",
                            params={"q": "expensive"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) > 0

    async def test_list_colors(self, client):
        r = await client.get("/api/v1/marketing/colors")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 10

    async def test_list_colors_by_stage(self, client):
        r = await client.get("/api/v1/marketing/colors", params={"stage": "action"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) > 0
        assert any(c["color"] == "Red" for c in data)

    async def test_list_colors_by_industry(self, client):
        r = await client.get("/api/v1/marketing/colors", params={"industry": "B2B"})
        assert r.status_code == 200
        data = r.json()
        assert len(data) > 0


@pytest.mark.asyncio
class TestCrossDomainQueries:
    """Integration tests that verify cross-cutting scenarios."""

    async def test_fear_full_profile_chain(self, client):
        """Verify the full chain: Fear → NT profile → triggers → funnel strategies."""
        # Get Fear emotion detail
        r = await client.get("/api/v1/emotions/4")
        assert r.status_code == 200
        fear = r.json()

        # Verify NT profile
        nts = fear["neurotransmitter_profile"]
        nt_names = [n["neurotransmitter_name"] for n in nts]
        assert "Adrenaline" in nt_names
        assert "Norepinephrine" in nt_names
        assert "Cortisol" in nt_names

        # Verify triggers
        triggers = fear["trigger_words"]
        categories = [t["category"] for t in triggers]
        assert "scarcity" in categories
        assert "fomo" in categories

    async def test_love_marketing_profile_chain(self, client):
        """Love → Oxytocin + Dopamine + PEA → trust stage → bonding channels."""
        r = await client.get("/api/v1/emotions/13/marketing")
        assert r.status_code == 200
        profile = r.json()

        # Love has strong oxytocin binding
        oxy = [n for n in profile["neurotransmitter_profile"]
               if n["neurotransmitter_name"] == "Oxytocin"]
        assert len(oxy) == 1
        assert oxy[0]["weight"] >= 0.9

        # Love triggers include belonging words
        categories = [t["category"] for t in profile["triggers"]]
        assert "belong" in categories

    async def test_funnel_template_step_integrity(self, client):
        """Each template step references valid stages and emotions."""
        r = await client.get("/api/v1/funnels/templates/2")  # SaaS
        assert r.status_code == 200
        tpl = r.json()

        for step in tpl["steps"]:
            assert step["stage_name_ru"]
            assert step["primary_emotion_name_ru"]
            assert step["expected_conv_rate"] > 0
            assert step["expected_conv_rate"] <= 1

    async def test_awareness_stage_uses_surprise_and_fear(self, client):
        """Top awareness strategies should include Surprise and Fear."""
        r = await client.get("/api/v1/funnels/stages/awareness/strategy")
        assert r.status_code == 200
        data = r.json()
        names = [s["emotion_name_ru"] for s in data["strategies"]]
        assert "Удивление" in names
        assert "Страх" in names

    async def test_objection_counter_emotion_resolves(self, client):
        """Every objection has a valid counter-emotion name."""
        r = await client.get("/api/v1/marketing/objections")
        assert r.status_code == 200
        data = r.json()
        for o in data:
            assert o["counter_emotion_name_ru"]
            assert o["trigger_nt"]
            assert o["copy_angle_ru"]
