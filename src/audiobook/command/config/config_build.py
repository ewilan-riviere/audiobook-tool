"""Handle config for build audiobook-tool"""

import tempfile
from dataclasses import dataclass
from pathlib import Path
import audiobook.utils as utils
from audiobook.args import AudiobookArgs
from audiobook.audible import YmlReader
from audiobook.audio import AudioWriter, M4bAudiobook


@dataclass
class ConfigBuild:
    """Handle config for build audiobook-tool"""

    # /path/to/the-wall (with .mp3, metadata.yml, cover.jpg)
    source_path: Path
    # /path/to (parent directory of `source_path`)
    source_directory: Path
    # /var/folders/m0/xhm5c_mx7yn2b8mqtqhdpc840000gn/T/tmppa8g2g_n
    temporary_directory: tempfile.TemporaryDirectory[str]
    # /path/to/the-wall/Assassin’s Apprentice
    m4b_directory: Path
    # M4bAudiobook for tags from metadata.yml to write inside future M4B
    audiobook: M4bAudiobook
    # /path/to/the-wall/metadata.yml
    yml_path: Path | None = None
    # /path/to/the-wall/cover.jpg
    cover_path: Path | None = None

    def __init__(self, args: AudiobookArgs):
        source_path = self._to_path(args.mp3_directory)
        if not source_path:
            raise FileNotFoundError(f"Path {source_path} is not valid!")
        self.source_path = source_path

        # Load parent path
        self.source_directory = Path(self.source_path)

        # Setup temporary directory (for clean work)
        self.temporary_directory = tempfile.TemporaryDirectory()

        # Load metadata.yml and get tags
        self.yml_path = utils.get_file(self.source_path, "yml")
        reader = YmlReader(self.yml_path).read()
        self.audiobook = reader.audiobook

        # Load cover
        self.cover_path = utils.get_file(self.source_path, "jpg")
        if not self.cover_path:
            self.cover_path = utils.get_file(self.source_path, "jpeg")

        # Set M4B output path, based on metadata
        self.m4b_directory = utils.path_join(
            self.source_path,
            reader.audiobook.title or reader.default_title,
        )

    @property
    def get_temporary_directory(self) -> Path:
        """Get `temporary_directory` as `Path`"""
        return Path(self.temporary_directory.name)

    def remove_temporary_directory(self):
        """Delete `temporary_directory`"""
        self.temporary_directory.cleanup()

    def remove_covers(self):
        """Remove covers from MP3 files"""
        mp3_files = utils.get_files(self.source_path, "mp3")
        items: list[AudioWriter] = []
        for mp3_file in mp3_files:
            items.append(AudioWriter(mp3_file))

        for item in items:
            item.remove_cover()

    def _to_path(self, path: str | Path | None) -> Path | None:
        if not path:
            return None

        return Path(path)
