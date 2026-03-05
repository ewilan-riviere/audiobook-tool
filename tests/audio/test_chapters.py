from typing import List

import pytest
from audiobook import utils
from audiobook.audio.reader.main import AudioReader
from audiobook.audio.writer.main import AudioWriter
from audiobook.common.chapter import AudioChapter
from tests.test_files import (
    AUDIOBOOKS,
    AUDIOBOOKS_IDS,
    RAW_M4B_AAC_FILE,
    RAW_M4B_ALAC_FILE,
    copy_to_output,
)


@pytest.mark.parametrize("path", AUDIOBOOKS, ids=AUDIOBOOKS_IDS)
def test_reader(path: str):
    reader = AudioReader(path)

    chapters = reader.tags.chapters
    last_chapter = chapters[-1]
    assert len(chapters) == 5
    assert last_chapter.id == 4
    assert last_chapter.start >= 80018
    assert isinstance(last_chapter.start_time, str)
    assert last_chapter.end >= 100
    assert isinstance(last_chapter.end_time, str)
    assert last_chapter.tags.get("title") == "Another Brick In the Wall, Pt. 1 (5)"
    assert last_chapter.time_base == "1/1000"


@pytest.mark.parametrize(
    "path", [RAW_M4B_AAC_FILE, RAW_M4B_ALAC_FILE], ids=["AAC", "ALAC"]
)
def test_writer(path: str):
    reader = AudioReader(path)
    new_file = copy_to_output(path)
    writer = AudioWriter(new_file)

    raw_chapters: List[AudioChapter] = [
        AudioChapter(
            id=0,
            start=0,
            start_time="0.000000",
            end=341186688,
            end_time="7736.659592",
            tags={"title": "Saison 1 - Eden"},
            time_base="1/44100",
        ),
        AudioChapter(
            id=1,
            start=341186688,
            start_time="7736.659592",
            end=691560576,
            end_time="15681.645714",
            tags={"title": "Saison 2 - Eden"},
            time_base="1/44100",
        ),
    ]
    writer.set_chapters(raw_chapters)

    reader = AudioReader(new_file)
    reader_chapters = reader.tags.chapters
    reader_chapter = reader_chapters[0]
    raw_chapter = raw_chapters[0]

    assert isinstance(reader_chapters, List)
    assert isinstance(reader_chapter, AudioChapter)
    assert reader_chapter.id == raw_chapter.id
    assert reader_chapter.start == raw_chapter.start
    assert reader_chapter.start_time == raw_chapter.start_time
    assert reader_chapter.end == raw_chapter.end
    assert reader_chapter.end_time == raw_chapter.end_time
    assert reader_chapter.tags == raw_chapter.tags
    assert reader_chapter.time_base == raw_chapter.time_base

    utils.remove_file(new_file)
