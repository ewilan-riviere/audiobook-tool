from audiobook.audible import Audible, AudibleAudiobook


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
