"""build command of audiobook-tool"""

from audiobook.args import AudiobookArgs
import audiobook.utils as utils
from audiobook.audible import Audible
from audiobook.forge import AudiobookForge
from audiobook.m4b import M4bSplitter, M4bTagger
from .config import ConfigBuild


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
            working_directory=config.working_path,
            clear=args.clear,
        ).run()

        print("📤 Split M4B file into multiple M4B...")
        splitter = M4bSplitter(
            m4b_file=str(forge.output_path),
            working_directory=config.working_path,
            part_size=config.part_size,
        ).run()

        print("🔖 Update tags with metadata.yml...")
        tagger = M4bTagger(
            m4b_files=splitter.m4b_files,
            audiobook=config.audiobook,
            cover=config.cover_path,
            title=config.audiobook.title,
        ).run()

        print("🧹 Cleaning...")
        utils.make_directory(config.output_path)
        utils.move_files(tagger.m4b_paths, config.output_path)
        config.remove_working_path()

        print(f"📚 Audiobook available at {config.output_path}")

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
