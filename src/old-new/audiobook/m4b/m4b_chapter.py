from typing import Dict, TypedDict


class M4bChapter(TypedDict):
    id: int
    time_base: str
    start: int
    start_time: str
    end: int
    end_time: str
    tags: Dict[str, str]


def chapter_print(chapter: M4bChapter) -> None:
    duration_seconds = float(chapter["end_time"]) - float(chapter["start_time"])

    start = format_duration(chapter["start_time"])
    end = format_duration(chapter["end_time"])
    diff = format_duration(str(duration_seconds))

    title = chapter["tags"].get("title", "Sans titre")

    print(f"[{start} -> {end}] {title} ({diff})")


def format_duration(seconds_float: float | str) -> str:
    total_seconds = int(seconds_float)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes:02}m {seconds:02}s"
    return f"{minutes}m {seconds:02}s"
