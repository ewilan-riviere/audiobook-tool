"""forge command of audiobook-tool"""

from audiobook.args import AudiobookArgs
from audiobook.config import ConfigForge
import audiobook.utils as utils
from audiobook.forge import AudiobookForge


class CommandForge:
    """forge command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        config = ConfigForge(args)
        forge = AudiobookForge(config.mp3_directory, True).build_native()
        print(f"\nM4B: `{forge.m4b_file}` ({forge.size})\n")

        utils.alert_sound()
