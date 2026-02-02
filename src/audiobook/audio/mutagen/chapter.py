"""M4B chapter"""

from typing import Any
from dataclasses import dataclass
from audiobook.utils import AutoRepr


@dataclass
class Chapter(AutoRepr):
    """M4B chapter"""

    id: int
    start: int
    start_time: str
    end: int
    end_time: str
    tags: dict[str, Any]
    time_base: str = "1/1000"  # Mutagen travaille par défaut en ms pour les chapitres
