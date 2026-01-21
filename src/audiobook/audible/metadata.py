"""Represent Audible audiobook"""

from datetime import datetime, time
from pathlib import Path
import requests
import audiobook.utils as utils


class AudibleMetadata:
    """Represent Audible audiobook"""

    def __init__(self):
        self.asin: str | None = None  # B008Y43GBY
        self.title: str | None = None  # Assassin’s Apprentice
        self.authors: list[str] | None = []  # [Robin Hobb]
        self.narrators: list[str] | None = []  # [Paul Boehmer]
        self.description: str | None = None  # The first volume...
        self.release_date: datetime | None = None  # 2012-08-30 00:00:00
        self.duration_human: str | None = None  # 17h 18m
        self.duration_time: time | None = None  # 17:18:00
        self.rating: float | None = None  # 4.6
        self.cover_url: str | None = (
            None  # https://m.media-amazon.com/images/I/618FzSA446L._SL500_.jpg
        )
        self.cover_path: str | None = None  # /path/to/cover.jpg
        self.publisher: str | None = None  # HarperCollins Publishers Limited
        self.language: str | None = None  # english
        self.is_abridged: bool = False

    def get_authors(self):
        if self.authors:
            return self._format_list(self.authors)

        return None

    def get_narrators(self):
        if self.narrators:
            return self._format_list(self.narrators)

        return None

    def get_year(self):
        if self.release_date:
            return self.release_date.year

        return None

    def get_language(self):
        if self.language:
            return self.language.title()

        return None

    def save_cover(self, filename: str | None = None):
        """Download the cover image to Downloads"""
        _download_path = utils.path_join(str(Path.home()), "Downloads")

        try:
            # If no name is provided, the file name is extracted from the URL
            if not filename and self.cover_url:
                filename = self.cover_url.split("/")[-1].split("?")[0]
                if not filename:
                    filename = "audible_cover.jpg"
            if not filename:
                filename = "cover.jpg"

            if not self.cover_url:
                return None

            target_path = utils.path_join(_download_path, filename)

            response = requests.get(self.cover_url, stream=True, timeout=30)
            response.raise_for_status()  # Check if the download was successful

            with open(target_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Success! Image saved as `{target_path}`")
            self.cover_path = target_path

            return self

        except requests.exceptions.RequestException as e:
            print(f"Error when downloading: {e}")
            return self

    def _format_list(self, items: list[str], separator: str = " & ") -> str:
        return separator.join(items)

    def __str__(self) -> str:
        authors = ", ".join(self.authors) if self.authors else "Unknown"
        narrators = ", ".join(self.narrators) if self.narrators else "Unknown"

        details = (
            f"asin: {self.asin}\n"
            f"title: {self.title}\n"
            f"authors: {authors}\n"
            f"narrators: {narrators}\n"
            f"description: {self.description}\n"
            f"release_date: {self.release_date}\n"
            f"duration_human: {self.duration_human}\n"
            f"duration_time: {self.duration_time}\n"
            f"rating: {self.rating}\n"
            f"cover_url: {self.cover_url}\n"
            f"cover_path: {self.cover_path}\n"
            f"publisher: {self.publisher}\n"
            f"language: {self.language}\n"
            f"is_abridged: {self.is_abridged}\n"
        )
        return f"{details}"
