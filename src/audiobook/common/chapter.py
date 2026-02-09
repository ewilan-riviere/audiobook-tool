"""M4B audio chapter"""

from typing import Any
from dataclasses import dataclass
from audiobook.common import AutoRepr


@dataclass
class AudioChapter(AutoRepr):
    """M4B audio chapter"""

    id: int
    start: int
    start_time: str
    end: int
    end_time: str
    tags: dict[str, Any]
    time_base: str = "1/44100"

    @property
    def title(self) -> str | None:
        """Get chapter title"""
        if not self.tags:
            return None

        value = self.tags.get("title")
        if not value:
            return None

        return str(value)
