import random

from audiobook.audible import Audible
import audiobook.utils as utils


ASIN_CODES = [
    "B07PX3SK1D",
    "0008487294",
    "B0BKP24LN8",
]


def test_cover():
    save_path = "./tests/media/covers"
    cover_path = f"{save_path}/cover.jpg"
    utils.remove_file(cover_path)

    asin = random.choice(ASIN_CODES)
    audible = Audible(asin)
    output_path = audible.audiobook.save_cover(save_path)

    assert output_path
    assert utils.file_exists(cover_path) is True
