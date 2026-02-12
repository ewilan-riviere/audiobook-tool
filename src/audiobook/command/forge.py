"""forge command of audiobook-tool"""

from audiobook.args import AudiobookArgs
import audiobook.utils as utils
from audiobook.forge import AudiobookForge
from .config import ConfigForge


class CommandForge:
    """forge command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        config = ConfigForge(args)
        forge = AudiobookForge(config.mp3_directory, True).build()
        print(f"\nM4B: `{forge.m4b_file}` ({forge.size_human})\n")
