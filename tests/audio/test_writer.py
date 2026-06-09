from pathlib import Path
from typing import Dict, Any
import pytest
from pytest import FixtureRequest
from audiobook.audio import (
    AudioReader,
    AudioType,
    AudioWriter,
)
import audiobook.utils as utils
from tests.test_files import RAW_FILES, RAW_FILES_IDS, copy_to_output


@pytest.fixture(name="path", params=RAW_FILES, ids=RAW_FILES_IDS)
def path_fixture(request: FixtureRequest):
    audio_path = Path(request.param)

    if not audio_path.exists():
        pytest.skip(f"Missing file : {audio_path}")

    reader = AudioReader(audio_path)
    new_file = copy_to_output(reader.file_path)

    yield new_file

    utils.remove_file(new_file)


def test_writer(path: str):
    assert Path(path).exists()

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
        "series-part": "2",
        "subtitle": "New Subtitle",
        "synopsis": "New Synopsis",
        "title": None,
        "track": "10/10",
        "date": "1980-11-30",
        "release_date": "2006-06-01",
    }
    writer = AudioWriter(path)
    writer.set_tags(new_tags)
    writer.remove_cover()

    reader = AudioReader(path)

    assert reader.tags.album == new_tags["album"]
    assert reader.tags.album_artist == new_tags["album_artist"]
    assert reader.tags.artist == new_tags["artist"]
    assert reader.tags.asin == new_tags["asin"]
    assert reader.tags.comment == new_tags["comment"]
    assert reader.tags.composer == new_tags["composer"]
    assert reader.tags.copyright_ == new_tags["copyright"]
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
    assert reader.tags.series_part == new_tags["series-part"]
    assert reader.tags.subtitle == new_tags["subtitle"]
    assert reader.tags.synopsis == new_tags["synopsis"]
    assert reader.tags.title == new_tags["title"]
    assert reader.tags.track == new_tags["track"]
    assert reader.tags.date == new_tags["date"]
    assert reader.tags.release_date == new_tags["release_date"]
    assert reader.tags.year == 1980
    assert reader.tags.has_cover is False

    if reader.type == AudioType.MP3:
        # to fix
        assert reader.tags.compilation is None
        assert reader.tags.is_compilation is False

    writer.remove_tag("album_artist")
    reader = AudioReader(path)

    assert reader.tags.album_artist is None
