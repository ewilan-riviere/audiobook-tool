"""parse command of audiobook-tool"""

from audiobook.args import AudiobookArgs
from audiobook.models import ContainerAudiobook
from audiobook.utils import ui_utils


class CommandParse:
    """parse command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        self._args = args

        print(self._args.audio_to_parse)
        if not self._args.audio_to_parse:
            print("Path is necessary!")

        container = ContainerAudiobook(str(args.audio_to_parse))
        ui_utils.rprint_(container)
