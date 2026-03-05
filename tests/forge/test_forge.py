import tempfile
from pathlib import Path

import pytest
import audiobook.utils as utils
from audiobook.forge import AudiobookForge
from audiobook.audio import AudioReader
from tests.test_files import (
    AUDIOBOOK_FILES,
    AUDIOBOOK_FILES_IDS,
    copy_to_output,
)


@pytest.mark.parametrize(
    "path",
    AUDIOBOOK_FILES,
    ids=AUDIOBOOK_FILES_IDS,
)
def test_forge(path: str):
    files_path = copy_to_output(path)

    temporary_directory = tempfile.TemporaryDirectory()
    forge = AudiobookForge(
        source_path=files_path,
        working_directory=Path(temporary_directory.name),
        clear=True,
    ).run()

    m4b_file = forge.output_path
    if not m4b_file:
        raise FileNotFoundError("M4B not found!")

    reader = AudioReader(m4b_file)
    assert m4b_file.exists() is True
    assert reader.container.extension == "m4b"
    assert len(reader.tags.chapters) == 5
    assert isinstance(reader.properties.bit_rate, int)
    assert reader.properties.duration_ms >= 100000

    assert reader.container.writable is True
    assert reader.container.readable is True
    assert reader.container.is_file is True

    temporary_directory.cleanup()
    utils.remove_directory(files_path)
