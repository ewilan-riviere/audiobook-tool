from audiobook.audible import Audible
import audiobook.utils as utils
from tests.test_files import OUTPUT_PATH, output_path


def test_yml():
    yml_path = output_path("metadata.yml")
    utils.remove_file(yml_path)

    audible = Audible("B0G5QKNT1J")
    audible.save_metadata(OUTPUT_PATH)

    assert utils.file_exists(yml_path) is True
