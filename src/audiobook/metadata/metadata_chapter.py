"""M4B chapter object"""

from typing import Any
import audiobook.utils as utils


class MetadataChapter:
    """M4B chapter object"""

    def __init__(self, chapter: dict[Any, Any]):
        self.chapter = chapter
        self.id = self._extract_key_as_str("id")
        self.time_base = self._extract_key_as_str("time_base")
        self.start = self._extract_key_as_str("start")
        self.start_time = self._extract_key_as_str("start_time")
        self.end = self._extract_key_as_str("end")
        self.end_time = self._extract_key_as_str("end_time")
        tags = self._extract_key("tags")

        tags = self._extract_key("tags")
        if tags and "title" in tags:
            self.title = str(tags["title"])
        else:
            self.title = None

    def _extract_key(self, key: str):
        if key in self.chapter:
            return self.chapter[key]

        return None

    def _extract_key_as_str(self, key: str):
        return str(self._extract_key(key))

    @property
    def string(self) -> str:
        """Print chapter from MetadataChapter"""
        start_f = float(self.start_time)
        end_f = float(self.end_time)

        start_str = utils.format_duration_full(start_f)
        end_str = utils.format_duration_full(end_f)
        diff_str = utils.format_duration_full(end_f - start_f)

        return (
            f"MetadataChapter(\n"
            f"   time: {start_str} -> {end_str}\n"
            f"   duration: {diff_str}\n"
            f"   title: {self.title}\n"
            f")"
        )

    def __str__(self) -> str:
        return (
            f"MetadataChapter(\n"
            f"   id: {self.id}\n"
            f"   time_base: {self.time_base}\n"
            f"   start: {self.start}\n"
            f"   start_time: {self.start_time}\n"
            f"   end: {self.end}\n"
            f"   end_time: {self.end_time}\n"
            f"   title: {self.title}\n"
            f")"
        )
