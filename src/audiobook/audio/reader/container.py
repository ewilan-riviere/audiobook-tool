"""Container of audio file"""

import os
from pathlib import Path
from datetime import datetime
from audiobook.common import AutoRepr


class AudioContainer(AutoRepr):
    """Container of audio file"""

    def __init__(self, file_path: Path):
        stat = file_path.stat()

        if not file_path.exists():
            raise FileNotFoundError(f"{str(file_path)} not exists!")

        self.path: Path = file_path.resolve()  # /tests/media/the-wall.mp3
        self.extension: str = file_path.suffix[1:].lower()  # mp3
        self.filename: str = file_path.name  # the-wall.mp3
        self.basename: str = file_path.stem  # the-wall
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

        self.writable: bool = os.access(file_path, os.W_OK)  # True
        self.readable: bool = os.access(file_path, os.R_OK)  # True
        self.is_file: bool = file_path.is_file()  # True
        self.is_directory: bool = file_path.is_dir()  # False
        self.is_exists: bool = file_path.exists()  # True
        self.is_link: bool = file_path.is_symlink()  # False

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
