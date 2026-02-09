"""build command of audiobook-tool"""

from audiobook.args import AudiobookArgs
import audiobook.utils as utils
from audiobook.audible import Audible
from .config import ConfigBuild


class CommandBuild:
    """build command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        self.args = args

        print(f"Handle {args.mp3_directory}...")
        if not utils.path_exists(str(args.mp3_directory)):
            raise FileNotFoundError(
                f"Failed! Path {args.mp3_directory} doesn't exists!"
            )

        # ASIN fetch metadata
        self._handle_audible()

        # Setup config
        config = ConfigBuild(args)
        print(config)
        # utils.delete_directory(config.m4b_directory_output)

        # if args.clear:
        #     print("🖼️ Remove MP3 files source covers...")
        #     config.remove_covers()

        # print("🔨 Forge M4B...")
        # forge = AudiobookForge(config.mp3_directory, args.clear)
        # if args.use_rust:
        #     print("Use audiobook-forge crate")
        #     forge = forge.build_rust()
        # else:
        #     forge = forge.build_native()
        # print(f"\n📦 M4B: `{forge.m4b_file}` ({forge.size})\n")

        # # Set audiobook-forge M4B output
        # config.set_m4b_forge_path(forge.m4b_file)

        # # Only with audiobook-forge
        # # Edit chapters of audiobook-forge M4B output
        # # with MP3 source files `title`
        # if args.use_rust:
        #     M4bChapterEditor(config).run()

        # print("📤 Split M4B file into multiple M4B...")
        # split = M4bSplit(config).run()
        # config.m4b_split_paths = split.m4b_split_paths

        # print("🔖 Update tags with metadata.yml...")
        # M4bTagger(config).run()

        # print("📐 Rename M4B splitted...")
        # config.m4b_split_paths = M4bRenamer(config).run()

        # print("🧹 Cleaning...")
        # # Move files to m4b_directory_output
        # utils.move_files(config.m4b_split_paths, config.m4b_directory_output)
        # # Delete temporary directory for M4B generation
        # config.temporary_directory_delete()

        # utils.alert_sound()

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
            if audible.success:
                audible.save_metadata(self.args.mp3_directory)
                audible.audiobook.save_cover(self.args.mp3_directory)
                print()
                print(
                    "You can check `metadata.yml` to validate by yourself "
                    "Audible data..."
                )
                if not utils.confirm_action():
                    exit()
