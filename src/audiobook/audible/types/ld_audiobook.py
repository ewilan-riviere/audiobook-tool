"""Represents Audible JSON-LD Audiobook"""

from dataclasses import dataclass
from datetime import date, timedelta
from .web_scraper import WebScraper


@dataclass
class LDAudiobook(WebScraper):
    """Represents Audible JSON-LD Audiobook"""

    context: str | None = None
    type_: str | None = None
    book_format: str | None = None
    name: str | None = None
    description: str | None = None
    image: str | None = None
    abridged: str | None = None
    author: list[str] | None = None
    read_by: list[str] | None = None
    publisher: str | None = None
    date_published: str | None = None
    in_language: str | None = None
    duration: str | None = None
    regions_allowed: list[str] | None = None
    rating_value: str | None = None
    rating_count: str | None = None
    price: str | None = None
    currency: str | None = None

    def __post_init__(self):
        if self.author:
            self.author.sort()

        if self.read_by:
            self.read_by.sort()

    @property
    def rating_value_typed(self) -> float | None:
        return self._to_float(self.rating_value)

    @property
    def rating_count_typed(self) -> int | None:
        return self._to_int(self.rating_count)

    @property
    def price_typed(self) -> int | None:
        return self._to_int(self.price)

    @property
    def duration_typed(self) -> timedelta | None:
        return self._to_time(self.duration)

    @property
    def duration_seconds(self) -> int | None:
        return self._to_seconds(self.duration_typed)

    @property
    def duration_human(self) -> str | None:
        return self._to_time_human(self.duration_typed)

    @property
    def date_published_typed(self) -> date | None:
        return self._to_date(self.date_published)

    @property
    def abridged_typed(self) -> bool:
        return self._to_bool(self.abridged)
