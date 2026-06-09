"""Represents an audiobook from .m4b files"""

from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict
from dataclasses import dataclass
from audiobook.common import AutoRepr
import audiobook.utils as utils
from audiobook.common import AudioChapter

if TYPE_CHECKING:
    from audiobook.audio import AudioReader
    from audiobook.audio.reader import AudioTags


class MetadataPaths(TypedDict):
    yml: Path
    cover: Path


@dataclass
class ContainerAudiobook(AutoRepr):
    """Represents an audiobook from .m4b files"""

    audiobook_path: Path
    m4b_parts: int
    chapters_count: int
    audio_tags: AudioTags
    audiobook_duration_ms: int
    m4b_files: list[Path]
    m4b_readers: list[AudioReader]
    chapters: list[AudioChapter]

    def __init__(self, audiobook_path: str | Path):
        self.audiobook_path = Path(audiobook_path).resolve()

        self._handle_m4b_files()
        self.m4b_parts: int = len(self.m4b_files)

        self.audiobook_duration_ms: int = 0
        self.m4b_readers: list[AudioReader] = []

        # pylint: disable=import-outside-toplevel
        from audiobook.audio import AudioReader

        self.chapters_count = 0
        self.chapters = []
        for m4b_file in self.m4b_files:
            reader = AudioReader(m4b_file)
            self.m4b_readers.append(reader)
            if reader.tags.chapters:
                for chapter in reader.tags.chapters:
                    self.chapters.append(chapter)
                self.chapters_count = self.chapters_count + len(reader.tags.chapters)

        first_m4b = self.m4b_readers[0]
        first_m4b.tags.title = first_m4b.tags.album
        self.audio_tags = first_m4b.tags
        self.audiobook_duration_ms = self._calculate_duration()

    @property
    def m4b_file(self) -> Path | None:
        """Get first part of M4B files"""
        if not self.m4b_files:
            return None

        return self.m4b_files[0]

    def save_metadata(self) -> MetadataPaths:
        """Save `metadata.yml` and `cover.jpg` to audiobook directory.

        Returns:
            dict with keys ``yml`` and ``cover`` pointing to files::
                {
                    "yml": PosixPath("/path/to/metadata.yml"),
                    "cover": PosixPath("path/to/cover.jpg"),
                }
        """
        save_path = self.audiobook_path
        if save_path.is_file():
            save_path = save_path.parent

        self.audio_tags.save_yml(
            save_path=save_path,
            duration=self.audiobook_duration_ms,
        )
        self.audio_tags.save_cover(save_path, "cover")

        return {
            "yml": save_path / "metadata.yml",
            "cover": save_path / "cover.jpg",
        }

    def _handle_m4b_files(self):
        if str(self.audiobook_path).endswith(".m4b"):
            self.m4b_files: list[Path] = [self.audiobook_path]
            if not self.audiobook_path.exists():
                self.m4b_files = []
        else:
            self.m4b_files: list[Path] = utils.get_files(self.audiobook_path, "m4b")

        if not self.m4b_files:
            raise FileNotFoundError(
                f"Path {str(self.audiobook_path)} doesn't have any M4B file!"
            )

    def _calculate_duration(self) -> int:
        audiobook_duration_ms: int = 0
        for m4b_reader in self.m4b_readers:
            audiobook_duration_ms += m4b_reader.properties.duration_ms

        return audiobook_duration_ms
