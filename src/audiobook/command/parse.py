"""parse command of audiobook-tool"""

from audiobook.args import AudiobookArgs
from audiobook.audio import AudioReader


class CommandParse:
    """parse command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        self._args = args

        print(self._args.audio_to_parse)
        if not self._args.audio_to_parse:
            print("Path is necessary!")

        audio = AudioReader(str(self._args.audio_to_parse))
        print(audio)
