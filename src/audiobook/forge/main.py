"""Forge audiobook from MP3 to M4B"""

from pathlib import Path
import audiobook.utils as utils
from audiobook.common import AutoRepr
from .blacksmith import AudiobookBlacksmith


class AudiobookForge(AutoRepr):
    """Forge audiobook from MP3 to M4B"""

    def __init__(self, mp3_directory: str, clear_old_file: bool = False):
        self.mp3_directory = mp3_directory
        parent = Path(mp3_directory).name
        self.m4b_file = f"{self.mp3_directory}/{parent}.m4b"
        self.bytes = 0
        self.blacksmith: AudiobookBlacksmith | None = None

        if clear_old_file:
            self._remove_old_file()

    @property
    def size_human(self) -> str:
        """Get M4B file size"""
        return utils.size_human_readable(self.bytes)

    def _remove_old_file(self):
        if Path(self.m4b_file).is_file():
            utils.delete_file(self.m4b_file)

    def _calculate_size(self):
        if Path(self.m4b_file).is_file():
            self.bytes = utils.get_file_size(self.m4b_file)

    def build(self):
        """Execute build command"""
        if utils.file_exists(self.m4b_file):
            print(f"File {self.m4b_file} exists, skipping forge...")
            return self

        self.blacksmith = AudiobookBlacksmith(self.mp3_directory)
        self.blacksmith.process()

        self._calculate_size()

        return self
