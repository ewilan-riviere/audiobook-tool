from pathlib import Path
import pytest
from pytest import FixtureRequest
from audiobook.audio import AudioReader, AudioWriter
import audiobook.utils as utils
from tests.test_files import (
    COVER_NEW,
    AUDIOBOOKS,
    AUDIOBOOKS_IDS,
    RAW_FILES,
    RAW_FILES_IDS,
    OUTPUT_PATH,
    copy_to_output,
)


@pytest.mark.parametrize("path", RAW_FILES, ids=RAW_FILES_IDS)
def test_cover_raw(path: str):
    reader = AudioReader(path)
    assert reader.tags.has_cover is True


@pytest.mark.parametrize("path", AUDIOBOOKS, ids=AUDIOBOOKS_IDS)
def test_cover_audiobook(path: str):
    reader = AudioReader(path)
    assert reader.tags.has_cover is True


@pytest.fixture(name="path", params=RAW_FILES, ids=RAW_FILES_IDS)
def path_fixture(request: FixtureRequest):
    audio_path = Path(request.param)

    if not audio_path.exists():
        pytest.skip(f"Missing file : {audio_path}")

    reader = AudioReader(audio_path)
    new_file = copy_to_output(reader.file_path)

    yield new_file

    utils.remove_file(new_file)


def test_cover(path: str):
    writer = AudioWriter(path)
    writer.remove_cover()
    reader = AudioReader(path)
    assert reader.tags.has_cover is False

    writer.set_cover(COVER_NEW)
    reader = AudioReader(path)
    assert reader.tags.has_cover is True


def test_save_cover(path: str):
    reader = AudioReader(path)
    cover_path = reader.tags.save_cover(OUTPUT_PATH)

    assert isinstance(cover_path, Path)
    assert utils.file_exists(cover_path) is True
    utils.remove_file(cover_path)


def test_cover_override(path: str):
    writer = AudioWriter(path)
    writer.set_cover(COVER_NEW)

    reader = AudioReader(path)
    assert reader.tags.has_cover is True
