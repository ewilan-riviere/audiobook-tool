from dataclasses import dataclass
from pathlib import Path
from typing import cast
from mutagen.mp3 import MP3, MPEGInfo


@dataclass
class AudioChapter:
    """Représente un chapitre du livre audio avec ses métadonnées."""

    source_path: Path
    temp_aac_path: Path
    title: str
    duration_ms: int = 0
    start_time_ms: int = 0

    def load_duration(self) -> int:
        """Calcule et stocke la durée du fichier via Mutagen."""
        audio = MP3(self.source_path)
        info = cast(MPEGInfo, audio.info)
        self.duration_ms = int(info.length * 1000)  # type: ignore
        return self.duration_ms
