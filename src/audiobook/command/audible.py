"""audible command of audiobook-tool"""

import sys
from audiobook.args import AudiobookArgs
from audiobook.audible import AudibleJson, AudibleYml


class CommandAudible:
    """audible command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        self._args = args

        print(f"Fetch Audible metadata for {self._args.asin}...")
        if not self._args.asin:
            print("Error: ASIN is necessary.")
            sys.exit(1)

        json = AudibleJson(self._args.asin)
        print(json.audiobook)

        if json.audiobook:
            AudibleYml(json.audiobook)
