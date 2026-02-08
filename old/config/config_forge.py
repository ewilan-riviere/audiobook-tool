"""Handle config for forge audiobook-tool"""

import audiobook.utils as utils
from ..args import AudiobookArgs


class ConfigForge:
    """Handle config for forge audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        # /path/to/audiobook_mp3
        self.mp3_directory = str(args.mp3_directory)

        # List of MP3 file paths as `list[str]` from `mp3_directory`
        self.mp3_list = utils.get_files(self.mp3_directory, "mp3")

    def __str__(self) -> str:
        return (
            f"ConfigForge(\n"
            f"  mp3_directory:  {self.mp3_directory}\n"
            f"  mp3_list:  {len(self.mp3_list)}\n"
            f")"
        )
