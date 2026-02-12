"""Represents Audible HTML web scraping"""

from typing import TypedDict, Optional


class AudibleHtml(TypedDict):
    """Represents Audible HTML web scraping"""

    title: Optional[str]
    subtitle: Optional[str]
    genres: Optional[list[str]]
    description: Optional[str]
    copyright: Optional[str]
