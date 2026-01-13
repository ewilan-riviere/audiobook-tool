"""Handle config for extract audiobook-tool"""

import os
import tempfile
from typing import List
import audiobook.utils as utils
from ..args import AudiobookArgs
from ..metadata import MetadataFile


class ConfigExtract:
    """Handle config for extract audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        # /path/to/audiobook_m4b
        self.m4b_directory = str(args.m4b_directory)
        # List of M4B file paths as `list[str]` from `m4b_directory_output`
        self.m4b_list = utils.get_files(self.m4b_directory, "m4b")
        self.m4b_metadata = self._handle_list_metadata(self.m4b_list)

        # /var/folders/m0/xhm5c_mx7yn2b8mqtqhdpc840000gn/T/tmppa8g2g_n
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.m4b_directory_output = os.path.join(str(args.m4b_directory), "m4b")

    @property
    def temporary_directory_path(self):
        """Get temporary_directory"""
        return self.temporary_directory.name

    def temporary_directory_delete(self):
        """Delete temporary_directory"""
        self.temporary_directory.cleanup()

    def _handle_list_metadata(self, listing: list[str]):
        items: List[MetadataFile] = []

        for media in listing:
            items.append(MetadataFile(media))

        return items

    def __str__(self) -> str:
        return (
            f"ConfigExtract(\n"
            f"  m4b_directory:  {self.m4b_directory}\n"
            f"  m4b_list:  {len(self.m4b_list)}\n"
            f"  m4b_metadata:  {len(self.m4b_metadata)}\n"
            f"  temporary_directory:  {self.temporary_directory.name}\n"
            f"  m4b_directory_output:  {self.m4b_directory_output}\n"
            f")"
        )
