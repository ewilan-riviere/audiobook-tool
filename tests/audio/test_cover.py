import os
from pathlib import Path
import pytest
from pytest import FixtureRequest
from audiobook.audio import AudioReader, AudioWriter
import audiobook.utils as utils
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
    writer_audio = utils.path_join(
        str(audio_path.parent), f"{audio_path.stem}_writer.{extension}"
    )

    utils.copy_file(audio_path, writer_audio)

    yield writer_audio

    utils.remove_file(writer_audio)


def test_cover(writer_path: str):
    writer = AudioWriter(writer_path)
    writer.remove_cover()
    writer.set_cover(PATH_COVER)

    reader = AudioReader(writer_path)
    assert reader.tags.has_cover is True


def test_save_cover(writer_path: str):
    cwd = os.getcwd()
    output_path = utils.path_join(cwd, "tests", "media", "covers")
    utils.remove_file(output_path)
    reader = AudioReader(writer_path)

    utils.make_directory(output_path)
    cover_path = reader.tags.save_cover(str(output_path))

    assert isinstance(cover_path, Path)
    assert utils.file_exists(cover_path) is True


def test_cover_override(writer_path: str):
    writer = AudioWriter(writer_path)
    writer.set_cover(PATH_COVER)

    reader = AudioReader(writer_path)
    assert reader.tags.has_cover is True
