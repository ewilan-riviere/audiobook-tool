import random
from audiobook.audible import Audible


# Lovecraft
# The Return of the King
# Halfway to the Grave
ASIN_CODES: dict[str, list[str]] = {
    "fr": [
        "B07PX3SK1D",
        "0008487294",
        "B0BKP24LN8",
    ],
    "com": [
        "B0FYH24VKH",
        "B002V1A2EA",
        "B0BKPCDWF3",
    ],
    "de": [
        "B0DDPFP14Y",
        "B004LRMZ2Y",
        "B004V03H3W",
    ],
    "co.uk": [
        "B0DBRLKFTD",
        "0008487294",
        "B0BKPKWNFJ",
    ],
}


def _get_asin(locale: str) -> str:
    codes = ASIN_CODES.get(locale)
    return random.choice(codes)  # type: ignore


# def test_audible_fr():
#     asin = _get_asin("fr")
#     audible = Audible(asin, "fr")
#     assert audible.success is True


# def test_audible_fr_auto():
#     asin = _get_asin("fr")
#     audible = Audible(asin)
#     assert audible.success is True


# def test_audible_co_uk():
#     asin = _get_asin("co.uk")
#     audible = Audible(asin, "co.uk")
#     assert audible.success is True


# def test_audible_co_uk_uk():
#     asin = _get_asin("co.uk")
#     audible = Audible(asin)
#     assert audible.success is True


# def test_audible_com():
#     asin = _get_asin("com")
#     audible = Audible(asin, "com")
#     assert audible.success is True


# def test_audible_com_auto():
#     asin = _get_asin("com")
#     audible = Audible(asin)
#     assert audible.success is True


# def test_audible_de():
#     asin = _get_asin("de")
#     audible = Audible(asin, "de")
#     assert audible.success is True


# def test_audible_de_auto():
#     asin = _get_asin("de")
#     audible = Audible(asin)
#     assert audible.success is True
