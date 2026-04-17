"""Data Transfer Objects — clean serialization boundaries between layers."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Emotions ──

class EmotionOut(BaseModel):
    id: int
    name_en: str
    name_ru: str
    valence: str | None
    activation: str | None
    is_micro: bool
    micro_marker: str | None


class EmotionDetailOut(EmotionOut):
    neurotransmitter_profile: list["NeurotransmitterLinkOut"] = Field(default_factory=list)
    trigger_words: list["TriggerWordOut"] = Field(default_factory=list)
    funnel_strategies: list["FunnelStrategyOut"] = Field(default_factory=list)
    channel_fits: list["EmotionChannelFitOut"] = Field(default_factory=list)


# ── Neurotransmitters ──

class NeurotransmitterOut(BaseModel):
    id: int
    name: str
    name_ru: str
    smiles: str
    canonical_smiles: str | None
    murcko_scaffold: str | None
    generic_scaffold: str | None
    molecular_formula: str
    molecular_weight: float
    logp: float
    tpsa: float
    h_bond_donors: int
    h_bond_acceptors: int
    rotatable_bonds: int
    aromatic_rings: int
    fraction_csp3: float
    pubchem_cid: int
    inchikey: str
    role: str
    role_ru: str


class NeurotransmitterDetailOut(NeurotransmitterOut):
    similarities: list["SimilarityOut"] = Field(default_factory=list)
    pathways: list["PathwayOut"] = Field(default_factory=list)
    linked_emotions: list["NeurotransmitterLinkOut"] = Field(default_factory=list)


class NeurotransmitterLinkOut(BaseModel):
    neurotransmitter_id: int
    neurotransmitter_name: str
    weight: float
    mechanism_ru: str
    is_excitatory: bool


class SimilarityOut(BaseModel):
    partner_id: int
    partner_name: str
    tanimoto: float
    structural_relation: str


class PathwayOut(BaseModel):
    from_nt_id: int
    to_nt_id: int
    pathway_type: str
    enzyme: str
    description_ru: str


# ── Funnel ──

class FunnelStageOut(BaseModel):
    id: int
    code: str
    name: str
    name_ru: str
    stage_order: int
    goal_ru: str
    key_nt: str
    description_ru: str


class FunnelStrategyOut(BaseModel):
    emotion_id: int
    emotion_name_ru: str
    effectiveness: float
    role_ru: str


class FunnelTemplateOut(BaseModel):
    id: int
    code: str
    name: str
    name_ru: str
    vertical: str
    vertical_ru: str
    description_ru: str


class FunnelTemplateStepOut(BaseModel):
    step_order: int
    stage_name_ru: str
    primary_emotion_name_ru: str
    secondary_emotion_name_ru: str | None
    channel_name_ru: str | None
    expected_conv_rate: float
    ctas_ru: str


class FunnelTemplateDetailOut(FunnelTemplateOut):
    steps: list[FunnelTemplateStepOut] = Field(default_factory=list)


# ── Marketing ──

class ChannelOut(BaseModel):
    id: int
    code: str
    name: str
    name_ru: str
    channel_type: str
    avg_cpc_usd: float | None
    best_funnel_stage: str
    attention_span_sec: int | None
    description_ru: str


class EmotionChannelFitOut(BaseModel):
    channel_id: int
    channel_name_ru: str
    fitness: float
    ad_format_ru: str


class TriggerWordOut(BaseModel):
    category: str
    words_ru: str
    words_en: str
    power_score: float


class ColorPsychologyOut(BaseModel):
    color: str
    hex_code: str
    primary_emotion_id: int
    arousal_level: str
    funnel_stage: str
    industries_ru: str


class CTAOut(BaseModel):
    id: int
    funnel_stage_id: int
    emotion_id: int
    cta_ru: str
    cta_en: str
    urgency: str
    conversion_lift: float


class BuyerArchetypeOut(BaseModel):
    id: int
    code: str
    name: str
    name_ru: str
    dominant_nt: str
    decision_style_ru: str
    price_sensitivity: float
    risk_tolerance: float
    social_proof_weight: float
    urgency_response: float
    description_ru: str


class ObjectionOut(BaseModel):
    id: int
    objection: str
    objection_ru: str
    counter_emotion_id: int
    counter_emotion_name_ru: str
    trigger_nt: str
    copy_angle_ru: str


# ── Aggregate responses ──

class StageStrategyOut(BaseModel):
    stage: FunnelStageOut
    strategies: list[FunnelStrategyOut]
    ctas: list[CTAOut]
    colors: list[ColorPsychologyOut]


class EmotionMarketingProfileOut(BaseModel):
    emotion: EmotionOut
    neurotransmitter_profile: list[NeurotransmitterLinkOut]
    triggers: list[TriggerWordOut]
    channel_fits: list[EmotionChannelFitOut]
    funnel_strategies: list[FunnelStrategyOut]
    ctas: list[CTAOut]
    colors: list[ColorPsychologyOut]


class HealthOut(BaseModel):
    status: str
    db_path: str
    tables: dict[str, int]
