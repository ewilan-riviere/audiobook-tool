from audiobook.audible import Audible
import audiobook.utils as utils


def test_yml():
    save_path = "./tests/media/covers"
    yml_path = f"{save_path}/metadata.yml"
    utils.remove_file(yml_path)

    audible = Audible("B0G5QKNT1J")
    audible.save_metadata(save_path)

    assert utils.file_exists(yml_path) is True
