from datetime import datetime, date, time
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


# Assassin’s Apprentice (The Farseer Trilogy, Book 1) from Audible.fr
def test_farseer():
    audible = Audible("B0G5QKNT1J")

    assert audible.success is True
    audiobook = audible.audiobook
    assert audiobook.asin == "B0G5QKNT1J"
    assert isinstance(audiobook.fetched_at, datetime)
    assert isinstance(audiobook.url, str)
    assert audiobook.original_title == "Assassin’s Apprentice Book 1"
    assert audiobook.subtitle is None
    assert isinstance(audiobook.description, str)
    assert audiobook.copyright_ == "©1995 Robin Hobb (P)2026 HarperCollins Publishers"
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
    assert audiobook.format_ == "Version intégrale Livre audio"
    assert audiobook.book_format == "AudiobookFormat"
    assert audiobook.sku == "BK_HCUK_011245FR"
    assert audiobook.product_id == "B0G5QKNT1J"
    assert audiobook.rating == 0
    assert audiobook.price == 9.95
    assert audiobook.currency == "EUR"
    assert audiobook.genres == [
        "Action et aventure",
        "Animaux",
        "Dragons et créatures mythiques",
        "Fantasy",
        "Fiction",
        "Épique",
    ]
    assert audiobook.categories == ["Littérature, romans et fiction"]

    assert audiobook.title == "Assassin’s Apprentice Book 1"
    assert audiobook.series == "Farseer"
    assert audiobook.volume == 1.0

    assert audiobook.genres_all == [
        "Action et aventure",
        "Animaux",
        "Dragons et créatures mythiques",
        "Fantasy",
        "Fiction",
        "Littérature, romans et fiction",
        "Épique",
    ]
    assert audiobook.duration_human == "16:35:00"

    assert audiobook.genres_list == (
        "Action et aventure/Animaux/Dragons et créatures mythiques/"
        "Fantasy/Fiction/Littérature, romans et fiction/Épique"
    )
    assert audiobook.authors_list == "Robin Hobb"
    assert audiobook.narrators_list == "Joe Eyre"
    assert audiobook.year == 2026


# L'œil d'Otolep from Audible.fr
def test_otolep():
    audible = Audible("2367627002")

    assert audible.audiobook.title == "L'œil d'Otolep"
    assert audible.audiobook.subtitle == "Les mondes d'Ewilan 2"
    assert audible.audiobook.series == "Les mondes d'Ewilan"
    assert audible.audiobook.volume == 2.0


# La bataille des Jedi from Audible.fr
def test_jedi():
    audible = Audible("B0D7D39LP5")

    assert audible.audiobook.title == "La bataille des Jedi"
    assert audible.audiobook.series == "La croisade noire du jedi fou"
    assert audible.audiobook.volume == 2.0
    assert audible.audiobook.volume_int == 2
    assert audible.audiobook.authors == ["Timothy Zahn"]


# Assassin’s Apprentice (The Farseer Trilogy, Book 1) from Audible.com
def test_farseer_com():
    audible = Audible("B0G5SMXT5S")

    assert audible.fetch.json_duration.series_typed == "Farseer Trilogy"
    assert audible.fetch.json_duration.part_typed == 1
