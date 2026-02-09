from audiobook.audible import Audible
from audiobook.utils import file_exists, delete_file


def test_yml():
    save_path = "./tests/media/covers"
    yml_path = f"{save_path}/metadata.yml"
    delete_file(yml_path)

    audible = Audible("B0G5QKNT1J")
    audible.save_metadata(save_path)

    assert file_exists(yml_path) is True
