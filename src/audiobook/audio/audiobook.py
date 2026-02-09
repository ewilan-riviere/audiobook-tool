"""Represents an M4B audiobook"""

from typing import Optional
from audiobook.common import AutoRepr


class M4bAudiobook(AutoRepr):
    """Represents an M4B audiobook"""

    title: Optional[str]
    album: Optional[str]
    artist: Optional[str]
    album_artist: Optional[str]
    composer: Optional[str]
    genre: Optional[str]
    date: Optional[str]
    copyright: Optional[str]
    comment: Optional[str]
    description: Optional[str]
    synopsis: Optional[str]
    compilation: Optional[str]
    lyrics: Optional[str]
    publisher: Optional[str]
    language: Optional[str]
    series: Optional[str]
    series_part: Optional[str]
    subtitle: Optional[str]
    isbn: Optional[str]
    asin: Optional[str]

    def to_tags(self):
        return {
            "title": self.title,
            "album": self.title,
            "artist": self.artist,
            "album_artist": self.album_artist,
            "composer": self.composer,
            "genre": self.genre,
            "date": self.date,
            "copyright": self.copyright,
            "comment": self.comment,
            "description": self.description,
            "synopsis": self.synopsis,
            "compilation": self.compilation,
            "lyrics": self.lyrics,
            "publisher": self.publisher,
            "language": self.language,
            "series": self.series,
            "series-part": self.series_part,
            "subtitle": self.subtitle,
            "isbn": self.isbn,
            "asin": self.asin,
        }
