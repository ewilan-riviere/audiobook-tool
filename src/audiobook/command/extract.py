"""extract command of audiobook-tool"""

from audiobook.args import AudiobookArgs
from audiobook.package import AudiobookForge
from audiobook.m4b import M4BMerger, M4BToMP3Splitter
import audiobook.utils as utils
from audiobook.config import ConfigExtract
from audiobook.mp3 import Mp3Fusion
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
        metadata = audio.extract(printing=True)
        cover = audio.extract_cover()

        print()
        audio = AudioMetadataManager(untagged)
        audio.extract(printing=True)

        print()
        audio = AudioMetadataManager(m4b)
        metadata_m4b = audio.extract(printing=True)
        cover_m4b = audio.extract_cover()

        audio = AudioMetadataManager(to_tag)
        audio.clear()
        audio.inject(metadata)
        audio.inject_cover(cover)

        audio = AudioMetadataManager(to_tag)
        audio.extract(printing=True)

        audio = AudioMetadataManager(to_tag_m4b)
        audio.clear()
        audio.inject(metadata_m4b)
        audio.inject_cover(cover_m4b)

        audio = AudioMetadataManager(to_tag_m4b)
        audio.extract(printing=True)

        # manager = AudioMetadataManager("mon_livre.m4b")

        # # Extraction
        # current_tags = manager.extract()
        # print(f"Titre actuel : {current_tags['title']}")

        # # Modification
        # current_tags["title"] = "Nouveau Titre"
        # current_tags["chapters"] = [{"title": "Intro", "start_time": 0.0}]

        # # Injection
        # success = manager.inject(current_tags)

        # Setup config
        # config = ConfigExtract(args)
        # utils.delete_directory(config.m4b_directory_output)

        # # for m4b in config.m4b_metadata:
        # #     print(m4b)
        # print("Merge M4B source files into one...")
        # m4b = M4BMerger(config).merge()
        # if not m4b:
        #     print("Merged M4B not found!")

        # utils.make_directory(config.m4b_directory)
        # utils.move_files([str(m4b)], config.m4b_directory_output)
        # m4b = utils.get_file(config.m4b_directory_output, "m4b")

        # print("Split M4B into MP3 files with chapters...")
        # mp3_list = M4BToMP3Splitter(str(m4b)).split_and_convert()
        # fusion = Mp3Fusion(mp3_list)

        # # Delete temporary directory for M4B generation
        # config.temporary_directory_delete()

        utils.alert_sound()
