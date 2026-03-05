"""parse command of audiobook-tool"""

from pathlib import Path

from audiobook.args import AudiobookArgs
from audiobook.models import ContainerAudiobook
from audiobook.utils import ui_utils


class CommandParse:
    """parse command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        self._args = args

        if not self._args.audio_to_parse:
            print("Path is necessary!")

        source_files: Path = Path(str(self._args.audio_to_parse)).resolve()
        if source_files.is_file():
            source_files = source_files.parent

        container = ContainerAudiobook(source_files)
        ui_utils.rprint_("TO FIX")
