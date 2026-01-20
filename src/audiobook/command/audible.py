"""audible command of audiobook-tool"""

from audiobook.args import AudiobookArgs
from audiobook.audible import AudibleContent, AudibleCover


class CommandAudible:
    """audible command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        self._args = args

        # asin = "B008Y43GBY"
        asin = "B0BKP24LN8"
        content = AudibleContent(asin)
        print(content)

        cover = AudibleCover(content.cover_url).download()
        print(cover)
