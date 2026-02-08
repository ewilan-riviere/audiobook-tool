from typing import Optional
from datetime import datetime, date, time
from audiobook.common import AutoRepr


class AudibleAudiobook(AutoRepr):
    asin: Optional[str]
    url: Optional[str]
    fetched_at: Optional[datetime]

    title: Optional[str]
    subtitle: Optional[str]
    description: Optional[str]
    copyright: Optional[str]
    publisher: Optional[str]

    authors: Optional[list[str]]
    narrators: Optional[list[str]]

    published_at: Optional[date]
    duration: Optional[time]
    language: Optional[str]
    abridged: Optional[bool]
    cover: Optional[str]

    series: Optional[list[str]]
    series_main: Optional[str]
    part: Optional[str]
    volume: Optional[float]

    format: Optional[str]
    book_format: Optional[str]
    sku: Optional[str]

    rating: Optional[float]
    price: Optional[float]

    genres: Optional[list[str]]
    categories: Optional[list[str]]

    def __init__(self, asin: str, url: str):
        self.asin = asin
        self.url = url
        self.fetched_at = datetime.now()

    def duration_human(self) -> str | None:
        """Get duration as human readable"""
        if not self.duration:
            return None

        return self.duration.strftime("%H:%M")
