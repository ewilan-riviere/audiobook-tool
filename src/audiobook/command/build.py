"""build command of audiobook-tool"""

from audiobook.args import AudiobookArgs
from audiobook.package import AudiobookForge
from audiobook.m4b import (
    M4bRenamer,
    M4bSplit,
    M4bChapterEditor,
    M4bTagger,
)
import audiobook.utils as utils
from audiobook.config import AudiobookConfig


class CommandBuild:
    """build command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        # Setup config
        config = AudiobookConfig(args)
        utils.delete_directory(config.m4b_directory_output)

        # Remove MP3 files source covers
        if args.clear_old_m4b:
            config.remove_covers()

        # Create audiobook with audiobook-forge
        # https://crates.io/crates/audiobook-forge
        forge = AudiobookForge(config.mp3_directory, args.clear_old_m4b).build()
        print(f"\nM4B: `{forge.m4b_file}` ({forge.size})\n")

        # Set audiobook-forge M4B output
        config.set_m4b_forge_path(forge.m4b_file)

        # Edit chapters of audiobook-forge M4B output
        # with MP3 source files `title`
        M4bChapterEditor(config).run()

        # Split M4B file into multiple M4B
        split = M4bSplit(config).run()
        config.m4b_split_paths = split.m4b_split_paths

        # Update tags with metadata.yml
        M4bTagger(config).run()

        # Rename M4B splitted
        config.m4b_split_paths = M4bRenamer(config).run()

        # Move files to m4b_directory_output
        utils.move_files(config.m4b_split_paths, config.m4b_directory_output)
        # utils.rename_directory(config.m4b_directory_output, config.metadata_yml.title)
        # Delete temporary directory for M4B generation
        config.temporary_directory_delete()

        utils.alert_sound()
