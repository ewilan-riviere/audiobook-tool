from typing import TypedDict, Optional


class AudibleJson(TypedDict):
    rating: Optional[str]
    series: Optional[str]
    realease_date: Optional[str]
    language: Optional[str]
    format: Optional[str]
    duration: Optional[str]
    publisher: Optional[str]
    categories: Optional[str]
