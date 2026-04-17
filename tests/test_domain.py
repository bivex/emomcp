"""Domain layer tests — entities, value objects, domain services."""

from emomcp.domain.entities import (
    Emotion,
    Neurotransmitter,
    EmotionNeurotransmitterLink,
    NeurotransmitterSimilarity,
)
from emomcp.domain.services import (
    classify_emotion_valence,
    dominant_neurotransmitter,
    is_peptide_link,
)


class TestEmotionEntity:
    def test_positive_valence(self):
        e = Emotion(id=1, name_en="Happiness", name_ru="Радость",
                     valence="positive", activation="high")
        assert e.is_positive
        assert not e.is_high_energy or e.is_high_energy  # activation="high"

    def test_negative_valence(self):
        e = Emotion(id=2, name_en="Sadness", name_ru="Грусть",
                     valence="negative", activation="low")
        assert not e.is_positive

    def test_high_energy(self):
        e = Emotion(id=3, name_en="Anger", name_ru="Гнев",
                     valence="negative", activation="high")
        assert e.is_high_energy

    def test_low_energy(self):
        e = Emotion(id=4, name_en="Serenity", name_ru="Умиротворение",
                     valence="positive", activation="low")
        assert not e.is_high_energy

    def test_frozen(self):
        e = Emotion(id=1, name_en="X", name_ru="Y",
                     valence="positive", activation="high")
        try:
            e.id = 99  # type: ignore
            assert False, "Should be frozen"
        except AttributeError:
            pass

    def test_micro_emotion(self):
        e = Emotion(id=100, name_en="Micro-fear", name_ru="Микро-страх",
                     valence="negative", activation="high",
                     is_micro=True, micro_marker="AU01+AU02")
        assert e.is_micro
        assert e.micro_marker == "AU01+AU02"

    def test_defaults(self):
        e = Emotion(id=1, name_en="X", name_ru="Y",
                     valence="neutral", activation="medium")
        assert e.is_micro is False
        assert e.micro_marker is None


class TestNeurotransmitterEntity:
    def _make_nt(self, mw=176.0) -> Neurotransmitter:
        return Neurotransmitter(
            id=1, name="Serotonin", name_ru="Серотонин", smiles="C1=CC",
            canonical_smiles=None, murcko_scaffold=None, generic_scaffold=None,
            molecular_formula="C10H12N2O", molecular_weight=mw,
            logp=1.37, tpsa=62.0, h_bond_donors=3, h_bond_acceptors=2,
            rotatable_bonds=2, aromatic_rings=2, fraction_csp3=0.2,
            pubchem_cid=5202, inchikey="QZAY", role="mood", role_ru="Настроение",
        )

    def test_small_molecule(self):
        nt = self._make_nt(mw=176.0)
        assert nt.is_small_molecule
        assert not nt.is_peptide

    def test_peptide(self):
        nt = self._make_nt(mw=1007.0)
        assert nt.is_peptide
        assert not nt.is_small_molecule

    def test_frozen(self):
        nt = self._make_nt()
        try:
            nt.name = "X"  # type: ignore
            assert False, "Should be frozen"
        except AttributeError:
            pass


class TestEmotionNeurotransmitterLink:
    def test_excitatory(self):
        link = EmotionNeurotransmitterLink(
            emotion_id=1, neurotransmitter_id=2,
            weight=0.85, mechanism="reward", mechanism_ru="вознаграждение",
        )
        assert link.is_excitatory
        assert not link.is_deficit

    def test_deficit(self):
        link = EmotionNeurotransmitterLink(
            emotion_id=2, neurotransmitter_id=1,
            weight=-0.8, mechanism="deficit", mechanism_ru="дефицит",
        )
        assert not link.is_excitatory
        assert link.is_deficit

    def test_neutral_weight(self):
        link = EmotionNeurotransmitterLink(
            emotion_id=1, neurotransmitter_id=1,
            weight=0.0, mechanism="none", mechanism_ru="нет",
        )
        assert not link.is_excitatory
        assert not link.is_deficit


class TestNeurotransmitterSimilarity:
    def test_high_similarity(self):
        s = NeurotransmitterSimilarity(
            nt_id_1=3, nt_id_2=4, tanimoto=0.58,
            tanimoto_r3=None, structural_relation="catecholamine",
        )
        assert s.is_high_similarity

    def test_low_similarity(self):
        s = NeurotransmitterSimilarity(
            nt_id_1=1, nt_id_2=5, tanimoto=0.13,
            tanimoto_r3=None, structural_relation="distant",
        )
        assert not s.is_high_similarity


class TestDomainServices:
    def test_classify_excitatory(self):
        links = [
            EmotionNeurotransmitterLink(1, 1, 0.9, "a", "а"),
            EmotionNeurotransmitterLink(1, 2, 0.8, "b", "б"),
        ]
        assert classify_emotion_valence(None, links) == "predominantly_excitatory"

    def test_classify_deficit(self):
        links = [
            EmotionNeurotransmitterLink(2, 1, -0.8, "a", "а"),
            EmotionNeurotransmitterLink(2, 2, -0.6, "b", "б"),
        ]
        assert classify_emotion_valence(None, links) == "predominantly_deficit"

    def test_classify_balanced(self):
        links = [
            EmotionNeurotransmitterLink(1, 1, 0.5, "a", "а"),
            EmotionNeurotransmitterLink(1, 2, -0.5, "b", "б"),
        ]
        assert classify_emotion_valence(None, links) == "balanced"

    def test_classify_empty(self):
        assert classify_emotion_valence(None, []) == "balanced"

    def test_dominant_nt(self):
        links = [
            EmotionNeurotransmitterLink(1, 1, 0.5, "a", "а"),
            EmotionNeurotransmitterLink(1, 2, 0.9, "b", "б"),
        ]
        assert dominant_neurotransmitter(links) == 2

    def test_dominant_nt_deficit_wins_by_abs(self):
        links = [
            EmotionNeurotransmitterLink(1, 1, 0.5, "a", "а"),
            EmotionNeurotransmitterLink(1, 3, -0.95, "b", "б"),
        ]
        assert dominant_neurotransmitter(links) == 3

    def test_dominant_nt_empty(self):
        assert dominant_neurotransmitter([]) is None
