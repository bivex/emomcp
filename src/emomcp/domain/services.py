"""Domain services — business logic that doesn't belong to a single entity."""

from __future__ import annotations

from .entities import (
    Emotion,
    Neurotransmitter,
    EmotionNeurotransmitterLink,
)


def classify_emotion_valence(emotion: Emotion, links: list[EmotionNeurotransmitterLink]) -> str:
    """Classify the neurochemical profile of an emotion based on its NT links."""
    excitatory = sum(1 for l in links if l.is_excitatory)
    deficit = sum(1 for l in links if l.is_deficit)
    if excitatory > deficit:
        return "predominantly_excitatory"
    if deficit > excitatory:
        return "predominantly_deficit"
    return "balanced"


def dominant_neurotransmitter(links: list[EmotionNeurotransmitterLink]) -> int | None:
    """Return the neurotransmitter ID with the highest absolute weight."""
    if not links:
        return None
    return max(links, key=lambda l: abs(l.weight)).neurotransmitter_id


def is_peptide_link(nt: Neurotransmitter) -> bool:
    """Check if a neurotransmitter is a peptide (large molecule)."""
    return nt.is_peptide
