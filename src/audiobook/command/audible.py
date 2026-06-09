"""audible command of audiobook-tool"""

import os
from pathlib import Path
from audiobook.args import AudiobookArgs
from audiobook.audible import Audible


class CommandAudible:
    """audible command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        self.args = args

        if not args.asin:
            raise Exception("ASIN code is needed!")

        audible = Audible(args.asin, args.locale)
        save_path = Path(os.getcwd()).resolve()
        if self.args.output_path:
            save_path = Path(self.args.output_path)

        metadata_yml = audible.save_metadata(save_path)
        metadata_yml_path = Path(metadata_yml).resolve()

        cover_path: Path | None = None
        if args.cover:
            cover_path = audible.audiobook.save_cover(save_path)

        print(f"Audible metadata are available: {metadata_yml_path}")
        if cover_path:
            print(f"Audible cover are available: {cover_path}")
