"""Forge audiobook from MP3 to M4B with Python or audiobook-forge (Rust)"""

import subprocess
import os
from pathlib import Path
from audiobook.forge import AudiobookBlacksmith
import audiobook.utils as utils


class AudiobookForge:
    """Forge audiobook from MP3 to M4B with Python or audiobook-forge (Rust)"""

    def __init__(self, mp3_directory: str, clear_old_file: bool = False):
        self._mp3_directory = mp3_directory
        parent = Path(mp3_directory).name
        self._m4b_file = f"{self._mp3_directory}/{parent}.m4b"
        self._size = 0
        self._size_human: str = "0 B"

        if clear_old_file:
            self.__remove_old_file()

    @property
    def m4b_file(self) -> str:
        """Get M4B file path"""
        return self._m4b_file

    @property
    def size(self) -> str:
        """Get M4B file size"""
        return self._size_human

    def __remove_old_file(self):
        if Path(self._m4b_file).is_file():
            os.remove(self._m4b_file)

    def __convert_size(self):
        """Convert bytes to human readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if self._size < 1024:
                return f"{self._size:.2f} {unit}"
            self._size /= 1024
        return f"{self._size:.2f} PB"

    def __calculate_size(self):
        if Path(self._m4b_file).is_file():
            self._size = os.path.getsize(self._m4b_file)
            self._size_human = self.__convert_size()
        else:
            print(f"ERROR: M4B not found at {self._m4b_file}")

    def build_native(self):
        """Execute build command with Python"""
        if utils.file_exists(self._m4b_file):
            print(f"File {self._m4b_file} exists, skipping forge...")
            return self

        blacksmith = AudiobookBlacksmith(self._mp3_directory)
        blacksmith.process()
        blacksmith.validate()

        self.__calculate_size()

        return self

    def build_rust(self):
        """Execute build command from audiobook-forge"""

        if utils.file_exists(self._m4b_file):
            print(f"File {self._m4b_file} exists, skipping forge...")
            return self

        try:
            subprocess.run(
                [
                    "audiobook-forge",
                    "build",
                    "--root",
                    self._mp3_directory,
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Le binaire a échoué avec le code : {e.returncode}")

        self.__calculate_size()

        return self
