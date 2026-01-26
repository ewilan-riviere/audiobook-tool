"""Represents metadata.yml as object"""

from typing import Dict, Any


class MetadataAudiobook:
    """Represents metadata.yml as object"""

    def __init__(self, yml: Dict[str, Any], default_title: str):
        volume = yml.get("volume") or None
        if yml.get("volume") == 0:
            volume = 0

        self.title: str = yml.get("title") or default_title
        self.authors: str | None = yml.get("authors") or None
        self.narrators: str | None = yml.get("narrators") or None
        self.description: str | None = yml.get("description") or None
        self.lyrics: str | None = yml.get("lyrics") or None
        self.copyright: str | None = yml.get("copyright") or None
        self.genres: str | None = yml.get("genres") or None
        self.series: str | None = yml.get("series") or None
        self.volume: int | None = volume
        self.language: str | None = yml.get("language") or None
        self.year: int | None = yml.get("year") or None
        self.publisher: str | None = yml.get("publisher") or None
        self.subtitle: str | None = yml.get("subtitle") or None
        self.isbn: int | None = yml.get("isbn") or None
        self.asin: str | None = yml.get("asin") or None

    def tags_standard(self, number: int) -> dict[str, Any]:
        base_album = self.title
        if self.series and self.volume:
            album = f"{self.series} {self.volume:02d}"
            if self.language and self.language.lower() == "french":
                album = f"{album} : {base_album}"
            else:
                album = f"{album}: {base_album}"
        else:
            album = base_album

        return {
            "title": f"{self.title}, Part {number:02d}",
            "album": album,
            "artist": self.authors,
            "album_artist": self.authors,
            "composer": self.narrators,
            "genre": self.genres,
            "date": self.year,
            "copyright": self.copyright,
            "comment": self.subtitle,
            "description": self.description,
            "synopsis": self.description,
            "track": number,
            # "disc": "1",
            # "compilation": "1",
        }

    def tags_custom(self) -> dict[str, Any]:
        return {
            # extra tags com.apple.iTunes
            "lyrics": self.lyrics,
            "publisher": self.publisher,
            "language": self.language,
            "series": self.series,
            "series-part": self.volume,
            "subtitle": self.subtitle,
            "isbn": self.isbn,
            "asin": self.asin,
        }

    def __str__(self) -> str:
        return (
            f"MetadataAudiobook(\n"
            f"  Title:  {self.title}\n"
            f"  Authors: {self.authors}\n"
            f"  Narrators:  {self.narrators}\n"
            f"  Description:  {self.description}\n"
            f"  Lyrics:  {self.lyrics}\n"
            f"  Copyright:  {self.copyright}\n"
            f"  Genres:  {self.genres}\n"
            f"  Series:  {self.series}\n"
            f"  Volume:  {self.volume}\n"
            f"  Language:  {self.language}\n"
            f"  Year:  {self.year}\n"
            f"  Publisher:  {self.publisher}\n"
            f"  Subtitle:  {self.subtitle}\n"
            f"  ISBN:  {self.isbn}\n"
            f"  ASIN:  {self.asin}\n"
            f")"
        )
