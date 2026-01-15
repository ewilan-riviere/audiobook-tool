"""extract command of audiobook-tool"""

from audiobook.args import AudiobookArgs
import audiobook.utils as utils
from audiobook.audio import AudioMetadataManager


class CommandExtract:
    """extract command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        tagged = "/Users/ewilan/Transfer/download-storage/GOR/Hors-series/Aria/m4b/merged_audiobook_split/001 - GoR x madmoiZelle  Une nuit en Osmanlie.mp3"
        untagged = "/Users/ewilan/Transfer/download-storage/GOR/Hors-series/Aria/m4b/merged_audiobook_split/003 - GoR x madmoiZelle  Une sorcière chez les mages.mp3"
        m4b = "/Users/ewilan/Transfer/download-storage/GOR/Hors-series/Aria/m4b/merged_audiobook.m4b"
        to_tag_m4b = "/Users/ewilan/Transfer/download-storage/GOR/Hors-series/Aria/Game.of.Roles-.Hors-series.Aria.Part.1.m4b"
        to_tag = "/Users/ewilan/Transfer/download-storage/GOR/Hors-series/Aria/m4b/merged_audiobook_split/002 - Enquête Spéciale  Le serial killer et le stagiaire.mp3"

        audio = AudioMetadataManager(tagged)
        metadata = audio.extract()
        cover = audio.extract_cover()

        print()
        audio = AudioMetadataManager(untagged)
        audio.extract()
        print(audio)

        print()
        audio = AudioMetadataManager(m4b)
        metadata_m4b = audio.extract()
        print(audio)
        cover_m4b = audio.extract_cover()
        print(audio.has_cover())

        audio = AudioMetadataManager(to_tag)
        audio.clear()
        audio.inject(metadata)
        audio.inject_cover(cover)

        audio = AudioMetadataManager(to_tag)
        audio.extract()
        print(audio)

        audio = AudioMetadataManager(to_tag_m4b)
        audio.clear()
        audio.inject(metadata_m4b)
        audio.inject_cover(cover_m4b)

        audio = AudioMetadataManager(to_tag_m4b)
        audio.extract()
        print(audio)

        audio = AudioMetadataManager(to_tag)
        audio.clear()
        audio.extract()
        print(audio)

        audio = AudioMetadataManager(to_tag_m4b)
        audio.clear()
        audio.extract()
        print(audio)

        audio = AudioMetadataManager(to_tag_m4b)
        audio.clear()
        print(audio.has_cover())

        utils.alert_sound()
