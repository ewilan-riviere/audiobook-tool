"""Represents an Audible audiobook"""

from __future__ import annotations
import os
from pathlib import Path
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import urllib3
from urllib3.exceptions import HTTPError, MaxRetryError
from audiobook.common import AutoRepr


if TYPE_CHECKING:
    from .m4b import M4bAudiobook


@dataclass
class AudibleAudiobook(AutoRepr):
    """Represents an Audible audiobook"""

    asin: str | None = None
    url: str | None = None
    fetched_at: datetime = field(default_factory=datetime.now, init=False)

    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    copyright_: str | None = None
    publisher: str | None = None

    original_title: str | None = None
    original_series: list[str] | None = None
    part: str | None = None

    series: str | None = None
    volume: float | None = None

    authors: list[str] | None = None
    narrators: list[str] | None = None

    published_at: date | None = None
    duration: timedelta | None = None
    language: str | None = None
    abridged: bool | None = None
    cover: str | None = None

    format_: str | None = None
    book_format: str | None = None
    sku: str | None = None
    product_id: str | None = None

    rating: float | None = None
    price: float | None = None
    currency: str | None = None

    genres: list[str] | None = None
    categories: list[str] | None = None

    @property
    def genres_all(self) -> list[str] | None:
        """Get genres with categories"""
        genres = self.genres if self.genres else []
        categories = self.categories if self.categories else []
        if not genres:
            genres = []
        if not categories:
            categories = []

        items = genres + categories
        items.sort()

        return items

    @property
    def duration_human(self) -> str | None:
        """Get duration as human readable"""
        if not self.duration:
            return None

        total_seconds = int(self.duration.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @property
    def authors_list(self):
        """Get authors"""
        if self.authors:
            return self._list_to_str(self.authors)

        return None

    @property
    def narrators_list(self):
        """Get narrators"""
        if self.narrators:
            return self._list_to_str(self.narrators)

        return None

    @property
    def year(self):
        """Get year"""
        if self.published_at:
            return self.published_at.year

        return None

    @property
    def genres_list(self):
        """Get genres"""
        if self.genres_all:
            return self._list_to_str(self.genres_all, "/")

        return None

    @property
    def volume_int(self):
        """Get volume as `int`"""
        if not self.volume:
            return None

        return int(self.volume)

    def to_m4b(self) -> M4bAudiobook:
        """Convert AudibleAudiobook to M4bAudiobook"""
        # pylint: disable=import-outside-toplevel
        from .m4b import M4bAudiobook

        m4b = M4bAudiobook()

        m4b.title = self.title if self.title else "Unknown"
        m4b.album = self.title
        m4b.artist = self.authors_list
        m4b.album_artist = self.authors_list
        m4b.composer = self.narrators_list
        m4b.genre = self.genres_list
        m4b.date = str(self.year) if self.year else None
        m4b.copyright_ = self.copyright_
        m4b.comment = None
        m4b.description = self.description
        m4b.synopsis = self.description
        m4b.compilation = None
        m4b.lyrics = None
        m4b.publisher = self.publisher
        m4b.language = self.language
        m4b.series = self.series
        m4b.series_part = str(self.volume) if self.volume else None
        m4b.subtitle = self.subtitle
        m4b.isbn = None
        m4b.asin = self.asin

        return m4b

    def save_cover(self, save_path: Path | str) -> Path | None:
        """
        Download cover and save it locally.
        """
        if not self.cover:
            return

        save_path = Path(save_path).resolve()

        if not save_path.exists():
            os.makedirs(save_path)

        save_path = save_path / "cover.jpg"
        # upscayl cover
        # sudo Upscayl.app/Contents/Resources/bin/upscayl-bin -f jpg \
        # -i ~/Downloads/51Wmz5ZhdGL._SL500_.jpg -o ~/Downloads/test.jpg -n upscayl-standard-4

        http = urllib3.PoolManager()

        try:
            response = http.request("GET", self.cover, preload_content=False)  # type: ignore

            if response.status == 200:  # type: ignore
                with open(save_path, "wb") as f:
                    for chunk in response.stream(1024):  # type: ignore
                        f.write(chunk)  # type: ignore
                response.release_conn()  # type: ignore

                return save_path

        except TimeoutError:
            print(
                "[bold orange3]⌛ Le serveur a mis trop de temps à répondre.[/bold orange3]"
            )
        except MaxRetryError:
            print(
                "[bold red]❌ Impossible de joindre le serveur (problème DNS ou URL invalide).[/bold red]"
            )
        except HTTPError as e:
            print(f"[bold red]❌ Erreur réseau urllib3 :[/bold red] {e}")
        except IOError as e:
            print(f"[bold red]❌ Erreur d'écriture sur le disque :[/bold red] {e}")

        return None

    def _list_to_str(self, items: list[str], separator: str = " & ") -> str:
        return separator.join(items)
