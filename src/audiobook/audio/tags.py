"""Tags of audio file"""

from pathlib import Path
from typing import Dict, Optional, List
import re
from audiobook.utils import AutoRepr
from .mutagen import MutagenReader
from .mutagen.chapter import Chapter


class AudioTags(AutoRepr):
    """Tags of audio file"""

    def __init__(self, path: str):
        reader = MutagenReader(path)

        self._path = path
        self.album: str | None = reader.get_tag("album")  # The Wall
        self.album_artist: str | None = reader.get_tag("album_artist")  # Pink Floyd
        self.artist: str | None = reader.get_tag(
            "artist"
        )  # Syd Barrett;Nick Mason;Roger Waters;Richard Wright
        self.asin: str | None = reader.get_tag("asin")  # B008Y43GBY
        self.comment: str | None = reader.get_tag(
            "comment"
        )  # Recorded at Abbey Road Studios
        self.compilation: str | None = reader.get_tag("compilation")  # 1
        self.composer: str | None = reader.get_tag("composer")  # Syd Barrett
        self.copyright: str | None = reader.get_tag("copyright")  # © 1979 Pink Floyd
        self.description: str | None = reader.get_tag(
            "description"
        )  # The Wall is the eleventh studio album
        self.disc: str | None = reader.get_tag("disc")  # 1/2
        self.encoded_by: str | None = reader.get_tag("encoded_by")  # iTunes
        self.encoder: str | None = reader.get_tag("encoder")  # Lavf62.3.100
        self.genre: str | None = reader.get_tag("genre")  # Progressive Rock;Rock Opera
        self.isbn: str | None = reader.get_tag("isbn")  # 9780007496785
        self.language: str | None = reader.get_tag("language")  # English
        self.lyrics: str | None = reader.get_tag(
            "lyrics"
        )  # Hey! Teachers! Leave them kids alone!
        self.publisher: str | None = reader.get_tag(
            "publisher"
        )  # Pink Floyd Music Publishers Ltd.
        self.series: str | None = reader.get_tag("series")  # The Wall Saga
        self.series_part: str | None = reader.get_tag("series_part")  # 1
        self.subtitle: str | None = reader.get_tag(
            "subtitle"
        )  # All in all, it's just another brick in the wall.
        self.synopsis: str | None = reader.get_tag(
            "synopsis"
        )  # The Wall is one of the most iconic concept albums
        self.title: str | None = reader.get_tag(
            "title"
        )  # Another Brick in the Wall, Part 1
        self.track: str | None = reader.get_tag("track")  # 3/13
        self.date: str | None = reader.get_tag("date")  # 1979-11-30
        self.chapters: List[Chapter] = reader.chapters
        self.has_cover: bool = reader.has_cover
        self.raw: Dict[str, str] = reader.get_all()

    @property
    def is_compilation(self) -> bool:
        """Know if audio file is a part of compilation"""
        if self.compilation == "1":
            return True

        return False

    @property
    def year(self) -> int | None:
        """Get year of release"""
        if self.date:
            year = self._extract_year(self.date)
            if year:
                return int(year)

        return None

    def save_cover(self, output_dir: str | None) -> Path | None:
        """Save cover to `output_dir`"""
        reader = MutagenReader(self._path)

        return reader.save_cover(output_dir)

    def _extract_year(self, date_str: str) -> Optional[str]:
        if not date_str:
            return None

        # We are looking for 4 consecutive digits starting with 19 or 20
        # to avoid capturing the day and month (e.g., 3011)
        match = re.search(r"(19|20)\d{2}", date_str)

        return match.group(0) if match else None
