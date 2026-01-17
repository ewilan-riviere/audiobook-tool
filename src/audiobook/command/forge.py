"""forge command of audiobook-tool"""

from audiobook.args import AudiobookArgs
from audiobook.config import ConfigForge
from audiobook.forge import AudiobookBlacksmith


class CommandForge:
    """forge command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        config = ConfigForge(args)
        AudiobookBlacksmith(config.mp3_directory).process()
