"""Represents an M4B audiobook"""

from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass, asdict


if TYPE_CHECKING:
    from audiobook.audio.reader import AudioTags


@dataclass
class M4bAudiobook:
    """
    Represents an M4B audiobook
    All data are `str` because audiotags are only `str`
    """

    title: str = "Unknown"
    album: str | None = None
    artist: str | None = None
    album_artist: str | None = None
    composer: str | None = None
    genre: str | None = None
    date: str | None = None
    copyright_: str | None = None
    comment: str | None = None
    description: str | None = None
    synopsis: str | None = None
    compilation: str | None = None
    lyrics: str | None = None
    publisher: str | None = None
    language: str | None = None
    series: str | None = None
    series_part: str | None = None
    subtitle: str | None = None
    isbn: str | None = None
    asin: str | None = None

    @property
    def to_tags(self) -> dict[str, str]:
        """Convert M4bAudiobook to tags for audio tags"""
        tags = asdict(self)

        tags["album"] = self.album or self.title
        tags["series-part"] = tags.pop("series_part")

        tags = {
            k: (str(v) if v is not None else "") if not isinstance(v, str) else v
            for k, v in tags.items()
        }

        items: dict[str, str] = {}
        for k, v in tags.items():
            if v is None:  # type: ignore
                value = ""
            elif not isinstance(v, str):  # type: ignore
                value = str(v)
            else:
                value = v

            if value == "None":
                value = ""

            items[k] = value

        return items

    def from_reader_tags(self, tags: AudioTags):
        """Fill M4BAudiobook from AudioReader with AudioTags"""

        self.title = tags.title or "Unknown"
        self.album = tags.album
        self.artist = tags.artist
        self.album_artist = tags.album_artist
        self.composer = tags.composer
        self.genre = tags.genre
        self.date = tags.date
        self.copyright_ = tags.copyright_
        self.comment = tags.comment
        self.description = tags.description
        self.synopsis = tags.synopsis
        self.compilation = tags.compilation
        self.lyrics = tags.lyrics
        self.publisher = tags.publisher
        self.language = tags.language
        self.series = tags.series
        self.series_part = tags.series_part
        self.subtitle = tags.subtitle
        self.isbn = tags.isbn
        self.asin = tags.asin

        return self
