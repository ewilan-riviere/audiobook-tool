"""Tags of audio file"""

from pathlib import Path
from typing import Dict, Optional, List
import re
from audiobook.common import AutoRepr, AudioChapter
from .mutagen import MutagenReader


class AudioTags(AutoRepr):
    """Tags of audio file"""

    def __init__(self, path: str):
        reader = MutagenReader(path)

        self._path = path
        # Audio Album
        self.album: str | None = reader.get_tag("album")
        # Audio Album Artist
        self.album_artist: str | None = reader.get_tag("album_artist")
        # Audio Artist 1;Audio Artist 2
        self.artist: str | None = reader.get_tag("artist")
        # B0G5QKNT1J
        self.asin: str | None = reader.get_tag("asin")
        # Audio Comment
        self.comment: str | None = reader.get_tag("comment")
        # 1
        self.compilation: str | None = reader.get_tag("compilation")
        # Audio Composer
        self.composer: str | None = reader.get_tag("composer")
        # Audio Copyright
        self.copyright: str | None = reader.get_tag("copyright")
        # Audio Description
        self.description: str | None = reader.get_tag("description")
        # 1/2
        self.disc: str | None = reader.get_tag("disc")
        # Audio Encoded by
        self.encoded_by: str | None = reader.get_tag("encoded_by")
        # Audio Encoder
        self.encoder: str | None = reader.get_tag("encoder")
        # Audio Genre 1;Audio Genre 2
        self.genre: str | None = reader.get_tag("genre")
        # 9780007531486
        self.isbn: str | None = reader.get_tag("isbn")
        # Audio Language
        self.language: str | None = reader.get_tag("language")
        # Audio Lyrics
        self.lyrics: str | None = reader.get_tag("lyrics")
        # Audio Publisher
        self.publisher: str | None = reader.get_tag("publisher")
        # Audio Series
        self.series: str | None = reader.get_tag("series")
        # 2
        self.series_part: str | None = reader.get_tag("series_part")
        # Audio Subtitle
        self.subtitle: str | None = reader.get_tag("subtitle")
        # Audio Synopsis
        self.synopsis: str | None = reader.get_tag("synopsis")
        # Audio Title
        self.title: str | None = reader.get_tag("title")
        # 1/10
        self.track: str | None = reader.get_tag("track")
        # 1979-11-30
        self.date: str | None = reader.get_tag("date")
        self.chapters: List[AudioChapter] = reader.chapters
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
