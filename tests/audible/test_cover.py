from audiobook.audible import Audible
from audiobook.utils import file_exists, delete_file


def test_cover():
    save_path = "./tests/media/covers"
    cover_path = f"{save_path}/cover.jpg"
    delete_file(cover_path)

    audible = Audible("B0G5QKNT1J")
    audible.audiobook.save_cover(save_path)

    assert file_exists(cover_path) is True
