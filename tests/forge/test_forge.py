import tempfile
from pathlib import Path
from audiobook.forge import AudiobookForge
from audiobook.audio import AudioReader


def test_forge():
    mp3_directory = "./tests/media/the-wall"
    temporary_directory = tempfile.TemporaryDirectory()
    forge = AudiobookForge(
        source_path=Path(mp3_directory),
        working_directory=Path(temporary_directory.name),
        clear=True,
    ).run()

    m4b_file = Path(forge.output_path)

    reader = AudioReader(m4b_file)
    assert m4b_file.exists() is True
    assert reader.container.extension == "m4b"
    assert len(reader.tags.chapters) == 5
    assert reader.properties.bit_rate == 193661
    assert reader.properties.duration_ms == 100060

    assert reader.container.writable is True
    assert reader.container.readable is True
    assert reader.container.is_file is True

    temporary_directory.cleanup()
