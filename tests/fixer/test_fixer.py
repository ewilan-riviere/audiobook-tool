import pytest
from audiobook.audio.fixer.main import AudioFixer
from audiobook.audio.reader.main import AudioReader
import audiobook.utils as utils
from tests.test_files import (
    FIXER_MP3_HEADER,
    FIXER_CHAPTER,
)


@pytest.mark.parametrize("path", [FIXER_MP3_HEADER, FIXER_CHAPTER])
def test_fix(path: str):
    checker = AudioFixer(path, strict=True)
    original_file = checker.output_path
    success = checker.run()
    assert checker.has_errors is True
    assert success is True

    repaired_file = checker.output_path
    checker = AudioFixer(repaired_file)
    assert checker.has_errors is False

    reader = AudioReader(repaired_file)
    assert reader.tags.title != ""

    utils.remove_file(original_file)
