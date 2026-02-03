"""M4B audio chapter"""

from typing import Any
from dataclasses import dataclass
from audiobook.utils import AutoRepr


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
