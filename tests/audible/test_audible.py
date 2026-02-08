from audiobook.audible import Audible

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


def test_audible():
    for asin in ASIN_LIST_FR:
        Audible(asin)
