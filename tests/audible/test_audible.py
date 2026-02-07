from audiobook.audible import Audible

# https://www.audible.fr/pd/B0G5QKNT1J
FARSEER_ASIN = "B0G5QKNT1J"
# https://www.audible.fr/pd/B0G71PC24C
NEBULEUSES_ASIN = "B0G71PC24C"


def test_audible():
    # audible = Audible(FARSEER_ASIN)
    # print(audible)

    audible = Audible(NEBULEUSES_ASIN)
    # print(audible)
