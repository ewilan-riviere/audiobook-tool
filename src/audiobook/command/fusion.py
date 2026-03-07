"""fusion command of audiobook-tool"""

# from pathlib import Path

from audiobook import utils
from audiobook.args import AudiobookArgs

# from audiobook.models import ContainerAudiobook


class CommandFusion:
    """fusion command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        self._args = args
        utils.rprint_(self._args)

        # if not self._args.audio_to_parse:
        #     print("Path is necessary!")

        # source_files: Path = Path(str(self._args.audio_to_parse)).resolve()
        # if source_files.is_file():
        #     source_files = source_files.parent

        # container = ContainerAudiobook(source_files)
        # ui_utils.rprint_(container)
