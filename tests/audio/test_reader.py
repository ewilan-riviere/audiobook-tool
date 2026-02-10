import os
from datetime import datetime
from typing import List
from pathlib import Path
import pytest
from audiobook.audio import (
    AudioReader,
    AudioType,
)
from audiobook.audio.reader import (
    AudioTags,
    AudioProperties,
    AudioContainer,
)
from audiobook.common import AudioChapter
from tests.test_files import ALL_FILES, ALL_FILES_IDS, PATH_BUILD_M4B


@pytest.mark.parametrize("path", ALL_FILES, ids=ALL_FILES_IDS)
def test_reader(path: str):
    reader = AudioReader(path)

    assert isinstance(reader.container, AudioContainer)
    assert isinstance(reader.tags, AudioTags)
    assert isinstance(reader.properties, AudioProperties)


@pytest.mark.parametrize("path", ALL_FILES, ids=ALL_FILES_IDS)
def test_reader_container(path: str):
    reader = AudioReader(path)
    container = reader.container

    assert container.path == Path(path).resolve()
    # assert container.basename == "the-wall"
    assert isinstance(container.access_time, datetime)
    assert isinstance(container.modification_time, datetime)
    assert isinstance(container.change_time, datetime)
    assert container.writable is True
    assert container.readable is True
    assert container.is_file is True
    assert container.is_directory is False
    assert container.is_exists is True
    assert container.is_link is False

    assert container.path_str == str(Path(path).resolve())

    if reader.type == AudioType.MP3:
        assert container.extension == "mp3"
        assert container.filename == "the-wall.mp3"
        assert isinstance(container.inode, int)
        assert container.size == 322560
        assert container.size_human == "315.00 KB"
    if reader.type == AudioType.M4B:
        basename = os.path.basename(path)
        assert container.extension == "m4b"
        assert container.filename == basename
        assert isinstance(container.inode, int)
        assert isinstance(container.size, int)
        assert isinstance(container.size_human, str)
        if basename == "the-wall.m4b":
            assert container.extension == "m4b"
            assert container.filename == "the-wall.m4b"
            assert isinstance(container.inode, int)
            assert container.size == 324999
            assert container.size_human == "317.38 KB"


@pytest.mark.parametrize("path", ALL_FILES, ids=ALL_FILES_IDS)
def test_reader_properties(path: str):
    reader = AudioReader(path)
    properties = reader.properties

    assert properties.sample_rate == 48000
    assert properties.channels == 2
    assert properties.channel_layout == "stereo"

    if reader.type == AudioType.MP3:
        assert properties.duration == 10.032
        assert properties.bit_rate == 128000
        assert properties.codec == "mp3"
        assert properties.format_type == "mp3"
        assert properties.format_label == "MPEG audio layer 3"
    if reader.type == AudioType.M4B:
        assert isinstance(properties.duration, float)
        assert isinstance(properties.bit_rate, int)
        assert properties.codec == "aac"
        assert properties.format_type == "mov,mp4,m4a,3gp"
        assert properties.format_label == "QuickTime / MOV"
        basename = os.path.basename(path)
        if basename == "the-wall.m4b":
            assert properties.duration == 10.032
            assert properties.bit_rate == 128000

    assert properties.duration_human == "0:00:10"


@pytest.mark.parametrize("path", ALL_FILES, ids=ALL_FILES_IDS)
def test_reader_tags(path: str):
    tags = AudioReader(path).tags

    assert tags.album == "Audio Album"
    assert tags.album_artist == "Audio Album Artist"
    assert tags.artist == "Audio Artist 1;Audio Artist 2"
    assert tags.asin == "B0G5QKNT1J"
    assert tags.comment == "Audio Comment"
    assert tags.compilation == "1"
    assert tags.composer == "Audio Composer"
    assert tags.copyright == "Audio Copyright"
    assert tags.description == "Audio Description"
    assert tags.disc == "1/2"
    assert tags.encoded_by == "Audio Encoded by"
    assert tags.encoder == "Audio Encoder"
    assert tags.genre == "Audio Genre 1;Audio Genre 2"
    assert tags.isbn == "9780007531486"
    assert tags.language == "Audio Language"
    assert tags.lyrics == "Audio Lyrics"
    assert tags.publisher == "Audio Publisher"
    assert tags.series == "Audio Series"
    assert tags.series_part == "2"
    assert tags.subtitle == "Audio Subtitle"
    assert tags.synopsis == "Audio Synopsis"
    assert tags.title == "Audio Title"
    assert tags.track == "1/10"
    assert tags.date == "1979-11-30"
    assert isinstance(tags.chapters, List)
    assert tags.has_cover is True
    assert isinstance(tags.raw, dict)

    assert tags.is_compilation is True
    assert tags.year == 1979


def test_m4b_chapters():
    reader = AudioReader(PATH_BUILD_M4B)

    chapters = reader.tags.chapters
    last_chapter = chapters[-1]
    assert len(chapters) == 5
    assert last_chapter == AudioChapter(
        id=4,
        start=80018,
        start_time="80.018000",
        end=100035,
        end_time="100.035000",
        tags={"title": "Another Brick In the Wall, Pt. 1 (5)"},
        time_base="1/1000",
    )
