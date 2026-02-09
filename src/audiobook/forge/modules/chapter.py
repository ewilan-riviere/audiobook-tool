"""M4B audio chapter for Forge"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class BlacksmithChapter:
    """M4B audio chapter for Forge"""

    source_path: Path
    temp_aac_path: Path
    title: str
    duration_ms: int = 0
    start_time_ms: int = 0
