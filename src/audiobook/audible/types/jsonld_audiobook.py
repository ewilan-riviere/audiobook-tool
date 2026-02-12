"""Represents JSON-LD audiobook from Audible website"""

from typing import TypedDict, Optional
from datetime import time, date


class JsonLdAudiobook(TypedDict):
    """Represents JSON-LD audiobook from Audible website"""

    context: Optional[str]
    type: Optional[str]
    book_format: Optional[str]
    name: Optional[str]
    description: Optional[str]
    image: Optional[str]
    abridged: Optional[bool]
    author: Optional[list[str]]
    read_by: Optional[list[str]]
    publisher: Optional[str]
    date_published: Optional[date]
    in_language: Optional[str]
    duration: Optional[time]
    regions_allowed: Optional[list[str]]
    rating: Optional[float]
    price: Optional[float]
