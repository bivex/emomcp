"""Domain entities — the core business objects of the emotions system."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Emotion:
    id: int
    name_en: str
    name_ru: str
    valence: str
    activation: str
    is_micro: bool = False
    micro_marker: str | None = None

    @property
    def is_positive(self) -> bool:
        return self.valence == "positive"

    @property
    def is_high_energy(self) -> bool:
        return self.activation in ("high",)


@dataclass(frozen=True, slots=True)
class Neurotransmitter:
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

    @property
    def is_peptide(self) -> bool:
        return self.molecular_weight > 500

    @property
    def is_small_molecule(self) -> bool:
        return self.molecular_weight < 300


@dataclass(frozen=True, slots=True)
class EmotionNeurotransmitterLink:
    emotion_id: int
    neurotransmitter_id: int
    weight: float
    mechanism: str
    mechanism_ru: str

    @property
    def is_excitatory(self) -> bool:
        return self.weight > 0

    @property
    def is_deficit(self) -> bool:
        return self.weight < 0


@dataclass(frozen=True, slots=True)
class NeurotransmitterSimilarity:
    nt_id_1: int
    nt_id_2: int
    tanimoto: float
    tanimoto_r3: float | None
    structural_relation: str

    @property
    def is_high_similarity(self) -> bool:
        return self.tanimoto >= 0.5


@dataclass(frozen=True, slots=True)
class NeurotransmitterPathway:
    from_nt_id: int
    to_nt_id: int
    pathway_type: str
    enzyme: str
    description_ru: str


@dataclass(frozen=True, slots=True)
class FunnelStage:
    id: int
    code: str
    name: str
    name_ru: str
    stage_order: int
    goal: str
    goal_ru: str
    key_nt: str
    description_ru: str


@dataclass(frozen=True, slots=True)
class FunnelEmotionStrategy:
    funnel_stage_id: int
    emotion_id: int
    effectiveness: float
    role: str
    role_ru: str


@dataclass(frozen=True, slots=True)
class MarketingChannel:
    id: int
    code: str
    name: str
    name_ru: str
    channel_type: str
    avg_cpc_usd: float | None
    best_funnel_stage: str
    attention_span_sec: int | None
    description_ru: str


@dataclass(frozen=True, slots=True)
class EmotionChannelFit:
    emotion_id: int
    channel_id: int
    fitness: float
    ad_format: str
    ad_format_ru: str


@dataclass(frozen=True, slots=True)
class TriggerWord:
    id: int
    emotion_id: int
    category: str
    words_ru: str
    words_en: str
    power_score: float


@dataclass(frozen=True, slots=True)
class ColorPsychology:
    id: int
    color: str
    hex_code: str
    primary_emotion_id: int
    secondary_emotion_id: int | None
    arousal_level: str
    funnel_stage: str
    industries: str
    industries_ru: str


@dataclass(frozen=True, slots=True)
class CTAPattern:
    id: int
    funnel_stage_id: int
    emotion_id: int
    cta_ru: str
    cta_en: str
    urgency: str
    conversion_lift: float


@dataclass(frozen=True, slots=True)
class BuyerArchetype:
    id: int
    code: str
    name: str
    name_ru: str
    dominant_nt: str
    decision_style: str
    decision_style_ru: str
    price_sensitivity: float
    risk_tolerance: float
    social_proof_weight: float
    urgency_response: float
    description_ru: str


@dataclass(frozen=True, slots=True)
class FunnelTemplate:
    id: int
    code: str
    name: str
    name_ru: str
    vertical: str
    vertical_ru: str
    description_ru: str


@dataclass(frozen=True, slots=True)
class FunnelTemplateStep:
    id: int
    template_id: int
    step_order: int
    funnel_stage_id: int
    primary_emotion_id: int
    secondary_emotion_id: int | None
    channel_id: int | None
    expected_conv_rate: float
    ctas_ru: str


@dataclass(frozen=True, slots=True)
class ObjectionHandling:
    id: int
    objection: str
    objection_ru: str
    counter_emotion_id: int
    trigger_nt: str
    copy_angle_ru: str
