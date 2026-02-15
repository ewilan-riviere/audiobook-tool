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
        current_dir = Path(os.getcwd()).resolve()
        metadata_yml = audible.save_metadata(current_dir)
        metadata_yml_path = Path(metadata_yml).resolve()

        cover_path: Path | None = None
        if args.cover:
            cover_path = audible.audiobook.save_cover(current_dir)

        print(f"Audible metadata are available: {metadata_yml_path}")
        if cover_path:
            print(f"Audible cover are available: {cover_path}")
