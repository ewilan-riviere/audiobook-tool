from typing import Any
import sys
import pytest
from audiobook import app, utils
from audiobook.audio.fixer.main import AudioFixer
from audiobook.audio.reader.main import AudioReader
from audiobook.models.container import ContainerAudiobook
from tests.test_files import (
    AUDIOBOOK_FILES,
    AUDIOBOOK_FILES_IDS,
    create_audiobook,
)


@pytest.mark.parametrize(
    "path",
    AUDIOBOOK_FILES,
    ids=AUDIOBOOK_FILES_IDS,
)
def test_extract_mp3(path: str, monkeypatch: Any):
    _extract(
        monkeypatch=monkeypatch,
        path=path,
        audio_type="mp3",
    )


@pytest.mark.parametrize(
    "path",
    AUDIOBOOK_FILES,
    ids=AUDIOBOOK_FILES_IDS,
)
def test_extract_m4a(path: str, monkeypatch: Any):
    _extract(
        monkeypatch=monkeypatch,
        path=path,
        audio_type="m4a",
    )


def _extract(monkeypatch: Any, path: str, audio_type: str):
    audiobook = create_audiobook(monkeypatch, path, audio_type)
    container = ContainerAudiobook(audiobook)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audiobook-tool",
            "extract",
            str(container.audiobook_path),
            "-t",
            audio_type,
        ],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    extracted_files_path = container.audiobook_path / "extracted_chapters"
    files = utils.get_files(extracted_files_path, audio_type)

    assert len(files) == 5
    first_chapter = files[0]
    reader = AudioReader(first_chapter)
    assert reader.tags.title == "Chapter 1 : In the Flesh? (1)"

    for file_ in files:
        reader = AudioReader(file_)
        fixer = AudioFixer(file_, strict=True)
        assert fixer.has_errors is False

    utils.remove_directory(container.audiobook_path)
