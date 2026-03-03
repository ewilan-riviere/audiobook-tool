import tempfile
from pathlib import Path
import audiobook.utils as utils
from audiobook.forge import AudiobookForge
from audiobook.audio import AudioReader


def test_forge():
    source_directory = "./tests/media/the-wall"
    source_directory_test = "./tests/media/the-wall-test"
    utils.remove_directory(source_directory_test)
    utils.copy_directory(source_directory, source_directory_test)

    temporary_directory = tempfile.TemporaryDirectory()
    forge = AudiobookForge(
        source_path=Path(source_directory),
        working_directory=Path(temporary_directory.name),
        clear=True,
    ).run()

    m4b_file = Path(str(forge.output_path))

    reader = AudioReader(m4b_file)
    assert m4b_file.exists() is True
    assert reader.container.extension == "m4b"
    assert len(reader.tags.chapters) == 5
    assert isinstance(reader.properties.bit_rate, int)
    assert reader.properties.duration_ms == 100060

    assert reader.container.writable is True
    assert reader.container.readable is True
    assert reader.container.is_file is True

    temporary_directory.cleanup()
