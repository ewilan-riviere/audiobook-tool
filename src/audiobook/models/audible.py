"""Represents an Audible audiobook"""

from __future__ import annotations
import re
import os
from pathlib import Path
from datetime import datetime, date, time
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
    copyright: str | None = None
    publisher: str | None = None

    original_title: str | None = None
    original_series: list[str] | None = None
    part: str | None = None

    series: str | None = None
    volume: float | None = None

    authors: list[str] | None = None
    narrators: list[str] | None = None

    published_at: date | None = None
    duration: time | None = None
    language: str | None = None
    abridged: bool | None = None
    cover: str | None = None

    format: str | None = None
    book_format: str | None = None
    sku: str | None = None

    rating: float | None = None
    price: float | None = None

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

        return items

    @property
    def duration_human(self) -> str | None:
        """Get duration as human readable"""
        if not self.duration:
            return None

        return self.duration.strftime("%H:%M:%S")

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
        m4b.copyright = self.copyright
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
            response = http.request("GET", self.cover, preload_content=False)

            if response.status == 200:
                with open(save_path, "wb") as f:
                    for chunk in response.stream(1024):
                        f.write(chunk)
                response.release_conn()

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

    def clean(self) -> dict[str, str | float | None]:
        """Clean title, series and volume to get more interesting data"""
        series = None
        if self.original_series:
            series = self.original_series[0]

        parsed_volume = self._clean_volume(series)
        parsed_title = self._clean_title(series)
        parsed_series = self._clean_series(series)

        if parsed_volume:
            self.volume = parsed_volume
        if parsed_title:
            self.title = parsed_title
        if parsed_series:
            self.series = parsed_series

        return {
            "title": parsed_title,
            "series": parsed_series,
            "volume": parsed_volume,
        }

    def _clean_series(self, series: str | None):
        series_raw = str(series)
        series = series if series else self.subtitle

        if not series:
            return None

        # On retire les numéros de tome qui traînent à la fin
        s = re.sub(
            r"(?i)\s*[,:\-]?\s*(?:book|tome|vol|volume|livre|part)?\s*\d+.*$",
            "",
            series_raw,
        )

        # Gestion des préfixes d'univers (ex: Star Wars - La croisade...)
        # On split et on prend la partie la plus longue pour éviter les préfixes courts
        if " - " in s or " : " in s:
            parts = re.split(r"[:\-\u2013\u2014]", s)
            s = max(parts, key=len).strip()

        # Nettoyage des suffixes de type de collection
        return re.sub(
            r"(?i)\b(Novels|Trilogy|Series|Collection|Novela|Saga)\b", "", s
        ).strip()

    def _clean_title(self, series: str | None):
        if not self.original_title:
            return None

        # On enlève d'abord les parenthèses (souvent des infos techniques)
        t = re.sub(r"\(.*?\)", "", self.original_title)

        # Au lieu de split sur le tiret (qui casse Passe-Miroir),
        # on ne coupe que si le tiret est suivi d'un mot-clé de volume ou de série
        t = re.sub(
            r"(?i)\s*[:\-\u2013\u2014]\s*(?:book|tome|vol|volume|livre|part).*$",
            "",
            t,
        )

        # Si le titre contient encore un ":" ou "-" (souvent "Série - Titre"),
        # on essaie d'isoler le titre s'il y a un doublon avec series_main
        if series and (" - " in t or " : " in t):
            parts = re.split(r"\s*[:\-\u2013\u2014]\s*", t)
            # On garde la partie qui n'est pas le nom de la série
            t = next(
                (p for p in parts if p.lower() not in series.lower()),
                parts[0],
            )

        return str(t).strip()

    def _clean_volume(self, series: str | None):
        parsed_volume = None
        # 1. Extraction du Volume (Logique renforcée)
        # On cherche d'abord les mots-clés, puis un chiffre isolé à la fin si rien n'est trouvé
        full_text = f"{self.original_title or ''} {self.subtitle or ''} {series or ''}"

        # Tentative A : Mot-clé + Chiffre (Tome 2, Book 1.5)
        volume_match = re.search(
            r"(?i)(?:book|tome|vol|volume|n°|livre|part|partie)\s?(\d+(?:\.\d+)?)",
            full_text,
        )

        if volume_match:
            parsed_volume = float(volume_match.group(1))
        else:
            # Tentative B : Chiffre isolé à la fin du titre ou du sous-titre
            # (ex: "La croisade noire 2")
            digit_match = re.search(
                r"(\d+(?:\.\d+)?)$", (self.subtitle or self.title or "").strip()
            )
            if digit_match:
                parsed_volume = float(digit_match.group(1))

        # Fallback sur le volume d'origine si l'extraction a échoué
        if parsed_volume is None and hasattr(self, "volume") and self.volume:
            parsed_volume = float(self.volume)

        return parsed_volume
