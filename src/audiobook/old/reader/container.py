"""Container of audio file"""

import os
import pathlib
from pathlib import Path
from datetime import datetime
from audiobook.utils import AutoRepr


class AudioContainer(AutoRepr):
    """Container of audio file"""

    def __init__(self, path: str | Path):
        pl = pathlib.Path(path)
        stat = pl.stat()

        self.path: Path = pl.resolve()  # /php-audio/tests/media/test-the-wall.mp3
        self.extension: str = pl.suffix[1:].lower()  # mp3
        self.filename: str = pl.name  # test-the-wall.mp3
        self.basename: str = pl.stem  # test-the-wall
        self.inode: int = stat.st_ino  # 23280300
        self.size: int = stat.st_size  # 321540
        self.access_time: datetime = datetime.fromtimestamp(
            stat.st_atime
        )  # 2026-01-22 10:12:00
        self.modification_time: datetime = datetime.fromtimestamp(
            stat.st_mtime
        )  # 2026-01-22 07:49:33
        self.change_time: datetime = datetime.fromtimestamp(
            stat.st_ctime
        )  # 2026-01-22 07:49:33

        self.writable: bool = os.access(path, os.W_OK)  # True
        self.readable: bool = os.access(path, os.R_OK)  # True
        self.is_file: bool = pl.is_file()  # True
        self.is_directory: bool = pl.is_dir()  # False
        self.is_exists: bool = pl.exists()  # True
        self.is_link: bool = pl.is_symlink()  # False

    @property
    def path_str(self) -> str:
        """Get path as `str`"""
        return str(self.path)

    @property
    def size_human(self) -> str:
        """Converts bytes into a readable format (e.g., 321540 -> 314.0 KB)"""
        decimal_places: int = 2
        size = self.size
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.{decimal_places}f} {unit}"
            size /= 1024.0
        return f"{size:.{decimal_places}f} PB"
