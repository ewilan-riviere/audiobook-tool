"""Tags of audio file"""

from pathlib import Path
from typing import Dict, Optional, List, Any
import re
from datetime import timedelta, date, datetime
from audiobook.common import AutoRepr, AudioChapter
from audiobook.yml import YmlWriter
from audiobook.models import AudibleAudiobook
from .mutagen import MutagenReader


class AudioTags(AutoRepr):
    """Tags of audio file"""

    def __init__(self, file_path: Path):
        reader = MutagenReader(file_path)

        self._file_path = file_path
        # Audio Album
        self.album = reader.get_tag("album")
        # Audio Album Artist
        self.album_artist = reader.get_tag("album_artist")
        # Audio Artist 1;Audio Artist 2
        self.artist = reader.get_tag("artist")
        # B0G5QKNT1J
        self.asin = reader.get_tag("asin")
        # Audio Comment
        self.comment = reader.get_tag("comment")
        # 1
        self.compilation = reader.get_tag("compilation")
        # Audio Composer
        self.composer = reader.get_tag("composer")
        # Audio Copyright
        self.copyright = reader.get_tag("copyright")
        # Audio Description
        self.description = reader.get_tag("description")
        # 1/2
        self.disc = reader.get_tag("disc")
        # Audio Encoded by
        self.encoded_by = reader.get_tag("encoded_by")
        # Audio Encoder
        self.encoder = reader.get_tag("encoder")
        # Audio Genre 1;Audio Genre 2
        self.genre = reader.get_tag("genre")
        # 9780007531486
        self.isbn = reader.get_tag("isbn")
        # Audio Language
        self.language = reader.get_tag("language")
        # Audio Lyrics
        self.lyrics = reader.get_tag("lyrics")
        # Audio Publisher
        self.publisher = reader.get_tag("publisher")
        # Audio Series
        self.series = reader.get_tag("series")
        # 2
        self.series_part = reader.get_tag("series-part")
        # Audio Subtitle
        self.subtitle = reader.get_tag("subtitle")
        # Audio Synopsis
        self.synopsis = reader.get_tag("synopsis")
        # Audio Title
        self.title = reader.get_tag("title")
        # 1/10
        self.track = reader.get_tag("track")
        # 1979-11-30
        self.date = reader.get_tag("date")
        self.chapters: List[AudioChapter] = reader.chapters
        self.has_cover: bool = reader.has_cover
        self.raw: Dict[str, str] = reader.get_all()

        if self.subtitle is None and self.comment is not None:
            self.subtitle = self.comment

    @property
    def track_int(self) -> int | None:
        """Get track as `int`"""
        if not self.track:
            return None

        clean_track = self.track.split("/")[0].lstrip("0")

        return int(clean_track) or None

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

    def to_audible_audiobook(
        self,
        duration: int | None = None,
        authors_separator: str = "&",
        narrators_separator: str = "&",
        genres_separator: str = "/",
    ) -> AudibleAudiobook:
        """Convert tags to AudibleAudiobook"""
        audible = AudibleAudiobook(self.asin)

        audible.title = self.title
        audible.subtitle = self.subtitle
        audible.description = self.description
        audible.copyright = self.copyright
        audible.publisher = self.publisher

        audible.original_title = self.title
        audible.original_series = [self.series] if self.series else None
        audible.part = self.series_part

        audible.series = self.series
        audible.volume = float(self.series_part) if self.series_part else None

        audible.authors = (
            self.album_artist.split(authors_separator) if self.album_artist else None
        )
        audible.narrators = (
            self.composer.split(narrators_separator) if self.composer else None
        )

        audible.published_at = date(self.year, 1, 1) if self.year else None

        audible.duration = None
        dt = timedelta(milliseconds=duration) if duration else None
        if dt:
            time_dt = (datetime.min + dt).time() if dt else None
            audible.duration = time_dt

        audible.language = self.language
        audible.abridged = False

        audible.genres = self.genre.split(genres_separator) if self.genre else None

        return audible

    def save_yml(
        self,
        save_path: Path,
        duration: int | None = None,
        authors_separator: str = "&",
        narrators_separator: str = "&",
        genres_separator: str = "/",
    ):
        """Save metadata of audiobook as metadata.yml in same directory"""

        audible = self.to_audible_audiobook(
            duration,
            authors_separator,
            narrators_separator,
            genres_separator,
        )
        writer = YmlWriter(audible, save_path)
        writer.write()

    def save_cover(self, save_path: Path | str) -> Path | None:
        """Save cover to `save_path`"""
        save_path = Path(save_path).resolve()
        reader = MutagenReader(self._file_path)

        return reader.save_cover(save_path)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert attributes to `dict` for `AudioWriter`
        """
        return {
            "title": self.title if self.title else "",
            "subtitle": self.subtitle if self.subtitle else "",
            "artist": self.artist if self.artist else "",
            "album": self.album if self.album else "",
            "album_artist": self.album_artist if self.album_artist else "",
            "date": self.date if self.date else "",
            "year": self.year if self.year else "",
            "track": self.track if self.track else "",
            "disc": self.disc if self.disc else "",
            "genre": self.genre if self.genre else "",
            "series": self.series if self.series else "",
            "series_part": self.series_part if self.series_part else "",
            "publisher": self.publisher if self.publisher else "",
            "composer": self.composer if self.composer else "",
            "description": self.description if self.description else "",
            "synopsis": self.synopsis if self.synopsis else "",
            "comment": self.comment if self.comment else "",
            "isbn": self.isbn if self.isbn else "",
            "asin": self.asin if self.asin else "",
            "language": self.language if self.language else "",
            "copyright": self.copyright if self.copyright else "",
            "compilation": self.is_compilation if self.is_compilation else "",
            "encoded_by": self.encoded_by if self.encoded_by else "",
            "encoder": self.encoder if self.encoder else "",
        }

    def _extract_year(self, date_str: str) -> Optional[str]:
        if not date_str:
            return None

        # We are looking for 4 consecutive digits starting with 19 or 20
        # to avoid capturing the day and month (e.g., 3011)
        match = re.search(r"(19|20)\d{2}", date_str)

        return match.group(0) if match else None
