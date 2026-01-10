"""Represents metadata.yml as object"""

from typing import Dict, Any


class MetadataAudiobook:
    """Represents metadata.yml as object"""

    def __init__(self, yml: Dict[str, Any], default_title: str):
        self.title: str = yml.get("title") or default_title
        self.authors: str | None = yml.get("authors") or None
        self.narrators: str | None = yml.get("narrators") or None
        self.description: str | None = yml.get("description") or None
        self.lyrics: str | None = yml.get("lyrics") or None
        self.copyright: str | None = yml.get("copyright") or None
        self.genres: str | None = yml.get("genres") or None
        self.series: str | None = yml.get("series") or None
        self.volume: int | None = yml.get("volume") or None
        self.language: str | None = yml.get("language") or None
        self.year: int | None = yml.get("year") or None
        self.editor: str | None = yml.get("editor") or None
        self.subtitle: str | None = yml.get("subtitle") or None

    def tags_standard(self, track: int) -> dict[str, Any]:
        return {
            "title": self.title,
            "album": self.title,
            "artist": self.authors,
            "album_artist": self.authors,
            "composer": self.narrators,
            "genre": self.genres,
            "date": self.year,
            "copyright": self.copyright,
            "comment": self.description,
            "description": self.description,
            "synopsis": self.description,
            "track": track,
        }

    def tags_extra(self) -> dict[str, Any]:
        return {
            # extra tags com.apple.iTunes
            "publisher": self.editor,
            "language": self.language,
            "series": self.series,
            "series-part": self.volume,
            "subtitle": self.subtitle,
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
            f"  Editor:  {self.editor}\n"
            f"  Subtitle:  {self.subtitle}\n"
            f")"
        )
