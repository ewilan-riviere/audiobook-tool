"""Handle config for build audiobook-tool"""

import tempfile
from dataclasses import dataclass, field
from pathlib import Path
import audiobook.utils as utils
from audiobook.args import AudiobookArgs
from audiobook.audible import YmlReader
from audiobook.audio import AudioWriter


@dataclass
class ConfigBuild:
    """Handle config for build audiobook-tool"""

    # /path/to/the-wall (with .mp3, metadata.yml, cover.jpg)
    source_path: Path
    # /path/to (parent directory of `source_path`)
    source_parent_path: Path
    # /var/folders/m0/xhm5c_mx7yn2b8mqtqhdpc840000gn/T/tmppa8g2g_n
    temporary_directory: tempfile.TemporaryDirectory[str]
    # /path/to/the-wall/Assassin’s Apprentice
    m4b_output_path: Path
    # /path/to/the-wall/Assassin’s Apprentice/Assassin’s Apprentice.m4b
    m4b_forge_path: Path
    # Audio tags from metadata.yml to print inside future M4B
    audio_tags: dict[str, str] = field(default_factory=dict[str, str])
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
        self.source_parent_path = Path(self.source_path)

        # Setup temporary directory (for clean work)
        self.temporary_directory = tempfile.TemporaryDirectory()

        # Load metadata.yml and get tags
        self.yml_path = utils.get_file(self.source_path, "yml")
        reader = YmlReader(self.yml_path).read()
        self.audio_tags = reader.audiobook.to_tags

        # Load cover
        self.cover_path = utils.get_file(self.source_path, "jpg")
        if not self.cover_path:
            self.cover_path = utils.get_file(self.source_path, "jpeg")

        # Set M4B output path, based on metadata
        self.m4b_output_path = utils.path_join(
            self.source_path,
            reader.audiobook.title or reader.default_title,
        )

        # Load M4B file if exists (rebuild)
        m4b_forge_path = utils.get_file(self.source_path, "m4b")
        if not m4b_forge_path:
            raise FileNotFoundError(f"Error on {m4b_forge_path}")
        self.m4b_forge_path = m4b_forge_path

    #     # List of MP3 file paths as `list[str]` from `mp3_directory`
    #     self.mp3_list = utils.get_files(self.mp3_directory, "mp3")
    #     # List of M4B file paths as `list[str]` from `m4b_directory_output`
    #     self.m4b_list = utils.get_files(self.m4b_directory_output, "m4b")

    #     self.mp3_metadata = self._handle_list_metadata(self.mp3_list)
    #     self.m4b_metadata = self._handle_list_metadata(self.m4b_list)

    #     self.m4b_forge_metadata = None
    #     if self.m4b_forge_path:
    #         self.m4b_forge_metadata = MetadataFile(self.m4b_forge_path)

    #     self.m4b_split_paths: list[str] = []

    # def _handle_list_metadata(self, listing: list[str]):
    #     items: List[MetadataFile] = []

    #     for media in listing:
    #         items.append(MetadataFile(media))

    #     return items

    @property
    def temporary_directory_path(self) -> Path:
        """Get `temporary_directory` as `Path`"""
        return Path(self.temporary_directory.name)

    def temporary_directory_delete(self):
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

    # def set_m4b_forge_path(self, m4b_forge_path: str):
    #     """Set fresh M4B output"""
    #     if not Path(m4b_forge_path).exists():
    #         print("Error: {m4b_forge_path} does not exists!")

    #     self.m4b_forge_path = m4b_forge_path
    #     if self.m4b_forge_path:
    #         self.m4b_forge_metadata = MetadataFile(self.m4b_forge_path)

    def _to_path(self, path: str | Path | None) -> Path | None:
        if not path:
            return None

        return Path(path)
