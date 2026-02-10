from audiobook.audible import Audible
import audiobook.utils as utils


def test_cover():
    save_path = "./tests/media/covers"
    cover_path = f"{save_path}/cover.jpg"
    utils.remove_file(cover_path)

    audible = Audible("B0G5QKNT1J")
    audible.audiobook.save_cover(save_path)

    assert utils.file_exists(cover_path) is True
