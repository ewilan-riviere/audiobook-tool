import pytest
from audiobook import utils
from audiobook.audio import AudioFixer, AudioReader, AudioType
from audiobook.m4b import M4bChapterize, M4bExtractor
from audiobook.models import ContainerAudiobook
from tests.test_files import (
    AUDIOBOOKS,
    AUDIOBOOKS_IDS,
    copy_to_output,
)


@pytest.mark.parametrize(
    "path",
    AUDIOBOOKS,
    ids=AUDIOBOOKS_IDS,
)
def test_extract_m4a(path: str):
    _extract(path, AudioType.M4A)


@pytest.mark.parametrize(
    "path",
    AUDIOBOOKS,
    ids=AUDIOBOOKS_IDS,
)
def test_extract_mp3(path: str):
    _extract(path, AudioType.MP3)


def _extract(path: str, audio_type: AudioType):
    audiobook_path = copy_to_output(path)
    output_path = audiobook_path.parent / audiobook_path.stem
    utils.move_files([audiobook_path], output_path)
    container = ContainerAudiobook(output_path)
    utils.rprint_(container)

    extractor = M4bExtractor(container).run(audio_type)
    M4bChapterize(
        chapters_path=extractor.output_path,
        audio_type=audio_type,
        tags=container.audio_tags.to_dict(),
    ).run()

    files = utils.get_files(extractor.output_path, audio_type.value)

    assert len(files) == 5
    first_chapter = files[0]
    reader = AudioReader(first_chapter)
    assert reader.tags.title == "Chapter 1 : In the Flesh? (1)"

    for file_ in files:
        reader = AudioReader(file_)
        fixer = AudioFixer(file_, strict=True)
        assert fixer.has_errors is False

    utils.remove_directory(container.audiobook_path)
