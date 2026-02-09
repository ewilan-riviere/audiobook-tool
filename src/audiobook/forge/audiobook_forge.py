"""Forge audiobook from MP3 to M4B"""

import os
from pathlib import Path
import audiobook.utils as utils
from audiobook.common import AutoRepr
from .audiobook_blacksmith import AudiobookBlacksmith


class AudiobookForge(AutoRepr):
    """Forge audiobook from MP3 to M4B"""

    def __init__(self, mp3_directory: str, clear_old_file: bool = False):
        self._mp3_directory = mp3_directory
        parent = Path(mp3_directory).name
        self._m4b_file = f"{self._mp3_directory}/{parent}.m4b"
        self._size = 0
        self._size_human: str = "0 B"

        if clear_old_file:
            self._remove_old_file()

    @property
    def m4b_file(self) -> str:
        """Get M4B file path"""
        return self._m4b_file

    @property
    def size(self) -> str:
        """Get M4B file size"""
        return self._size_human

    def _remove_old_file(self):
        if Path(self._m4b_file).is_file():
            os.remove(self._m4b_file)

    def _calculate_size(self):
        if Path(self._m4b_file).is_file():
            self._size = utils.get_file_size(self._m4b_file)
            self._size_human = utils.size_human_readable(self._size)
        else:
            print(f"ERROR: M4B not found at {self._m4b_file}")

    def build(self):
        """Execute build command"""
        if utils.file_exists(self._m4b_file):
            print(f"File {self._m4b_file} exists, skipping forge...")
            return self

        blacksmith = AudiobookBlacksmith(self._mp3_directory)
        blacksmith.process()
        blacksmith.validate()

        self._calculate_size()

        return self
