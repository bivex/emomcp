# EmoMCP

Emotions, neurochemistry & marketing funnel database with MCP server and HTTP API.

**260 emotions**, **12 neurotransmitters**, **8-stage funnel system**, buyer archetypes, color psychology, CTA patterns, trigger words — all linked by neurochemical weights.

## What's inside

- 260 emotions (174 base + 36 marketing + 50 unique/cultural) with valence, activation, approach/avoidance
- 12 neurotransmitters (Serotonin, Dopamine, Adrenaline, Norepinephrine, GABA, Glutamate, Acetylcholine, PEA, Oxytocin, Vasopressin, Cortisol, Testosterone) with SMILES, molecular descriptors, PubChem data
- 88 Tanimoto molecular similarities between neurotransmitters
- 8 biosynthetic pathways (PEA→Dopamine→Norepinephrine→Adrenaline, Glutamate↔GABA, etc.)
- 298 emotion-neurotransmitter weighted links (positive/negative)
- 8-stage marketing funnel (awareness → interest → desire → trust → action → retention → advocacy → reactivation)
- 70 funnel emotion strategies with effectiveness scores
- 92 emotion-channel fits across 15 marketing channels
- 65 trigger word sets (Russian + English) with power scores
- 51 CTA patterns with urgency levels and conversion lift
- 12 color psychology entries by stage and industry
- 7 buyer archetypes based on dominant neurotransmitter profiles
- 8 pre-built funnel templates with 33 steps across verticals
- 14 objection handling entries with counter-emotion strategies

## Quick start

```bash
cd emomcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### HTTP API

```bash
python run.py
# → http://localhost:8800
```

Endpoints:

| Path | Description |
|------|-------------|
| `GET /health` | Health check, table counts |
| `GET /api/v1/emotions` | List emotions (filter: `valence`, `is_micro`, `q`) |
| `GET /api/v1/emotions/{id}` | Emotion detail with NT profile, triggers |
| `GET /api/v1/emotions/by-name/{name}` | Find by English/Russian name |
| `GET /api/v1/emotions/{id}/marketing` | Full marketing profile |
| `GET /api/v1/neurotransmitters` | List all 12 NTs |
| `GET /api/v1/neurotransmitters/{id}` | NT detail with similarities, pathways, linked emotions |
| `GET /api/v1/neurotransmitters/by-name/{name}` | Find NT by name |
| `GET /api/v1/funnels/stages` | List 8 funnel stages |
| `GET /api/v1/funnels/stages/{code}/strategy` | Stage strategies, CTAs, colors |
| `GET /api/v1/funnels/templates` | List funnel templates (filter: `vertical`) |
| `GET /api/v1/funnels/templates/{id}` | Template detail with steps |
| `GET /api/v1/marketing/channels` | List channels (filter: `channel_type`) |
| `GET /api/v1/marketing/archetypes` | List buyer archetypes |
| `GET /api/v1/marketing/archetypes/by-nt/{name}` | Archetype by neurotransmitter |
| `GET /api/v1/marketing/objections` | List objections (filter: `q`) |
| `GET /api/v1/marketing/colors` | Color psychology (filter: `stage`, `industry`) |

### MCP Server

16 tools for AI assistants (Kilo, Claude Code, etc.):

```bash
pip install mcp
.venv/bin/python3 mcp_server.py
```

Tools: `list_emotions`, `get_emotion`, `get_emotion_by_name`, `get_emotion_marketing_profile`, `list_neurotransmitters`, `get_neurotransmitter`, `get_neurotransmitter_by_name`, `list_funnel_stages`, `get_stage_strategy`, `list_funnel_templates`, `get_funnel_template`, `list_channels`, `list_archetypes`, `get_archetype_by_nt`, `list_objections`, `list_colors`.

## Architecture

Hexagonal / Ports & Adapters (DDD, Clean Architecture):

```
src/emomcp/
  domain/          — entities, repository interfaces, domain services
  application/     — use cases, DTOs
  infrastructure/  — SQLite repositories, config
  presentation/    — FastAPI app, routes
```

## Tests

```bash
.venv/bin/python3 -m pytest tests/ -v
# 154 tests, all passing
```

## License

MIT
