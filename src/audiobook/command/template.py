"""parse command of audiobook-tool"""

from pathlib import Path

from audiobook.args import AudiobookArgs


class CommandTemplate:
    """parse command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        self._args = args

        template_path = Path(__file__).parent.parent / "templates" / "metadata.template.yml"

        dest = Path(self._args.source_directory) / "metadata.yml"
        dest.write_bytes(template_path.read_bytes())

        print(f"`metadata.yml` available at {dest}")
