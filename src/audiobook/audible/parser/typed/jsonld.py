from typing import TypedDict, Optional
from datetime import date, time


class AudibleJsonld(TypedDict):
    title: Optional[str]
    description: Optional[str]
    authors: Optional[list[str]]
    narrators: Optional[list[str]]
    release_date: Optional[date]
    duration_human: Optional[str]
    duration_time: Optional[time]
    rating: Optional[float]
    cover_url: Optional[str]
    publisher: Optional[str]
    language: Optional[str]
    is_abridged: Optional[bool]
