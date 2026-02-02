"""parse command of audiobook-tool"""

# import sys
from audiobook.args import AudiobookArgs

# from audiobook.audible import AudibleJson, AudibleYml
from audiobook.reader import AudioReader


class CommandParse:
    """parse command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        self._args = args

        print(self._args.audio_to_parse)
        if not self._args.audio_to_parse:
            print("Path is necessary!")

        audio = AudioReader(str(self._args.audio_to_parse))
        print(audio)
