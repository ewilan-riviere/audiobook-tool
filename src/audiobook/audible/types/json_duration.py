"""Represents Audible JSON with duration"""

from dataclasses import dataclass, field
import re
from typing import Any
from .web_scraper import WebScraper


@dataclass
class JsonDuration(WebScraper):
    """Represents Audible JSON with duration"""

    duration: str | None = None
    release_date: str | None = None
    series: list[str] | None = None
    part: str | None = None
    format_: str | None = None
    publisher: str | None = None
    language: str | None = None
    categories: list[str] | None = None
    # post_init
    series_typed: str | None = field(init=False)
    part_typed: int | None = field(init=False)

    def __post_init__(self):
        series = self._handle_series()

        self.series_typed = series.get("series")
        self.part_typed = series.get("part")

        if self.categories:
            self.categories.sort()

    def _handle_series(self) -> dict[str, Any]:
        if not self.series:
            return {}

        main_series = self.series[0]
        main_part = None

        if self.part:
            match = re.search(r"\d+", self.part)
            if match:
                main_part = int(match.group())

        return {"series": main_series, "part": main_part}
