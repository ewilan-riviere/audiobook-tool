"""Represents Audible HTML web scraping"""

from dataclasses import dataclass
from .web_scraper import WebScraper


@dataclass
class AudibleHtml(WebScraper):
    """Represents Audible HTML web scraping"""

    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    synopsis: str | None = None
    copyright_: str | None = None
    genres: list[str] | None = None
    rating_value: str | None = None
    rating_count: str | None = None
    image_url: str | None = None

    @property
    def rating_value_typed(self) -> float | None:
        return self._to_float(self.rating_value)

    @property
    def rating_count_typed(self) -> int | None:
        return self._to_int(self.rating_count)
