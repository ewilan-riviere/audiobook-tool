"""parse command of audiobook-tool"""

from pathlib import Path

from audiobook.args import AudiobookArgs


class CommandTemplate:
    """parse command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        self._args = args

        # source_files: Path = Path(str()).resolve()
        template_path = Path(__file__).parent / "templates" / "template.txt"
        print(template_path)
        # if source_files.is_file():
        #     source_files = source_files.parent

        # container = ContainerAudiobook(source_files)
        # # TODO FIX PARSE AUDIOBOOK
        # ui_utils.rprint_(container)
