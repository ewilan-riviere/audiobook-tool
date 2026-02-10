"""build command of audiobook-tool"""

from audiobook.args import AudiobookArgs
import audiobook.utils as utils
from audiobook.audible import Audible
from audiobook.forge import AudiobookForge
from audiobook.audio import M4bSplitter, M4bTagger, M4bRenamer
from .config import ConfigBuild
from audiobook.env import PART_SIZE


class CommandBuild:
    """build command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        self.args = args

        print(f"Handle {args.mp3_directory}...")
        if not utils.path_exists(args.mp3_directory):
            raise FileNotFoundError(
                f"Failed! Path {args.mp3_directory} doesn't exists!"
            )

        # ASIN fetch metadata
        self._handle_audible()

        # Setup config
        config = ConfigBuild(args)
        if args.clear:
            print("🖼️ Remove MP3 files source covers...")
            config.remove_covers()

        print("🔨 Forge M4B...")
        forge = AudiobookForge(
            source_path=config.source_path,
            working_directory=config.get_temporary_directory,
            clear=args.clear,
        ).run()
        print(f"\n📦 M4B: `{forge.output_path}` ({forge.size_human})\n")

        print("📤 Split M4B file into multiple M4B...")
        # part_size = PART_SIZE
        part_size = 1
        splitter = M4bSplitter(
            m4b_file=forge.output_path,
            working_directory=config.get_temporary_directory,
            part_size=part_size,
        ).run()

        print("🔖 Update tags with metadata.yml...")
        M4bTagger(
            m4b_files=splitter.m4b_files,
            audiobook=config.audiobook,
            cover=config.cover_path,
        ).run()

        print("📐 Rename M4B splitted...")
        m4b_files = M4bRenamer(
            m4b_files=splitter.m4b_files,
            title=config.audiobook.title,
        ).run()

        print("🧹 Cleaning...")
        utils.make_directory(config.m4b_directory)
        utils.move_files(m4b_files, config.m4b_directory)
        # Delete temporary directory for M4B generation
        config.remove_temporary_directory()

        utils.alert_sound()

    def _handle_audible(self):
        if not self.args.asin or not self.args.mp3_directory:
            return

        yml = utils.get_file(self.args.mp3_directory, "yml")
        cover = utils.get_file(self.args.mp3_directory, "jpg")

        if (yml and cover) and not self.args.clear:
            print(
                "Existing `metadata.yml` and `cover.jpg` are found, "
                "skip Audible fetching..."
            )
        else:
            print(f"Fetch Audible metadata for ASIN {self.args.asin}...")
            if self.args.clear:
                print(
                    "If any `metadata.yml` or `cover.jpg` exists override "
                    "with clear flag..."
                )

            audible = Audible(self.args.asin, self.args.locale)
            if not audible.success:
                return

            audible.save_metadata(self.args.mp3_directory)
            audible.audiobook.save_cover(self.args.mp3_directory)
            print()
            print(
                "You can check `metadata.yml` to validate by yourself "
                "Audible data..."
            )
            if not utils.confirm_action():
                exit()
