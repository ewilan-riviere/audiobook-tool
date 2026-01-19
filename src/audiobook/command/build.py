"""build command of audiobook-tool"""

from audiobook.args import AudiobookArgs
from audiobook.m4b import (
    M4bRenamer,
    M4bSplit,
    # M4bChapterEditor,
    M4bTagger,
)
import audiobook.utils as utils
from audiobook.config import ConfigBuild
from audiobook.forge import AudiobookForge


class CommandBuild:
    """build command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        # Setup config
        config = ConfigBuild(args)
        utils.delete_directory(config.m4b_directory_output)

        if args.clear_old_m4b:
            print("🖼️ Remove MP3 files source covers...")
            config.remove_covers()

        print("🔨 Forge M4B...")
        forge = AudiobookForge(config.mp3_directory, args.clear_old_m4b).build_native()
        print(f"\n📦 M4B: `{forge.m4b_file}` ({forge.size})\n")

        # Set audiobook-forge M4B output
        config.set_m4b_forge_path(forge.m4b_file)

        # Only with audiobook-forge
        # Edit chapters of audiobook-forge M4B output
        # with MP3 source files `title`
        # M4bChapterEditor(config).run()

        print("📤 Split M4B file into multiple M4B...")
        split = M4bSplit(config).run()
        config.m4b_split_paths = split.m4b_split_paths

        print("🔖 Update tags with metadata.yml...")
        M4bTagger(config).run()

        print("📐 Rename M4B splitted...")
        config.m4b_split_paths = M4bRenamer(config).run()

        print("🧹 Cleaning...")
        # Move files to m4b_directory_output
        utils.move_files(config.m4b_split_paths, config.m4b_directory_output)
        # Delete temporary directory for M4B generation
        config.temporary_directory_delete()

        utils.alert_sound()
