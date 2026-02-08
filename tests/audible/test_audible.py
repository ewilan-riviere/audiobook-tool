from audiobook.audible import Audible, AudibleAudiobook

ASIN_LIST_FR = [
    "B0D7D39LP5",  # La bataille des Jedi
    "B0G5QKNT1J",  # Assassin’s Apprentice (The Farseer Trilogy, Book 1)
    "B0G71PC24C",  # La Conquête des Nébuleuses
    "B0BVGSJ9TD",  # One Foot in the Grave (Dramatized Adaptation)
    "B00BSX9XM4",  # Twice Tempted
    "B0FSDY3D2F",  # L'Épée de la Providence
    "2367627002",  # L'œil d'Otolep
    "2075136246",  # La mémoire de Babel
]
ASIN_LIST_UK = [
    "B0BVGSYL4Q",  # One Foot in the Grave
]


# def test_audible():
#     for asin in ASIN_LIST_FR:
#         Audible(asin)


# def test_audible_uk():
#     Audible("B0BVGSYL4Q", "co.uk")
#     Audible("B0BVGSYL4Q")


def test_audible_fr():
    asin = "B00945ME60"
    audible = Audible(asin, "fr")
    _test_halway_to_the_grave(audible.audiobook)
    audible = Audible(asin)
    _test_halway_to_the_grave(audible.audiobook)


def test_audible_co_uk():
    asin = "B004FTL55Q"
    audible = Audible(asin, "co.uk")
    _test_halway_to_the_grave(audible.audiobook)
    audible = Audible(asin)
    _test_halway_to_the_grave(audible.audiobook)


def test_audible_com():
    asin = "B003EYRWCS"
    audible = Audible(asin, "com")
    _test_halway_to_the_grave(audible.audiobook)
    audible = Audible(asin)
    _test_halway_to_the_grave(audible.audiobook)


def test_audible_de():
    asin = "B004V03H3W"
    audible = Audible(asin, "de")
    _test_halway_to_the_grave(audible.audiobook)
    audible = Audible(asin)
    _test_halway_to_the_grave(audible.audiobook)


def _test_halway_to_the_grave(audiobook: AudibleAudiobook):
    assert audiobook.title_clean == "Halfway to the Grave"
