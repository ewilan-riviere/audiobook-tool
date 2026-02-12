"""write on audio file"""

from typing import Dict, Any, List
from pathlib import Path
from audiobook.common import AudioChapter
from .mutagen import MutagenWriter


class AudioWriter:
    """write on audio file"""

    def __init__(self, file_path: Path | str):
        file_path = Path(file_path).resolve()
        self._writer = MutagenWriter(file_path)

    def set_tag(self, tag: str, value: str):
        """Write tag on audio file"""
        return self._writer.set_tag(tag, value)

    def set_tags(self, tags: Dict[str, Any]):
        """Write tags on audio file"""
        return self._writer.set_tags(tags)

    def set_chapters(self, chapters: List[AudioChapter]):
        """Write chapters on audio file (only for M4B files)"""
        return self._writer.set_chapters(chapters)

    def set_cover(self, path: str | Path):
        """Write cover on audio file"""
        return self._writer.set_cover(path)

    def remove_tag(self, key: str):
        """Delete specific tag on audio file"""
        return self._writer.remove_tag(key)

    def remove_cover(self):
        """Delete cover on audio file"""
        return self._writer.remove_cover()
