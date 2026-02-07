from datetime import date, time
from audiobook.common import AutoRepr


class AudibleAudiobook(AutoRepr):
    def __init__(self, asin: str, url: str):
        self.asin = asin
        self.url = url
        self.success: bool = False

        # jsonld
        self.title: str | None = None
        self.description: str | None = None
        self.authors: list[str] | None = None
        self.narrators: list[str] | None = None
        self.release_date: date | None = None
        self.duration_time: time | None = None
        self.duration_human: str | None = None
        self.rating: float | None = None
        self.cover: str | None = None
        self.publisher: str | None = None
        self.language: str | None = None
        self.is_abridged: bool = False

        # html
        self.subtitle: str | None = None
        self.copyright: str | None = None
        self.genres: list[str] | None = None

        # json
        self.series: str | None = None
        self.format: str | None = None
        self.categories: str | None = None

        # additionnal
        self.volume: float | None = None
