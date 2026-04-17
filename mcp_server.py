"""EmoMCP — MCP server exposing emotions, neurotransmitters, and marketing funnel data."""

import json
import sys
from pathlib import Path

# Ensure emomcp package is importable regardless of cwd
_SRC = str(Path(__file__).resolve().parent / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("emomcp")

sys.modules.setdefault("mcp_server", sys.modules[__name__])

DB_PATH = str(Path(__file__).resolve().parent / "config" / "emotions.db")

# ---------------------------------------------------------------------------
# Helpers — thin wrappers over use cases (no FastAPI dependency)
# ---------------------------------------------------------------------------

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
)

_db = DatabaseConnection(DB_PATH)

_emotion_uc = EmotionUseCases(
    emotions=SqliteEmotionRepository(_db),
    nt_links=SqliteEmotionNeurotransmitterRepository(_db),
    nts=SqliteNeurotransmitterRepository(_db),
    triggers=SqliteTriggerWordRepository(_db),
    funnel_strategies=SqliteFunnelEmotionStrategyRepository(_db),
    channel_fits=SqliteEmotionChannelFitRepository(_db),
    ctas=SqliteCTAPatternRepository(_db),
    colors=SqliteColorPsychologyRepository(_db),
)

_nt_uc = NeurotransmitterUseCases(
    nts=SqliteNeurotransmitterRepository(_db),
    similarities=SqliteNeurotransmitterSimilarityRepository(_db),
    pathways=SqliteNeurotransmitterPathwayRepository(_db),
    nt_links=SqliteEmotionNeurotransmitterRepository(_db),
    emotions=SqliteEmotionRepository(_db),
)

_funnel_uc = FunnelUseCases(
    stages=SqliteFunnelStageRepository(_db),
    strategies=SqliteFunnelEmotionStrategyRepository(_db),
    templates=SqliteFunnelTemplateRepository(_db),
    template_steps=SqliteFunnelTemplateStepRepository(_db),
    emotions=SqliteEmotionRepository(_db),
    channels=SqliteMarketingChannelRepository(_db),
    ctas=SqliteCTAPatternRepository(_db),
    colors=SqliteColorPsychologyRepository(_db),
)

_marketing_uc = MarketingUseCases(
    channels=SqliteMarketingChannelRepository(_db),
    channel_fits=SqliteEmotionChannelFitRepository(_db),
    triggers=SqliteTriggerWordRepository(_db),
    colors=SqliteColorPsychologyRepository(_db),
    archetypes=SqliteBuyerArchetypeRepository(_db),
    objections=SqliteObjectionHandlingRepository(_db),
    emotions=SqliteEmotionRepository(_db),
)


def _entity_to_dict(obj):
    """Convert a frozen dataclass entity to a dict."""
    return {
        k: v for k, v in obj.__dict__.items()
        if not k.startswith("_")
    }


# ---------------------------------------------------------------------------
# Emotion tools
# ---------------------------------------------------------------------------

@mcp.tool()
def list_emotions(
    valence: str | None = None,
    activation: str | None = None,
    is_micro: bool | None = None,
    q: str | None = None,
) -> str:
    """List emotions with optional filters.

    Args:
        valence: Filter by valence — "positive", "negative", "neutral", "ambivalent".
        activation: Filter by activation — "high", "medium", "low".
        is_micro: Set true to get micro-emotions only, false for base emotions.
        q: Search query (matches English and Russian names).
    """
    if q:
        emotions = _emotion_uc.search(q)
    else:
        emotions = _emotion_uc.list_emotions(valence=valence, activation=activation, is_micro=is_micro)
    return json.dumps([_entity_to_dict(e) for e in emotions], ensure_ascii=False, indent=2)


@mcp.tool()
def get_emotion(emotion_id: int) -> str:
    """Get detailed emotion profile: neurotransmitter links, triggers, funnel strategies, channel fits.

    Args:
        emotion_id: Numeric ID of the emotion.
    """
    result = _emotion_uc.get(emotion_id)
    if result is None:
        return json.dumps({"error": f"Emotion {emotion_id} not found"})
    d = _entity_to_dict(result)
    d["neurotransmitter_profile"] = [_entity_to_dict(l) for l in result.neurotransmitter_profile]
    d["trigger_words"] = [_entity_to_dict(t) for t in result.trigger_words]
    d["funnel_strategies"] = [_entity_to_dict(s) for s in result.funnel_strategies]
    d["channel_fits"] = [_entity_to_dict(c) for c in result.channel_fits]
    return json.dumps(d, ensure_ascii=False, indent=2)


@mcp.tool()
def get_emotion_by_name(name: str) -> str:
    """Find an emotion by English or Russian name (case-insensitive).

    Args:
        name: Emotion name in English or Russian, e.g. "Fear" or "Страх".
    """
    result = _emotion_uc.get_by_name(name)
    if result is None:
        return json.dumps({"error": f"Emotion '{name}' not found"})
    d = _entity_to_dict(result)
    d["neurotransmitter_profile"] = [_entity_to_dict(l) for l in result.neurotransmitter_profile]
    d["trigger_words"] = [_entity_to_dict(t) for t in result.trigger_words]
    d["funnel_strategies"] = [_entity_to_dict(s) for s in result.funnel_strategies]
    d["channel_fits"] = [_entity_to_dict(c) for c in result.channel_fits]
    return json.dumps(d, ensure_ascii=False, indent=2)


@mcp.tool()
def get_emotion_marketing_profile(emotion_id: int) -> str:
    """Get full marketing profile for an emotion: NT profile, triggers, channel fits, funnel strategies, CTAs, colors.

    Args:
        emotion_id: Numeric ID of the emotion.
    """
    result = _emotion_uc.get_marketing_profile(emotion_id)
    if result is None:
        return json.dumps({"error": f"Marketing profile for emotion {emotion_id} not found"})
    d = {
        "emotion": _entity_to_dict(result.emotion),
        "neurotransmitter_profile": [_entity_to_dict(n) for n in result.neurotransmitter_profile],
        "triggers": [_entity_to_dict(t) for t in result.triggers],
        "channel_fits": [_entity_to_dict(c) for c in result.channel_fits],
        "funnel_strategies": [_entity_to_dict(s) for s in result.funnel_strategies],
        "ctas": [_entity_to_dict(c) for c in result.ctas],
        "colors": [_entity_to_dict(c) for c in result.colors],
    }
    return json.dumps(d, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Neurotransmitter tools
# ---------------------------------------------------------------------------

@mcp.tool()
def list_neurotransmitters() -> str:
    """List all 12 neurotransmitters with chemical properties."""
    nts = _nt_uc.list_all()
    return json.dumps([_entity_to_dict(nt) for nt in nts], ensure_ascii=False, indent=2)


@mcp.tool()
def get_neurotransmitter(neurotransmitter_id: int) -> str:
    """Get detailed neurotransmitter profile: similarities, pathways, linked emotions.

    Args:
        neurotransmitter_id: Numeric ID of the neurotransmitter.
    """
    result = _nt_uc.get(neurotransmitter_id)
    if result is None:
        return json.dumps({"error": f"Neurotransmitter {neurotransmitter_id} not found"})
    d = _entity_to_dict(result)
    d["similarities"] = [_entity_to_dict(s) for s in result.similarities]
    d["pathways"] = [_entity_to_dict(p) for p in result.pathways]
    d["linked_emotions"] = [_entity_to_dict(e) for e in result.linked_emotions]
    return json.dumps(d, ensure_ascii=False, indent=2)


@mcp.tool()
def get_neurotransmitter_by_name(name: str) -> str:
    """Find a neurotransmitter by name (case-insensitive), e.g. "Dopamine" or "Дофамин".

    Args:
        name: Neurotransmitter name in English or Russian.
    """
    result = _nt_uc.get_by_name(name)
    if result is None:
        return json.dumps({"error": f"Neurotransmitter '{name}' not found"})
    d = _entity_to_dict(result)
    d["similarities"] = [_entity_to_dict(s) for s in result.similarities]
    d["pathways"] = [_entity_to_dict(p) for p in result.pathways]
    d["linked_emotions"] = [_entity_to_dict(e) for e in result.linked_emotions]
    return json.dumps(d, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Funnel tools
# ---------------------------------------------------------------------------

@mcp.tool()
def list_funnel_stages() -> str:
    """List all 8 funnel stages: awareness → interest → desire → trust → action → retention → advocacy → reactivation."""
    stages = _funnel_uc.list_stages()
    return json.dumps([_entity_to_dict(s) for s in stages], ensure_ascii=False, indent=2)


@mcp.tool()
def get_stage_strategy(stage_code: str) -> str:
    """Get top strategies, CTAs, and colors for a funnel stage.

    Args:
        stage_code: One of: awareness, interest, desire, trust, action, retention, advocacy, reactivation.
    """
    result = _funnel_uc.get_stage_strategy(stage_code)
    if result is None:
        return json.dumps({"error": f"Stage '{stage_code}' not found"})
    d = {
        "stage": _entity_to_dict(result.stage),
        "strategies": [_entity_to_dict(s) for s in result.strategies],
        "ctas": [_entity_to_dict(c) for c in result.ctas],
        "colors": [_entity_to_dict(c) for c in result.colors],
    }
    return json.dumps(d, ensure_ascii=False, indent=2)


@mcp.tool()
def list_funnel_templates(vertical: str | None = None) -> str:
    """List pre-built funnel templates, optionally filtered by vertical.

    Args:
        vertical: Filter by vertical, e.g. "e-commerce", "saas", "education".
    """
    templates = _funnel_uc.list_templates(vertical=vertical)
    return json.dumps([_entity_to_dict(t) for t in templates], ensure_ascii=False, indent=2)


@mcp.tool()
def get_funnel_template(template_id: int) -> str:
    """Get funnel template detail with all steps, emotions, channels, and CTAs.

    Args:
        template_id: Numeric ID of the funnel template.
    """
    result = _funnel_uc.get_template(template_id)
    if result is None:
        return json.dumps({"error": f"Template {template_id} not found"})
    d = _entity_to_dict(result)
    d["steps"] = [_entity_to_dict(s) for s in result.steps]
    return json.dumps(d, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Marketing tools
# ---------------------------------------------------------------------------

@mcp.tool()
def list_channels(channel_type: str | None = None) -> str:
    """List marketing channels, optionally filtered by type.

    Args:
        channel_type: Filter by type — "paid_social", "paid_search", "owned", "email", "community", etc.
    """
    channels = _marketing_uc.list_channels(channel_type=channel_type)
    return json.dumps([_entity_to_dict(c) for c in channels], ensure_ascii=False, indent=2)


@mcp.tool()
def list_archetypes() -> str:
    """List all 7 buyer archetypes based on dominant neurotransmitter profiles, sorted by urgency."""
    archetypes = _marketing_uc.list_archetypes()
    return json.dumps([_entity_to_dict(a) for a in archetypes], ensure_ascii=False, indent=2)


@mcp.tool()
def get_archetype_by_nt(neurotransmitter_name: str) -> str:
    """Find buyer archetype by dominant neurotransmitter, e.g. "Dopamine" → Охотник за новизной.

    Args:
        neurotransmitter_name: Name of the neurotransmitter, e.g. "Dopamine", "Serotonin".
    """
    result = _marketing_uc.get_archetype_by_nt(neurotransmitter_name)
    if result is None:
        return json.dumps({"error": f"No archetype for '{neurotransmitter_name}'"})
    return json.dumps(_entity_to_dict(result), ensure_ascii=False, indent=2)


@mcp.tool()
def list_objections(query: str | None = None) -> str:
    """List buyer objections with counter-emotion strategies and copy angles.

    Args:
        query: Search filter (English or Russian), e.g. "expensive" or "дорого".
    """
    objections = _marketing_uc.list_objections(query=query)
    return json.dumps([_entity_to_dict(o) for o in objections], ensure_ascii=False, indent=2)


@mcp.tool()
def list_colors(stage: str | None = None, industry: str | None = None) -> str:
    """List color psychology data for marketing, filterable by funnel stage or industry.

    Args:
        stage: Funnel stage code, e.g. "awareness", "action", "trust".
        industry: Industry vertical, e.g. "B2B", "luxury", "finance", "food".
    """
    colors = _marketing_uc.list_colors(stage=stage, industry=industry)
    return json.dumps([_entity_to_dict(c) for c in colors], ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
