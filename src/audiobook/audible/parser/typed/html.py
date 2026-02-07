from typing import TypedDict, Optional


class AudibleHtml(TypedDict):
    title: Optional[str]
    subtitle: Optional[str]
    genres: Optional[list[str]]
    description: Optional[str]
    copyright: Optional[str]
