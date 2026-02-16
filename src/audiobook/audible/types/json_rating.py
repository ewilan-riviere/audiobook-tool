"""Represents Audible JSON with rating"""

from dataclasses import dataclass
from .web_scraper import WebScraper


@dataclass
class JsonRating(WebScraper):
    """Represents Audible JSON with rating"""

    rating_count: int | None = None
    rating_value: float | None = None
    authors: list[str] | None = None
    narrators: list[str] | None = None

    def __post_init__(self):
        if self.rating_value:
            self.rating_value = round(self.rating_value, 2)

        if self.authors:
            self.authors.sort()

        if self.narrators:
            self.narrators.sort()

    @property
    def authors_typed(self) -> list[str]:
        return self._handle_authors(self.authors)
