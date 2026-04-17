"""Repository interfaces — domain ports that infrastructure must implement."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .entities import (
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


class EmotionRepository(ABC):
    @abstractmethod
    def get_by_id(self, emotion_id: int) -> Emotion | None: ...

    @abstractmethod
    def get_by_name(self, name: str) -> Emotion | None: ...

    @abstractmethod
    def list_all(
        self,
        valence: str | None = None,
        activation: str | None = None,
        is_micro: bool | None = None,
    ) -> list[Emotion]: ...

    @abstractmethod
    def search(self, query: str) -> list[Emotion]: ...


class NeurotransmitterRepository(ABC):
    @abstractmethod
    def get_by_id(self, nt_id: int) -> Neurotransmitter | None: ...

    @abstractmethod
    def get_by_name(self, name: str) -> Neurotransmitter | None: ...

    @abstractmethod
    def list_all(self) -> list[Neurotransmitter]: ...


class EmotionNeurotransmitterRepository(ABC):
    @abstractmethod
    def get_profile(self, emotion_id: int) -> list[EmotionNeurotransmitterLink]: ...

    @abstractmethod
    def get_emotions_for_nt(self, nt_id: int) -> list[EmotionNeurotransmitterLink]: ...


class NeurotransmitterSimilarityRepository(ABC):
    @abstractmethod
    def get_for_nt(self, nt_id: int) -> list[NeurotransmitterSimilarity]: ...

    @abstractmethod
    def get_pair(self, id_a: int, id_b: int) -> NeurotransmitterSimilarity | None: ...

    @abstractmethod
    def list_all(self) -> list[NeurotransmitterSimilarity]: ...


class NeurotransmitterPathwayRepository(ABC):
    @abstractmethod
    def get_for_nt(self, nt_id: int) -> list[NeurotransmitterPathway]: ...

    @abstractmethod
    def list_all(self) -> list[NeurotransmitterPathway]: ...


class FunnelStageRepository(ABC):
    @abstractmethod
    def get_by_id(self, stage_id: int) -> FunnelStage | None: ...

    @abstractmethod
    def get_by_code(self, code: str) -> FunnelStage | None: ...

    @abstractmethod
    def list_all(self) -> list[FunnelStage]: ...


class FunnelEmotionStrategyRepository(ABC):
    @abstractmethod
    def get_for_stage(self, stage_id: int) -> list[FunnelEmotionStrategy]: ...

    @abstractmethod
    def get_for_emotion(self, emotion_id: int) -> list[FunnelEmotionStrategy]: ...


class MarketingChannelRepository(ABC):
    @abstractmethod
    def get_by_id(self, channel_id: int) -> MarketingChannel | None: ...

    @abstractmethod
    def list_all(self, channel_type: str | None = None) -> list[MarketingChannel]: ...


class EmotionChannelFitRepository(ABC):
    @abstractmethod
    def get_for_emotion(self, emotion_id: int) -> list[EmotionChannelFit]: ...

    @abstractmethod
    def get_for_channel(self, channel_id: int) -> list[EmotionChannelFit]: ...


class TriggerWordRepository(ABC):
    @abstractmethod
    def get_for_emotion(self, emotion_id: int) -> list[TriggerWord]: ...

    @abstractmethod
    def get_for_emotion_and_category(self, emotion_id: int, category: str) -> list[TriggerWord]: ...


class ColorPsychologyRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[ColorPsychology]: ...

    @abstractmethod
    def get_for_stage(self, funnel_stage: str) -> list[ColorPsychology]: ...

    @abstractmethod
    def get_for_industry(self, industry: str) -> list[ColorPsychology]: ...


class CTAPatternRepository(ABC):
    @abstractmethod
    def get_for_stage(self, stage_id: int) -> list[CTAPattern]: ...

    @abstractmethod
    def get_for_emotion(self, emotion_id: int) -> list[CTAPattern]: ...


class BuyerArchetypeRepository(ABC):
    @abstractmethod
    def get_by_id(self, archetype_id: int) -> BuyerArchetype | None: ...

    @abstractmethod
    def get_by_nt(self, dominant_nt: str) -> BuyerArchetype | None: ...

    @abstractmethod
    def list_all(self) -> list[BuyerArchetype]: ...


class FunnelTemplateRepository(ABC):
    @abstractmethod
    def get_by_id(self, template_id: int) -> FunnelTemplate | None: ...

    @abstractmethod
    def get_by_code(self, code: str) -> FunnelTemplate | None: ...

    @abstractmethod
    def list_all(self, vertical: str | None = None) -> list[FunnelTemplate]: ...


class FunnelTemplateStepRepository(ABC):
    @abstractmethod
    def get_for_template(self, template_id: int) -> list[FunnelTemplateStep]: ...


class ObjectionHandlingRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[ObjectionHandling]: ...

    @abstractmethod
    def search(self, query: str) -> list[ObjectionHandling]: ...
