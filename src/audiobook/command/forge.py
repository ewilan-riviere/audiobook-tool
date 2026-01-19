"""forge command of audiobook-tool"""

from audiobook.args import AudiobookArgs
from audiobook.config import ConfigForge
from audiobook.forge import AudiobookBlacksmith
import audiobook.utils as utils


class CommandForge:
    """forge command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        config = ConfigForge(args)
        blacksmith = AudiobookBlacksmith(config.mp3_directory)
        blacksmith.process()
        # blacksmith.validate()

        utils.alert_sound()
