"""SQLite infrastructure adapters — concrete implementations of domain repository ports."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from ..domain.entities import (
    Emotion,
    Neurotransmitter,
    EmotionNeurotransmitterLink,
    NeurotransmitterSimilarity,
    NeurotransmitterPathway,
    FunnelStage,
    FunnelEmotionStrategy,
    MarketingChannel,
    EmotionChannelFit,
    TriggerWord,
    ColorPsychology,
    CTAPattern,
    BuyerArchetype,
    FunnelTemplate,
    FunnelTemplateStep,
    ObjectionHandling,
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


class DatabaseConnection:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None

    @property
    def raw_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    @contextmanager
    def cursor(self) -> Iterator[sqlite3.Cursor]:
        cur = self.raw_connection.cursor()
        try:
            yield cur
        finally:
            cur.close()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None


# ─── Emotion ───

class SqliteEmotionRepository(EmotionRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_by_id(self, emotion_id: int) -> Emotion | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM emotions WHERE id=?", (emotion_id,))
            row = cur.fetchone()
        return self._to_entity(row) if row else None

    def get_by_name(self, name: str) -> Emotion | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM emotions WHERE name_en LIKE ? OR name_ru LIKE ?",
                        (name, name))
            row = cur.fetchone()
        return self._to_entity(row) if row else None

    def list_all(self, valence: str | None = None, activation: str | None = None,
                 is_micro: bool | None = None) -> list[Emotion]:
        clauses: list[str] = []
        params: list = []
        if valence:
            clauses.append("valence=?")
            params.append(valence)
        if activation:
            clauses.append("activation=?")
            params.append(activation)
        if is_micro is not None:
            clauses.append("is_micro=?")
            params.append(int(is_micro))
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._db.cursor() as cur:
            cur.execute(f"SELECT * FROM emotions{where} ORDER BY id", params)
            return [self._to_entity(r) for r in cur.fetchall()]

    def search(self, query: str) -> list[Emotion]:
        q_lower = query.lower()
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM emotions")
            return [self._to_entity(r) for r in cur.fetchall()
                    if q_lower in r["name_en"].lower() or q_lower in r["name_ru"].lower()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> Emotion:
        return Emotion(
            id=r["id"], name_en=r["name_en"], name_ru=r["name_ru"],
            valence=r["valence"], activation=r["activation"],
            is_micro=bool(r["is_micro"]),
            micro_marker=r["micro_marker"] if "micro_marker" in r.keys() else None,
        )


# ─── Neurotransmitter ───

class SqliteNeurotransmitterRepository(NeurotransmitterRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_by_id(self, nt_id: int) -> Neurotransmitter | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM neurotransmitters WHERE id=?", (nt_id,))
            row = cur.fetchone()
        return self._to_entity(row) if row else None

    def get_by_name(self, name: str) -> Neurotransmitter | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM neurotransmitters WHERE name=? COLLATE NOCASE", (name,))
            row = cur.fetchone()
        return self._to_entity(row) if row else None

    def list_all(self) -> list[Neurotransmitter]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM neurotransmitters ORDER BY id")
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> Neurotransmitter:
        return Neurotransmitter(
            id=r["id"], name=r["name"], name_ru=r["name_ru"], smiles=r["smiles"],
            canonical_smiles=r["canonical_smiles"],
            murcko_scaffold=r["murcko_scaffold"],
            generic_scaffold=r["generic_scaffold"],
            molecular_formula=r["molecular_formula"], molecular_weight=r["molecular_weight"],
            logp=r["logp"], tpsa=r["tpsa"], h_bond_donors=r["h_bond_donors"],
            h_bond_acceptors=r["h_bond_acceptors"], rotatable_bonds=r["rotatable_bonds"],
            aromatic_rings=r["aromatic_rings"], fraction_csp3=r["fraction_csp3"],
            pubchem_cid=r["pubchem_cid"], inchikey=r["inchikey"],
            role=r["role"], role_ru=r["role_ru"],
        )


# ─── Emotion ↔ Neurotransmitter ───

class SqliteEmotionNeurotransmitterRepository(EmotionNeurotransmitterRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_profile(self, emotion_id: int) -> list[EmotionNeurotransmitterLink]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM emotion_neurotransmitter WHERE emotion_id=? ORDER BY ABS(weight) DESC", (emotion_id,))
            return [self._to_entity(r) for r in cur.fetchall()]

    def get_emotions_for_nt(self, nt_id: int) -> list[EmotionNeurotransmitterLink]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM emotion_neurotransmitter WHERE neurotransmitter_id=? ORDER BY ABS(weight) DESC", (nt_id,))
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> EmotionNeurotransmitterLink:
        return EmotionNeurotransmitterLink(
            emotion_id=r["emotion_id"], neurotransmitter_id=r["neurotransmitter_id"],
            weight=r["weight"], mechanism=r["mechanism"], mechanism_ru=r["mechanism_ru"],
        )


# ─── Similarity ───

class SqliteNeurotransmitterSimilarityRepository(NeurotransmitterSimilarityRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_for_nt(self, nt_id: int) -> list[NeurotransmitterSimilarity]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM neurotransmitter_similarity WHERE nt_id_1=? OR nt_id_2=? ORDER BY tanimoto DESC", (nt_id, nt_id))
            return [self._to_entity(r) for r in cur.fetchall()]

    def get_pair(self, id_a: int, id_b: int) -> NeurotransmitterSimilarity | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM neurotransmitter_similarity WHERE (nt_id_1=? AND nt_id_2=?) OR (nt_id_1=? AND nt_id_2=?)", (id_a, id_b, id_b, id_a))
            row = cur.fetchone()
        return self._to_entity(row) if row else None

    def list_all(self) -> list[NeurotransmitterSimilarity]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM neurotransmitter_similarity ORDER BY tanimoto DESC")
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> NeurotransmitterSimilarity:
        return NeurotransmitterSimilarity(
            nt_id_1=r["nt_id_1"], nt_id_2=r["nt_id_2"], tanimoto=r["tanimoto"],
            tanimoto_r3=r["tanimoto_r3"] if "tanimoto_r3" in r.keys() else None,
            structural_relation=r["structural_relation"],
        )


# ─── Pathway ───

class SqliteNeurotransmitterPathwayRepository(NeurotransmitterPathwayRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_for_nt(self, nt_id: int) -> list[NeurotransmitterPathway]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM neurotransmitter_pathway WHERE from_nt_id=? OR to_nt_id=?", (nt_id, nt_id))
            return [self._to_entity(r) for r in cur.fetchall()]

    def list_all(self) -> list[NeurotransmitterPathway]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM neurotransmitter_pathway ORDER BY id")
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> NeurotransmitterPathway:
        return NeurotransmitterPathway(
            from_nt_id=r["from_nt_id"], to_nt_id=r["to_nt_id"],
            pathway_type=r["pathway_type"], enzyme=r["enzyme"],
            description_ru=r["description_ru"],
        )


# ─── Funnel Stage ───

class SqliteFunnelStageRepository(FunnelStageRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_by_id(self, stage_id: int) -> FunnelStage | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM funnel_stages WHERE id=?", (stage_id,))
            row = cur.fetchone()
        return self._to_entity(row) if row else None

    def get_by_code(self, code: str) -> FunnelStage | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM funnel_stages WHERE code=?", (code,))
            row = cur.fetchone()
        return self._to_entity(row) if row else None

    def list_all(self) -> list[FunnelStage]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM funnel_stages ORDER BY stage_order")
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> FunnelStage:
        return FunnelStage(
            id=r["id"], code=r["code"], name=r["name"], name_ru=r["name_ru"],
            stage_order=r["stage_order"], goal=r["goal"], goal_ru=r["goal_ru"],
            key_nt=r["key_nt"], description_ru=r["description_ru"],
        )


# ─── Funnel Emotion Strategy ───

class SqliteFunnelEmotionStrategyRepository(FunnelEmotionStrategyRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_for_stage(self, stage_id: int) -> list[FunnelEmotionStrategy]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM funnel_emotion_strategy WHERE funnel_stage_id=? ORDER BY effectiveness DESC", (stage_id,))
            return [self._to_entity(r) for r in cur.fetchall()]

    def get_for_emotion(self, emotion_id: int) -> list[FunnelEmotionStrategy]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM funnel_emotion_strategy WHERE emotion_id=? ORDER BY effectiveness DESC", (emotion_id,))
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> FunnelEmotionStrategy:
        return FunnelEmotionStrategy(
            funnel_stage_id=r["funnel_stage_id"], emotion_id=r["emotion_id"],
            effectiveness=r["effectiveness"], role=r["role"], role_ru=r["role_ru"],
        )


# ─── Marketing Channel ───

class SqliteMarketingChannelRepository(MarketingChannelRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_by_id(self, channel_id: int) -> MarketingChannel | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM marketing_channels WHERE id=?", (channel_id,))
            row = cur.fetchone()
        return self._to_entity(row) if row else None

    def list_all(self, channel_type: str | None = None) -> list[MarketingChannel]:
        if channel_type:
            with self._db.cursor() as cur:
                cur.execute("SELECT * FROM marketing_channels WHERE channel_type=? ORDER BY id", (channel_type,))
                return [self._to_entity(r) for r in cur.fetchall()]
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM marketing_channels ORDER BY id")
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> MarketingChannel:
        return MarketingChannel(
            id=r["id"], code=r["code"], name=r["name"], name_ru=r["name_ru"],
            channel_type=r["channel_type"], avg_cpc_usd=r["avg_cpc_usd"],
            best_funnel_stage=r["best_funnel_stage"],
            attention_span_sec=r["attention_span_sec"],
            description_ru=r["description_ru"],
        )


# ─── Emotion Channel Fit ───

class SqliteEmotionChannelFitRepository(EmotionChannelFitRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_for_emotion(self, emotion_id: int) -> list[EmotionChannelFit]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM emotion_channel_fit WHERE emotion_id=? ORDER BY fitness DESC", (emotion_id,))
            return [self._to_entity(r) for r in cur.fetchall()]

    def get_for_channel(self, channel_id: int) -> list[EmotionChannelFit]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM emotion_channel_fit WHERE channel_id=? ORDER BY fitness DESC", (channel_id,))
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> EmotionChannelFit:
        return EmotionChannelFit(
            emotion_id=r["emotion_id"], channel_id=r["channel_id"],
            fitness=r["fitness"], ad_format=r["ad_format"],
            ad_format_ru=r["ad_format_ru"],
        )


# ─── Trigger Words ───

class SqliteTriggerWordRepository(TriggerWordRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_for_emotion(self, emotion_id: int) -> list[TriggerWord]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM trigger_words WHERE emotion_id=? ORDER BY power_score DESC", (emotion_id,))
            return [self._to_entity(r) for r in cur.fetchall()]

    def get_for_emotion_and_category(self, emotion_id: int, category: str) -> list[TriggerWord]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM trigger_words WHERE emotion_id=? AND category=?", (emotion_id, category))
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> TriggerWord:
        return TriggerWord(
            id=r["id"], emotion_id=r["emotion_id"], category=r["category"],
            words_ru=r["words_ru"], words_en=r["words_en"], power_score=r["power_score"],
        )


# ─── Color Psychology ───

class SqliteColorPsychologyRepository(ColorPsychologyRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def list_all(self) -> list[ColorPsychology]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM color_psychology ORDER BY id")
            return [self._to_entity(r) for r in cur.fetchall()]

    def get_for_stage(self, funnel_stage: str) -> list[ColorPsychology]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM color_psychology WHERE funnel_stage=?", (funnel_stage,))
            return [self._to_entity(r) for r in cur.fetchall()]

    def get_for_industry(self, industry: str) -> list[ColorPsychology]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM color_psychology WHERE industries_ru LIKE ? OR industries LIKE ?",
                        (f"%{industry}%", f"%{industry}%"))
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> ColorPsychology:
        return ColorPsychology(
            id=r["id"], color=r["color"], hex_code=r["hex_code"],
            primary_emotion_id=r["primary_emotion_id"],
            secondary_emotion_id=r["secondary_emotion_id"],
            arousal_level=r["arousal_level"], funnel_stage=r["funnel_stage"],
            industries=r["industries"], industries_ru=r["industries_ru"],
        )


# ─── CTA Patterns ───

class SqliteCTAPatternRepository(CTAPatternRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_for_stage(self, stage_id: int) -> list[CTAPattern]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM cta_patterns WHERE funnel_stage_id=? ORDER BY conversion_lift DESC", (stage_id,))
            return [self._to_entity(r) for r in cur.fetchall()]

    def get_for_emotion(self, emotion_id: int) -> list[CTAPattern]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM cta_patterns WHERE emotion_id=? ORDER BY conversion_lift DESC", (emotion_id,))
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> CTAPattern:
        return CTAPattern(
            id=r["id"], funnel_stage_id=r["funnel_stage_id"],
            emotion_id=r["emotion_id"], cta_ru=r["cta_ru"], cta_en=r["cta_en"],
            urgency=r["urgency"], conversion_lift=r["conversion_lift"],
        )


# ─── Buyer Archetype ───

class SqliteBuyerArchetypeRepository(BuyerArchetypeRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_by_id(self, archetype_id: int) -> BuyerArchetype | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM buyer_archetypes WHERE id=?", (archetype_id,))
            row = cur.fetchone()
        return self._to_entity(row) if row else None

    def get_by_nt(self, dominant_nt: str) -> BuyerArchetype | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM buyer_archetypes WHERE dominant_nt=? COLLATE NOCASE", (dominant_nt,))
            row = cur.fetchone()
        return self._to_entity(row) if row else None

    def list_all(self) -> list[BuyerArchetype]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM buyer_archetypes ORDER BY urgency_response DESC")
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> BuyerArchetype:
        return BuyerArchetype(
            id=r["id"], code=r["code"], name=r["name"], name_ru=r["name_ru"],
            dominant_nt=r["dominant_nt"], decision_style=r["decision_style"],
            decision_style_ru=r["decision_style_ru"],
            price_sensitivity=r["price_sensitivity"], risk_tolerance=r["risk_tolerance"],
            social_proof_weight=r["social_proof_weight"], urgency_response=r["urgency_response"],
            description_ru=r["description_ru"],
        )


# ─── Funnel Template ───

class SqliteFunnelTemplateRepository(FunnelTemplateRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_by_id(self, template_id: int) -> FunnelTemplate | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM funnel_templates WHERE id=?", (template_id,))
            row = cur.fetchone()
        return self._to_entity(row) if row else None

    def get_by_code(self, code: str) -> FunnelTemplate | None:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM funnel_templates WHERE code=?", (code,))
            row = cur.fetchone()
        return self._to_entity(row) if row else None

    def list_all(self, vertical: str | None = None) -> list[FunnelTemplate]:
        if vertical:
            with self._db.cursor() as cur:
                cur.execute("SELECT * FROM funnel_templates WHERE vertical=? OR vertical_ru LIKE ?",
                            (vertical, f"%{vertical}%"))
                return [self._to_entity(r) for r in cur.fetchall()]
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM funnel_templates ORDER BY id")
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> FunnelTemplate:
        return FunnelTemplate(
            id=r["id"], code=r["code"], name=r["name"], name_ru=r["name_ru"],
            vertical=r["vertical"], vertical_ru=r["vertical_ru"],
            description_ru=r["description_ru"],
        )


# ─── Funnel Template Steps ───

class SqliteFunnelTemplateStepRepository(FunnelTemplateStepRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def get_for_template(self, template_id: int) -> list[FunnelTemplateStep]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM funnel_template_steps WHERE template_id=? ORDER BY step_order", (template_id,))
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> FunnelTemplateStep:
        return FunnelTemplateStep(
            id=r["id"], template_id=r["template_id"], step_order=r["step_order"],
            funnel_stage_id=r["funnel_stage_id"], primary_emotion_id=r["primary_emotion_id"],
            secondary_emotion_id=r["secondary_emotion_id"] if "secondary_emotion_id" in r.keys() else None,
            channel_id=r["channel_id"] if "channel_id" in r.keys() else None,
            expected_conv_rate=r["expected_conv_rate"],
            ctas_ru=r["ctas_ru"],
        )


# ─── Objection Handling ───

class SqliteObjectionHandlingRepository(ObjectionHandlingRepository):
    def __init__(self, db: DatabaseConnection) -> None:
        self._db = db

    def list_all(self) -> list[ObjectionHandling]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM objection_handling ORDER BY id")
            return [self._to_entity(r) for r in cur.fetchall()]

    def search(self, query: str) -> list[ObjectionHandling]:
        with self._db.cursor() as cur:
            cur.execute("SELECT * FROM objection_handling WHERE objection_ru LIKE ? OR objection LIKE ?",
                        (f"%{query}%", f"%{query}%"))
            return [self._to_entity(r) for r in cur.fetchall()]

    @staticmethod
    def _to_entity(r: sqlite3.Row) -> ObjectionHandling:
        return ObjectionHandling(
            id=r["id"], objection=r["objection"], objection_ru=r["objection_ru"],
            counter_emotion_id=r["counter_emotion_id"], trigger_nt=r["trigger_nt"],
            copy_angle_ru=r["copy_angle_ru"],
        )
