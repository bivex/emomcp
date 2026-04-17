"""Application use cases — orchestrate domain logic for each API operation."""

from __future__ import annotations

from .dto import (
    EmotionOut,
    EmotionDetailOut,
    NeurotransmitterOut,
    NeurotransmitterDetailOut,
    NeurotransmitterLinkOut,
    SimilarityOut,
    PathwayOut,
    FunnelStageOut,
    FunnelStrategyOut,
    FunnelTemplateOut,
    FunnelTemplateStepOut,
    FunnelTemplateDetailOut,
    ChannelOut,
    EmotionChannelFitOut,
    TriggerWordOut,
    ColorPsychologyOut,
    CTAOut,
    BuyerArchetypeOut,
    ObjectionOut,
    StageStrategyOut,
    EmotionMarketingProfileOut,
    HealthOut,
)
from ..domain.repositories import (
    EmotionRepository,
    NeurotransmitterRepository,
    EmotionNeurotransmitterRepository,
    NeurotransmitterSimilarityRepository,
    NeurotransmitterPathwayRepository,
    FunnelStageRepository,
    FunnelEmotionStrategyRepository,
    MarketingChannelRepository,
    EmotionChannelFitRepository,
    TriggerWordRepository,
    ColorPsychologyRepository,
    CTAPatternRepository,
    BuyerArchetypeRepository,
    FunnelTemplateRepository,
    FunnelTemplateStepRepository,
    ObjectionHandlingRepository,
)
from ..domain.entities import Emotion


def _emotion_to_dto(e: Emotion) -> EmotionOut:
    return EmotionOut(
        id=e.id, name_en=e.name_en, name_ru=e.name_ru,
        valence=e.valence, activation=e.activation,
        is_micro=e.is_micro, micro_marker=e.micro_marker,
    )


class EmotionUseCases:
    def __init__(
        self,
        emotions: EmotionRepository,
        nt_links: EmotionNeurotransmitterRepository,
        nts: NeurotransmitterRepository,
        triggers: TriggerWordRepository,
        funnel_strategies: FunnelEmotionStrategyRepository,
        channel_fits: EmotionChannelFitRepository,
        ctas: CTAPatternRepository,
        colors: ColorPsychologyRepository,
    ) -> None:
        self._emotions = emotions
        self._nt_links = nt_links
        self._nts = nts
        self._triggers = triggers
        self._funnel_strategies = funnel_strategies
        self._channel_fits = channel_fits
        self._ctas = ctas
        self._colors = colors

    def get(self, emotion_id: int) -> EmotionDetailOut | None:
        emotion = self._emotions.get_by_id(emotion_id)
        if not emotion:
            return None
        return self._build_detail(emotion)

    def get_by_name(self, name: str) -> EmotionDetailOut | None:
        emotion = self._emotions.get_by_name(name)
        if not emotion:
            return None
        return self._build_detail(emotion)

    def list_emotions(
        self,
        valence: str | None = None,
        activation: str | None = None,
        is_micro: bool | None = None,
    ) -> list[EmotionOut]:
        emotions = self._emotions.list_all(valence=valence, activation=activation, is_micro=is_micro)
        return [_emotion_to_dto(e) for e in emotions]

    def search(self, query: str) -> list[EmotionOut]:
        emotions = self._emotions.search(query)
        return [_emotion_to_dto(e) for e in emotions]

    def get_marketing_profile(self, emotion_id: int) -> EmotionMarketingProfileOut | None:
        emotion = self._emotions.get_by_id(emotion_id)
        if not emotion:
            return None
        return EmotionMarketingProfileOut(
            emotion=_emotion_to_dto(emotion),
            neurotransmitter_profile=self._build_nt_links(emotion.id),
            triggers=self._build_triggers(emotion.id),
            channel_fits=self._build_channel_fits(emotion.id),
            funnel_strategies=self._build_funnel_strategies(emotion.id),
            ctas=self._build_ctas(emotion_id=emotion.id),
            colors=[
                ColorPsychologyOut(color=c.color, hex_code=c.hex_code,
                                   primary_emotion_id=c.primary_emotion_id,
                                   arousal_level=c.arousal_level,
                                   funnel_stage=c.funnel_stage,
                                   industries_ru=c.industries_ru)
                for c in self._colors.list_all()
            ],
        )

    def _build_detail(self, emotion: Emotion) -> EmotionDetailOut:
        return EmotionDetailOut(
            id=emotion.id, name_en=emotion.name_en, name_ru=emotion.name_ru,
            valence=emotion.valence, activation=emotion.activation,
            is_micro=emotion.is_micro, micro_marker=emotion.micro_marker,
            neurotransmitter_profile=self._build_nt_links(emotion.id),
            trigger_words=self._build_triggers(emotion.id),
            funnel_strategies=self._build_funnel_strategies(emotion.id),
            channel_fits=self._build_channel_fits(emotion.id),
        )

    def _build_nt_links(self, emotion_id: int) -> list[NeurotransmitterLinkOut]:
        links = self._nt_links.get_profile(emotion_id)
        result = []
        for link in links:
            nt = self._nts.get_by_id(link.neurotransmitter_id)
            if nt:
                result.append(NeurotransmitterLinkOut(
                    neurotransmitter_id=nt.id,
                    neurotransmitter_name=nt.name,
                    weight=link.weight,
                    mechanism_ru=link.mechanism_ru,
                    is_excitatory=link.is_excitatory,
                ))
        return result

    def _build_triggers(self, emotion_id: int) -> list[TriggerWordOut]:
        return [
            TriggerWordOut(category=t.category, words_ru=t.words_ru,
                           words_en=t.words_en, power_score=t.power_score)
            for t in self._triggers.get_for_emotion(emotion_id)
        ]

    def _build_funnel_strategies(self, emotion_id: int) -> list[FunnelStrategyOut]:
        strategies = self._funnel_strategies.get_for_emotion(emotion_id)
        result = []
        for s in strategies:
            e = self._emotions.get_by_id(s.emotion_id)
            result.append(FunnelStrategyOut(
                emotion_id=s.emotion_id,
                emotion_name_ru=e.name_ru if e else "?",
                effectiveness=s.effectiveness,
                role_ru=s.role_ru,
            ))
        return result

    def _build_channel_fits(self, emotion_id: int) -> list[EmotionChannelFitOut]:
        fits = self._channel_fits.get_for_emotion(emotion_id)
        result = []
        for f in fits:
            result.append(EmotionChannelFitOut(
                channel_id=f.channel_id,
                channel_name_ru=f.ad_format_ru,
                fitness=f.fitness,
                ad_format_ru=f.ad_format_ru,
            ))
        return result

    def _build_ctas(self, emotion_id: int | None = None, stage_id: int | None = None) -> list[CTAOut]:
        if emotion_id:
            raw = self._ctas.get_for_emotion(emotion_id)
        elif stage_id:
            raw = self._ctas.get_for_stage(stage_id)
        else:
            raw = []
        return [
            CTAOut(
                id=c.id, funnel_stage_id=c.funnel_stage_id,
                emotion_id=c.emotion_id, cta_ru=c.cta_ru,
                cta_en=c.cta_en, urgency=c.urgency,
                conversion_lift=c.conversion_lift,
            )
            for c in raw
        ]


class NeurotransmitterUseCases:
    def __init__(
        self,
        nts: NeurotransmitterRepository,
        similarities: NeurotransmitterSimilarityRepository,
        pathways: NeurotransmitterPathwayRepository,
        nt_links: EmotionNeurotransmitterRepository,
        emotions: EmotionRepository,
    ) -> None:
        self._nts = nts
        self._similarities = similarities
        self._pathways = pathways
        self._nt_links = nt_links
        self._emotions = emotions

    def get(self, nt_id: int) -> NeurotransmitterDetailOut | None:
        nt = self._nts.get_by_id(nt_id)
        if not nt:
            return None
        return self._build_detail(nt)

    def get_by_name(self, name: str) -> NeurotransmitterDetailOut | None:
        nt = self._nts.get_by_name(name)
        if not nt:
            return None
        return self._build_detail(nt)

    def list_all(self) -> list[NeurotransmitterOut]:
        return [
            NeurotransmitterOut(
                id=n.id, name=n.name, name_ru=n.name_ru, smiles=n.smiles,
                molecular_formula=n.molecular_formula, molecular_weight=n.molecular_weight,
                logp=n.logp, tpsa=n.tpsa, h_bond_donors=n.h_bond_donors,
                h_bond_acceptors=n.h_bond_acceptors, rotatable_bonds=n.rotatable_bonds,
                aromatic_rings=n.aromatic_rings, fraction_csp3=n.fraction_csp3,
                pubchem_cid=n.pubchem_cid, inchikey=n.inchikey,
                role=n.role, role_ru=n.role_ru,
            )
            for n in self._nts.list_all()
        ]

    def get_similarities(self, nt_id: int) -> list[SimilarityOut]:
        sims = self._similarities.get_for_nt(nt_id)
        result = []
        for s in sims:
            partner_id = s.nt_id_2 if s.nt_id_1 == nt_id else s.nt_id_1
            partner = self._nts.get_by_id(partner_id)
            result.append(SimilarityOut(
                partner_id=partner_id,
                partner_name=partner.name if partner else "?",
                tanimoto=s.tanimoto,
                structural_relation=s.structural_relation,
            ))
        return result

    def _build_detail(self, nt: NeurotransmitterOut) -> NeurotransmitterDetailOut:
        links = self._nt_links.get_emotions_for_nt(nt.id)
        linked = []
        for link in links:
            e = self._emotions.get_by_id(link.emotion_id)
            if e:
                linked.append(NeurotransmitterLinkOut(
                    neurotransmitter_id=nt.id,
                    neurotransmitter_name=nt.name,
                    weight=link.weight,
                    mechanism_ru=link.mechanism_ru,
                    is_excitatory=link.is_excitatory,
                ))

        return NeurotransmitterDetailOut(
            id=nt.id, name=nt.name, name_ru=nt.name_ru, smiles=nt.smiles,
            molecular_formula=nt.molecular_formula, molecular_weight=nt.molecular_weight,
            logp=nt.logp, tpsa=nt.tpsa, h_bond_donors=nt.h_bond_donors,
            h_bond_acceptors=nt.h_bond_acceptors, rotatable_bonds=nt.rotatable_bonds,
            aromatic_rings=nt.aromatic_rings, fraction_csp3=nt.fraction_csp3,
            pubchem_cid=nt.pubchem_cid, inchikey=nt.inchikey,
            role=nt.role, role_ru=nt.role_ru,
            similarities=self.get_similarities(nt.id),
            pathways=[
                PathwayOut(from_nt_id=p.from_nt_id, to_nt_id=p.to_nt_id,
                           pathway_type=p.pathway_type, enzyme=p.enzyme,
                           description_ru=p.description_ru)
                for p in self._pathways.get_for_nt(nt.id)
            ],
            linked_emotions=linked,
        )


class FunnelUseCases:
    def __init__(
        self,
        stages: FunnelStageRepository,
        strategies: FunnelEmotionStrategyRepository,
        templates: FunnelTemplateRepository,
        template_steps: FunnelTemplateStepRepository,
        emotions: EmotionRepository,
        channels: MarketingChannelRepository,
        ctas: CTAPatternRepository,
        colors: ColorPsychologyRepository,
    ) -> None:
        self._stages = stages
        self._strategies = strategies
        self._templates = templates
        self._template_steps = template_steps
        self._emotions = emotions
        self._channels = channels
        self._ctas = ctas
        self._colors = colors

    def list_stages(self) -> list[FunnelStageOut]:
        return [
            FunnelStageOut(id=s.id, code=s.code, name=s.name, name_ru=s.name_ru,
                           stage_order=s.stage_order, goal_ru=s.goal_ru,
                           key_nt=s.key_nt, description_ru=s.description_ru)
            for s in self._stages.list_all()
        ]

    def get_stage_strategy(self, stage_code: str) -> StageStrategyOut | None:
        stage = self._stages.get_by_code(stage_code)
        if not stage:
            return None
        strats = self._strategies.get_for_stage(stage.id)
        strategy_dtos = []
        for s in strats:
            e = self._emotions.get_by_id(s.emotion_id)
            strategy_dtos.append(FunnelStrategyOut(
                emotion_id=s.emotion_id,
                emotion_name_ru=e.name_ru if e else "?",
                effectiveness=s.effectiveness,
                role_ru=s.role_ru,
            ))
        cta_dtos = [
            CTAOut(id=c.id, funnel_stage_id=c.funnel_stage_id, emotion_id=c.emotion_id,
                   cta_ru=c.cta_ru, cta_en=c.cta_en, urgency=c.urgency,
                   conversion_lift=c.conversion_lift)
            for c in self._ctas.get_for_stage(stage.id)
        ]
        color_dtos = [
            ColorPsychologyOut(color=c.color, hex_code=c.hex_code,
                               primary_emotion_id=c.primary_emotion_id,
                               arousal_level=c.arousal_level,
                               funnel_stage=c.funnel_stage,
                               industries_ru=c.industries_ru)
            for c in self._colors.get_for_stage(stage_code)
        ]
        return StageStrategyOut(
            stage=FunnelStageOut(id=stage.id, code=stage.code, name=stage.name,
                                 name_ru=stage.name_ru, stage_order=stage.stage_order,
                                 goal_ru=stage.goal_ru, key_nt=stage.key_nt,
                                 description_ru=stage.description_ru),
            strategies=strategy_dtos,
            ctas=cta_dtos,
            colors=color_dtos,
        )

    def list_templates(self, vertical: str | None = None) -> list[FunnelTemplateOut]:
        return [
            FunnelTemplateOut(id=t.id, code=t.code, name=t.name, name_ru=t.name_ru,
                              vertical=t.vertical, vertical_ru=t.vertical_ru,
                              description_ru=t.description_ru)
            for t in self._templates.list_all(vertical=vertical)
        ]

    def get_template(self, template_id: int) -> FunnelTemplateDetailOut | None:
        tpl = self._templates.get_by_id(template_id)
        if not tpl:
            return None
        steps = self._template_steps.get_for_template(tpl.id)
        step_dtos = []
        for s in steps:
            pe = self._emotions.get_by_id(s.primary_emotion_id)
            se = self._emotions.get_by_id(s.secondary_emotion_id) if s.secondary_emotion_id else None
            ch = self._channels.get_by_id(s.channel_id) if s.channel_id else None
            step_dtos.append(FunnelTemplateStepOut(
                step_order=s.step_order,
                stage_name_ru=self._stages.get_by_id(s.funnel_stage_id).name_ru if self._stages.get_by_id(s.funnel_stage_id) else "?",
                primary_emotion_name_ru=pe.name_ru if pe else "?",
                secondary_emotion_name_ru=se.name_ru if se else None,
                channel_name_ru=ch.name_ru if ch else None,
                expected_conv_rate=s.expected_conv_rate,
                ctas_ru=s.ctas_ru,
            ))
        return FunnelTemplateDetailOut(
            id=tpl.id, code=tpl.code, name=tpl.name, name_ru=tpl.name_ru,
            vertical=tpl.vertical, vertical_ru=tpl.vertical_ru,
            description_ru=tpl.description_ru,
            steps=step_dtos,
        )


class MarketingUseCases:
    def __init__(
        self,
        channels: MarketingChannelRepository,
        channel_fits: EmotionChannelFitRepository,
        triggers: TriggerWordRepository,
        colors: ColorPsychologyRepository,
        archetypes: BuyerArchetypeRepository,
        objections: ObjectionHandlingRepository,
        emotions: EmotionRepository,
    ) -> None:
        self._channels = channels
        self._channel_fits = channel_fits
        self._triggers = triggers
        self._colors = colors
        self._archetypes = archetypes
        self._objections = objections
        self._emotions = emotions

    def list_channels(self, channel_type: str | None = None) -> list[ChannelOut]:
        return [
            ChannelOut(id=c.id, code=c.code, name=c.name, name_ru=c.name_ru,
                       channel_type=c.channel_type, avg_cpc_usd=c.avg_cpc_usd,
                       best_funnel_stage=c.best_funnel_stage,
                       attention_span_sec=c.attention_span_sec,
                       description_ru=c.description_ru)
            for c in self._channels.list_all(channel_type=channel_type)
        ]

    def list_archetypes(self) -> list[BuyerArchetypeOut]:
        return [
            BuyerArchetypeOut(id=a.id, code=a.code, name=a.name, name_ru=a.name_ru,
                              dominant_nt=a.dominant_nt, decision_style_ru=a.decision_style_ru,
                              price_sensitivity=a.price_sensitivity, risk_tolerance=a.risk_tolerance,
                              social_proof_weight=a.social_proof_weight,
                              urgency_response=a.urgency_response,
                              description_ru=a.description_ru)
            for a in self._archetypes.list_all()
        ]

    def get_archetype_by_nt(self, nt: str) -> BuyerArchetypeOut | None:
        a = self._archetypes.get_by_nt(nt)
        if not a:
            return None
        return BuyerArchetypeOut(id=a.id, code=a.code, name=a.name, name_ru=a.name_ru,
                                 dominant_nt=a.dominant_nt, decision_style_ru=a.decision_style_ru,
                                 price_sensitivity=a.price_sensitivity, risk_tolerance=a.risk_tolerance,
                                 social_proof_weight=a.social_proof_weight,
                                 urgency_response=a.urgency_response,
                                 description_ru=a.description_ru)

    def list_objections(self, query: str | None = None) -> list[ObjectionOut]:
        raw = self._objections.search(query) if query else self._objections.list_all()
        result = []
        for o in raw:
            e = self._emotions.get_by_id(o.counter_emotion_id)
            result.append(ObjectionOut(
                id=o.id, objection=o.objection, objection_ru=o.objection_ru,
                counter_emotion_id=o.counter_emotion_id,
                counter_emotion_name_ru=e.name_ru if e else "?",
                trigger_nt=o.trigger_nt, copy_angle_ru=o.copy_angle_ru,
            ))
        return result

    def list_colors(self, stage: str | None = None, industry: str | None = None) -> list[ColorPsychologyOut]:
        if stage:
            raw = self._colors.get_for_stage(stage)
        elif industry:
            raw = self._colors.get_for_industry(industry)
        else:
            raw = self._colors.list_all()
        return [
            ColorPsychologyOut(color=c.color, hex_code=c.hex_code,
                               primary_emotion_id=c.primary_emotion_id,
                               arousal_level=c.arousal_level,
                               funnel_stage=c.funnel_stage,
                               industries_ru=c.industries_ru)
            for c in raw
        ]


class HealthUseCases:
    def __init__(self, db_path: str, conn) -> None:
        self._db_path = db_path
        self._conn = conn

    def check(self) -> HealthOut:
        tables: dict[str, int] = {}
        try:
            cursor = self._conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            for (name,) in cursor.fetchall():
                count = self._conn.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
                tables[name] = count
        except Exception:
            pass
        return HealthOut(status="ok", db_path=self._db_path, tables=tables)
