"""write on audio file"""

from typing import Dict, Any, List
from pathlib import Path
from .mutagen import MutagenWriter, AudioChapter


class AudioWriter:
    """write on audio file"""

    def __init__(self, path: str | Path):
        self._writer = MutagenWriter(path)

    def set_tags(self, tags: Dict[str, Any]):
        """Write tags on audio file"""
        return self._writer.set_tags(tags)

    def set_chapters(self, chapters: List[AudioChapter]):
        """Write chapters on audio file (only for M4B files)"""
        return self._writer.set_chapters(chapters)

    def set_cover(self, path: str | Path):
        """Write cover on audio file"""
        return self._writer.set_cover(path)

    def delete_tag(self, key: str):
        """Delete specific tag on audio file"""
        return self._writer.delete_tag(key)

    def delete_cover(self):
        """Delete cover on audio file"""
        return self._writer.delete_cover()
