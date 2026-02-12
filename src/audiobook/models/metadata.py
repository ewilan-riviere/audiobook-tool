"""Represents an metadata audiobook (fro metadata.yml)"""

from typing import Any
from audiobook.common import AutoRepr


class MetadataAudiobook(AutoRepr):
    """Represents an metadata audiobook (fro metadata.yml)"""

    def __init__(self, data: dict[str, Any], default_title: str = "Unknown"):
        self.title: str = data.get("title") or default_title
        self.authors: str | None = data.get("authors")
        self.narrators: str | None = data.get("narrators")
        self.description: str | None = data.get("description")
        self.lyrics: str | None = data.get("lyrics")
        self.copyright: str | None = data.get("copyright")
        self.genres: str | None = data.get("genres")
        self.series: str | None = data.get("series")
        self.volume: float | None = data.get("volume")
        self.language: str | None = data.get("language")
        self.year: int | None = data.get("year")
        self.publisher: str | None = data.get("publisher")
        self.subtitle: str | None = data.get("subtitle")
        self.isbn: int | None = data.get("isbn")
        self.asin: str | None = data.get("asin")
