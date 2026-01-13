from typing import TypedDict


class ChapterDict(TypedDict):
    id: int
    time_base: str  # ex: "1/1000"
    start: int  # en unités time_base
    start_time: float  # en secondes
    end: int  # en unités time_base
    end_time: float  # en secondes
    title: str
