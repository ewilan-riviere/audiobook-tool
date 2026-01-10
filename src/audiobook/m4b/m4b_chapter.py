"""M4B chapter object"""

from typing import Dict, TypedDict


class M4bChapter(TypedDict):
    """M4B chapter object"""

    id: int
    time_base: str
    start: int
    start_time: str
    end: int
    end_time: str
    tags: Dict[str, str]


def chapter_print(chapter: M4bChapter) -> None:
    """Print chapter from M4bChapter"""
    start_f = float(chapter["start_time"])
    end_f = float(chapter["end_time"])

    tags = chapter.get("tags") or {}
    title = tags.get("title", "Sans titre")

    start_str = format_duration(start_f)
    end_str = format_duration(end_f)
    diff_str = format_duration(end_f - start_f)

    print(f"[{start_str} -> {end_str}] {title} ({diff_str})")


def format_duration(seconds_float: float | str) -> str:
    """Format seconds into human readable text"""
    total_seconds = int(seconds_float)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes:02}m {seconds:02}s"
    return f"{minutes}m {seconds:02}s"
