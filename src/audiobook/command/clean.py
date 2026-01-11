"""builcleand command of audiobook-tool"""

from audiobook.args import AudiobookArgs
from audiobook.metadata import CleanMp3
from audiobook.utils import get_files


class CommandClean:
    """clean command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        # Clean MP3 files (remove cover and silences)
        mp3_list = get_files(str(args.mp3_directory), "mp3")
        clean = CleanMp3(mp3_list)
        clean.remove_covers()
        clean.remove_silences()
        clean.finalize()
