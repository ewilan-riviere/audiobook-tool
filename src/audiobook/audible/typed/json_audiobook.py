from typing import TypedDict, Optional


class JsonAudiobook(TypedDict):
    authors: Optional[list[str]]
    narrators: Optional[list[str]]
    release_date: Optional[str]
    series: Optional[list[str]]
    part: Optional[str]
    duration: Optional[str]
    rating: Optional[float]
    format: Optional[str]
    publisher: Optional[str]
    language: Optional[str]
    categories: Optional[list[str]]
