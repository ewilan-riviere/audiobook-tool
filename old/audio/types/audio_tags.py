"""Audio tags representation"""

from typing import List, Optional, TypedDict
from .chapter_tag import ChapterTag


class AudioTags(TypedDict):
    """Audio tags representation"""

    title: Optional[str]
    subtitle: Optional[str]
    artist: Optional[str]
    album_artist: Optional[str]
    album: Optional[str]
    composer: Optional[str]
    genre: Optional[str]
    year: Optional[int] | Optional[str]
    track: Optional[int] | Optional[str]
    disc: Optional[int] | Optional[str]
    comment: Optional[str]
    description: Optional[str]
    synopsis: Optional[str]
    language: Optional[str]
    copyright: Optional[str]
    publisher: Optional[str]
    series: Optional[str]
    series_part: Optional[str]
    isbn: Optional[str]
    asin: Optional[str]
    compilation: bool
    chapters: List[ChapterTag]
