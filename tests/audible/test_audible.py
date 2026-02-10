from datetime import datetime, date, time
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


def test_audible():
    audible = Audible("B0G5QKNT1J")

    assert audible.success is True
    audiobook = audible.audiobook
    assert audiobook.asin == "B0G5QKNT1J"
    assert isinstance(audiobook.fetched_at, datetime)
    assert isinstance(audiobook.url, str)
    assert (
        audiobook.original_title
        == "Assassin’s Apprentice (The Farseer Trilogy, Book 1)"
    )
    assert audiobook.subtitle is None
    assert isinstance(audiobook.description, str)
    assert audiobook.copyright == "©1995 Robin Hobb (P)2026 HarperCollins Publishers"
    assert audiobook.publisher == "HarperVoyager"
    assert audiobook.authors == ["Robin Hobb"]
    assert audiobook.narrators == ["Joe Eyre"]
    assert audiobook.published_at == date(2026, 1, 29)
    assert audiobook.duration == time(16, 35)
    assert audiobook.language == "English"
    assert audiobook.abridged is False
    assert isinstance(audiobook.cover, str)
    assert audiobook.original_series == ["Farseer Trilogy"]
    assert audiobook.part is None
    assert audiobook.volume == 1.0
    assert audiobook.format == "Version intégrale Livre audio"
    assert audiobook.book_format == "AudiobookFormat"
    assert audiobook.sku == "BK_HCUK_011245FR"
    assert audiobook.rating is None
    assert audiobook.price == 9.95
    assert audiobook.genres == [
        "Action et aventure",
        "Animaux",
        "Dragons et créatures mythiques",
        "Fantasy",
        "Fiction",
    ]
    assert audiobook.categories == ["Littérature, romans et fiction"]

    assert audiobook.title == "Assassin’s Apprentice"
    assert audiobook.series == "Farseer"
    assert audiobook.volume == 1.0

    assert audiobook.genres_all == [
        "Action et aventure",
        "Animaux",
        "Dragons et créatures mythiques",
        "Fantasy",
        "Fiction",
        "Littérature, romans et fiction",
    ]
    assert audiobook.duration_human == "16:35:00"

    assert (
        audiobook.genres_list
        == "Action et aventure/Animaux/Dragons et créatures mythiques/Fantasy/Fiction/Littérature, romans et fiction"
    )
    assert audiobook.authors_list == "Robin Hobb"
    assert audiobook.narrators_list == "Joe Eyre"
    assert audiobook.year == 2026


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
    assert audiobook.title == "Halfway to the Grave"
