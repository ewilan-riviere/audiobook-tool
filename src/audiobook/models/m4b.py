"""Represents an M4B audiobook"""

from dataclasses import dataclass, asdict


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

        return tags
