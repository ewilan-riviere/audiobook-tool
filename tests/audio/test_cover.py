from pathlib import Path
import pytest
from pytest import FixtureRequest
from src.audiobook.audio import AudioReader, AudioWriter
from src.audiobook.utils import copy_file, path_join, delete_file
from tests.test_files import ALL_FILES, ALL_FILES_IDS, PATH_COVER


@pytest.fixture(
    name="writer_path",
    params=ALL_FILES,
    ids=ALL_FILES_IDS,
)
def writer_file(request: FixtureRequest):
    audio_path = Path(request.param)

    if not audio_path.exists():
        pytest.skip(f"Missing file : {audio_path}")

    extension = audio_path.suffix[1:].lower()
    writer_audio = path_join(
        str(audio_path.parent), f"{audio_path.stem}_writer.{extension}"
    )

    copy_file(audio_path, writer_audio)

    yield writer_audio

    delete_file(writer_audio)


def test_cover(writer_path: str):
    writer = AudioWriter(writer_path)
    writer.delete_cover()
    writer.set_cover(PATH_COVER)

    reader = AudioReader(writer_path)
    assert reader.tags.has_cover is True


def test_cover_override(writer_path: str):
    writer = AudioWriter(writer_path)
    writer.set_cover(PATH_COVER)

    reader = AudioReader(writer_path)
    assert reader.tags.has_cover is True
