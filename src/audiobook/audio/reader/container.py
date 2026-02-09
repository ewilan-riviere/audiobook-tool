"""Container of audio file"""

import os
import pathlib
from pathlib import Path
from datetime import datetime
from audiobook.common import AutoRepr


class AudioContainer(AutoRepr):
    """Container of audio file"""

    def __init__(self, path: str | Path):
        pl = pathlib.Path(path)
        stat = pl.stat()

        if not pl.exists():
            raise FileNotFoundError(f"{path} not exists!")

        self.path: Path = pl.resolve()  # /tests/media/the-wall.mp3
        self.extension: str = pl.suffix[1:].lower()  # mp3
        self.filename: str = pl.name  # the-wall.mp3
        self.basename: str = pl.stem  # the-wall
        self.inode: int = stat.st_ino  # 23280300
        self.size: int = stat.st_size  # 323052
        self.access_time: datetime = datetime.fromtimestamp(
            stat.st_atime
        )  # 2026-02-03 06:13:28
        self.modification_time: datetime = datetime.fromtimestamp(
            stat.st_mtime
        )  # 2026-02-03 06:12:11
        self.change_time: datetime = datetime.fromtimestamp(
            stat.st_ctime
        )  # 2026-02-03 06:12:11

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
