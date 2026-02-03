from pathlib import Path
from typing import Dict, Any, List
import pytest
from pytest import FixtureRequest
from audiobook.reader import (
    AudioReader,
    AudioType,
)
from audiobook.writer import AudioWriter
from audiobook.common import AudioChapter
from audiobook.utils import copy_file, path_join, delete_file
from tests.test_files import ALL_FILES, ALL_FILES_IDS


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


def test_writer(writer_path: str):
    assert Path(writer_path).exists()

    new_tags: Dict[str, Any] = {
        "album": "New Album",
        "album_artist": "New Album Artist",
        "artist": "New Artist 1;New Artist 2",
        "asin": "ASIN",
        "comment": "New Comment",
        "compilation": None,
        "composer": "New Composer",
        "copyright": "New Copyright",
        "description": "New Description",
        "disc": "2/2",
        "encoded_by": "New Encoded by",
        "encoder": "New Encoder",
        "genre": "New Genre 1;New Genre 2",
        "isbn": "ISBN",
        "language": "New Language",
        "lyrics": "New Lyrics",
        "publisher": "New Publisher",
        "series": "New Series",
        "series_part": "2",
        "subtitle": "New Subtitle",
        "synopsis": "New Synopsis",
        "title": None,
        "track": "10/10",
        "date": "1980-11-30",
    }
    writer = AudioWriter(writer_path)
    writer.set_tags(new_tags)
    writer.delete_cover()

    reader = AudioReader(writer_path)

    assert reader.tags.album == new_tags["album"]
    assert reader.tags.album_artist == new_tags["album_artist"]
    assert reader.tags.artist == new_tags["artist"]
    assert reader.tags.asin == new_tags["asin"]
    assert reader.tags.comment == new_tags["comment"]
    assert reader.tags.composer == new_tags["composer"]
    assert reader.tags.copyright == new_tags["copyright"]
    assert reader.tags.description == new_tags["description"]
    assert reader.tags.disc == new_tags["disc"]
    assert reader.tags.encoded_by == new_tags["encoded_by"]
    assert reader.tags.encoder == new_tags["encoder"]
    assert reader.tags.genre == new_tags["genre"]
    assert reader.tags.isbn == new_tags["isbn"]
    assert reader.tags.language == new_tags["language"]
    assert reader.tags.lyrics == new_tags["lyrics"]
    assert reader.tags.publisher == new_tags["publisher"]
    assert reader.tags.series == new_tags["series"]
    assert reader.tags.series_part == new_tags["series_part"]
    assert reader.tags.subtitle == new_tags["subtitle"]
    assert reader.tags.synopsis == new_tags["synopsis"]
    assert reader.tags.title == new_tags["title"]
    assert reader.tags.track == new_tags["track"]
    assert reader.tags.date == new_tags["date"]
    assert reader.tags.year == 1980
    assert reader.tags.has_cover is False

    if reader.type == AudioType.MP3:
        # to fix
        assert reader.tags.compilation is None
        assert reader.tags.is_compilation is False

    writer.delete_tag("album_artist")
    reader = AudioReader(writer_path)

    assert reader.tags.album_artist is None


def test_m4b_chapters(writer_path: str):
    reader = AudioReader(writer_path)
    if reader.container.extension == "mp3":
        return

    writer = AudioWriter(writer_path)

    raw_chapters = [
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

    reader = AudioReader(writer_path)
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
