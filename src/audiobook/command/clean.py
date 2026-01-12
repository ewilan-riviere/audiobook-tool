"""builcleand command of audiobook-tool"""

from audiobook.args import AudiobookArgs
from audiobook.clean import CleanSilences
import audiobook.utils as utils


class CommandClean:
    """clean command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        mp3_directory = str(args.mp3_directory)
        # Clean MP3 files (remove cover and silences)

        # CleanCovers(mp3_directory).remove_covers()

        clean = CleanSilences(mp3_directory)
        clean.remove_silences()
        clean.finalize()

        utils.alert_sound()
