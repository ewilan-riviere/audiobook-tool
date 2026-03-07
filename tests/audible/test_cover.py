import random

from audiobook.audible import Audible
import audiobook.utils as utils
from tests.test_files import OUTPUT_PATH


ASIN_CODES = [
    "B07PX3SK1D",
    "0008487294",
    "B0BKP24LN8",
]


def test_cover():
    cover_path = f"{OUTPUT_PATH}/cover.jpg"
    utils.remove_file(cover_path)

    asin = random.choice(ASIN_CODES)
    audible = Audible(asin)
    output_path = audible.audiobook.save_cover(OUTPUT_PATH)

    assert output_path
    assert utils.file_exists(cover_path) is True

    utils.remove_file(cover_path)
