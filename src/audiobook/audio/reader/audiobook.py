"""read audiobook"""

from pathlib import Path
import audiobook.utils as utils
from audiobook.common import AutoRepr
from .main import AudioReader


class AudiobookReader(AutoRepr):
    """read audiobook"""

    def __init__(self, audiobook_path: str | Path):
        self.audiobook_path = Path(audiobook_path).resolve()
        self.m4b_files: list[Path] = utils.get_files(self.audiobook_path, "m4b")
        if not self.m4b_files:
            raise FileNotFoundError(
                f"Path {str(self.audiobook_path)} doesn't have any M4B file!"
            )
        self.m4b_parts = len(self.m4b_files)

        self.m4b_readers: list[AudioReader] = []
        for m4b_file in self.m4b_files:
            self.m4b_readers.append(AudioReader(m4b_file))

        self.audiobook_duration_ms = 0
        first_m4b = self.m4b_readers[0]
        self.tags = first_m4b.tags
        for m4b_reader in self.m4b_readers:
            self.audiobook_duration_ms += m4b_reader.properties.duration_ms

        self.tags.save_yml(
            save_path=self.audiobook_path,
            duration=self.audiobook_duration_ms,
        )
        self.tags.save_cover(self.audiobook_path)
