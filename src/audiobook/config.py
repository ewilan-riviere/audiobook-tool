"""Handle path for audiobook-tool"""

import tempfile
import os
from typing import List
from pathlib import Path
import audiobook.utils as utils
from .args import AudiobookArgs
from .metadata import MetadataFile
from .metadata import MetadataYml


class AudiobookConfig:
    """Handle path for audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        # /path/to/audiobook_mp3
        self.mp3_directory = str(args.mp3_directory)

        # /path/to/audiobook_mp3/audiobook_mp3.m4b
        self.m4b_forge_path = utils.get_file(self.mp3_directory, "m4b")

        # /path/to/audiobook_mp3/metadata.yml
        self.metadata_yml_path = utils.get_file(self.mp3_directory, "yml")
        # Load metadata.yml
        yml = MetadataYml(self.metadata_yml_path)
        self.metadata_yml = yml.get_yml()

        # /path/to/audiobook_mp3/cover.jpg
        self.cover_path = utils.get_file(self.mp3_directory, "jpg")
        if not self.cover_path:
            self.cover_path = utils.get_file(self.mp3_directory, "png")
        # /var/folders/m0/xhm5c_mx7yn2b8mqtqhdpc840000gn/T/tmppa8g2g_n
        self.temporary_directory = tempfile.TemporaryDirectory()

        # /path/to/audiobook_mp3/m4b
        m4b_output = Path(str(args.mp3_directory)).name
        self.m4b_directory_output = os.path.join(str(args.mp3_directory), m4b_output)

        # /path/to
        mp3_parent_directory = Path(self.mp3_directory)
        self.mp3_parent_directory = str(mp3_parent_directory.parent)

        # List of MP3 file paths as `list[str]` from `mp3_directory`
        self.mp3_list = utils.get_files(self.mp3_directory, "mp3")
        # List of M4B file paths as `list[str]` from `m4b_directory_output`
        self.m4b_list = utils.get_files(self.m4b_directory_output, "m4b")

        self.mp3_metadata = self._handle_list_metadata(self.mp3_list)
        self.m4b_metadata = self._handle_list_metadata(self.m4b_list)

        self.m4b_forge_metadata = None
        if self.m4b_forge_path:
            self.m4b_forge_metadata = MetadataFile(self.m4b_forge_path)

        self.m4b_split_paths: list[str] = []

    def _handle_list_metadata(self, listing: list[str]):
        items: List[MetadataFile] = []

        for media in listing:
            items.append(MetadataFile(media))

        return items

    def temporary_directory_delete(self):
        """Delete temporary_directory"""
        self.temporary_directory.cleanup()

    def remove_covers(self):
        """Remove covers from MP3 files"""
        for file in self.mp3_metadata:
            file.remove_cover()

    def set_m4b_forge_path(self, m4b_forge_path: str):
        """Set fresh M4B output"""
        if not Path(m4b_forge_path).exists():
            print("Error: {m4b_forge_path} does not exists!")

        self.m4b_forge_path = m4b_forge_path
        if self.m4b_forge_path:
            self.m4b_forge_metadata = MetadataFile(self.m4b_forge_path)

    def __str__(self) -> str:
        metadata_yml_valid = False
        if self.metadata_yml:
            metadata_yml_valid = True
        return (
            f"AudiobookPath(\n"
            f"  mp3_directory:  {self.mp3_directory}\n"
            f"  metadata_yml_path:  {self.metadata_yml_path}\n"
            f"  metadata_yml_valid:  {metadata_yml_valid}\n"
            f"  cover_path:  {self.cover_path}\n"
            f"  m4b_forge_path:  {self.m4b_forge_path}\n"
            f"  temporary_directory:  {self.temporary_directory.name}\n"
            f"  m4b_directory_output:  {self.m4b_directory_output}\n"
            f"  mp3_parent_directory:  {self.mp3_parent_directory}\n"
            f"  mp3_list:  {len(self.mp3_list)}\n"
            f"  m4b_list:  {len(self.m4b_list)}\n"
            f"  mp3_metadata:  {len(self.mp3_metadata)}\n"
            f"  m4b_metadata:  {len(self.m4b_metadata)}\n"
            f"  m4b_split_paths:  {len(self.m4b_split_paths)}\n"
            f")"
        )
