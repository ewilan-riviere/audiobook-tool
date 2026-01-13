from typing import List, Optional, TypedDict
from .chapter_dict import ChapterDict


class AudioMetadata(TypedDict):
    title: Optional[str]
    subtitle: Optional[str]
    artist: Optional[str]
    album_artist: Optional[str]
    album: Optional[str]
    composer: Optional[str]
    genre: Optional[str]
    year: Optional[str]
    track: Optional[str]  # format "1/10"
    disc: Optional[str]  # format "1/1"
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
    chapters: List[ChapterDict]
