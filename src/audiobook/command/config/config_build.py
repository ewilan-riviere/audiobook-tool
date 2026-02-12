"""Handle config for build audiobook-tool"""

import tempfile
from pathlib import Path
import audiobook.utils as utils
from audiobook.args import AudiobookArgs
from audiobook.yml import YmlReader
from audiobook.audio import AudioWriter
from audiobook.env import PART_SIZE
from audiobook.common import AutoRepr


class ConfigBuild(AutoRepr):
    """Handle config for build audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        # /path/to/the-wall (with .mp3, metadata.yml, cover.jpg)
        source_path = self._to_path(args.mp3_directory)
        if not source_path:
            raise FileNotFoundError(f"Path {source_path} is not valid!")
        self.source_path = source_path

        # Setup temporary directory (for clean work)
        # /var/folders/m0/xhm5c_mx7yn2b8mqtqhdpc840000gn/T/tmppa8g2g_n
        self.temporary_directory = tempfile.TemporaryDirectory()

        # Load metadata.yml and get tags
        # /path/to/the-wall/metadata.yml
        self.yml_path = utils.get_file(self.source_path, "yml")
        reader = YmlReader(self.yml_path).read()
        # M4bAudiobook for tags from metadata.yml to write inside future M4B
        self.audiobook = reader.to_audiobook()

        # Load cover
        # /path/to/the-wall/cover.jpg
        self.cover_path = utils.get_file(self.source_path, "jpg")
        if not self.cover_path:
            self.cover_path = utils.get_file(self.source_path, "jpeg")

        # Set M4B output path, based on metadata
        # /path/to/the-wall/Assassin’s Apprentice
        custom_output_path = self._to_path(args.output_path)
        if custom_output_path:
            self.output_path = custom_output_path
        else:
            container_name = (
                self.audiobook.title if self.audiobook else reader.default_title
            )
            self.output_path = self.source_path / str(container_name)

        # Single or multiple
        self.single = args.single
        # Part of each size (if not single)
        if args.part_size:
            self.part_size = int(args.part_size)
        else:
            self.part_size = int(PART_SIZE)

    @property
    def working_path(self) -> Path:
        """Get `temporary_directory` as `Path`"""
        return Path(self.temporary_directory.name)

    def remove_working_path(self):
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
