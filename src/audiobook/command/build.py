"""build command of audiobook-tool"""

from audiobook.args import AudiobookArgs
from audiobook.package import AudiobookForge
from audiobook.metadata import MetadataLoader
from audiobook.clean import CleanCovers
from audiobook.m4b import M4bParser, M4bRenamer, M4bSplit, M4bTagger, M4bTaggerCustom


class CommandBuild:
    """build command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        mp3_directory = str(args.mp3_directory)
        CleanCovers(mp3_directory).remove_covers()

        # Create audiobook with audiobook-forge
        # https://crates.io/crates/audiobook-forge
        forge = AudiobookForge(
            mp3_directory=mp3_directory, clear_old_file=args.clear_old_m4b
        ).build()
        print(f"\nm4b_file: {forge.m4b_file}\n")

        # Load metadata.yml
        loader = MetadataLoader(mp3_directory)
        metadata = loader.get_metadata_audiobook()

        # Extract chapters and cover from M4B
        parser = M4bParser(forge.m4b_file)

        # Split M4B file into multiple M4B
        split = M4bSplit(parser.path, parser.chapters)
        parts = split.run()

        # Set tags on M4B splitted
        tagger = M4bTagger(parts, metadata, parser.cover)
        m4b_files = tagger.run()

        # Set tags extra on M4B splitted
        M4bTaggerCustom(m4b_files, metadata).run()

        # Delete temp cover
        parser.cover_delete()

        # Rename M4B splitted
        renamer = M4bRenamer(m4b_files, metadata, split.get_temp_dir(), forge.m4b_file)
        renamer.rename_files()
        renamer.handle_audiobook()

        # Delete temporary directory for M4B generation
        split.delete_temp_dir()
