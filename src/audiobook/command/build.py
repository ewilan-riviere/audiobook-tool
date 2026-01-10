"""build command of audiobook-tool"""

from audiobook.args import AudiobookArgs
from audiobook.package import AudiobookForge
from audiobook.metadata import MetadataLoader
from audiobook.m4b import M4bParser, M4bRenamer, M4bSplit, M4bTagger, M4bTaggerCustom


class CommandBuild:
    """build command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        args = args

        forge = AudiobookForge(
            mp3_directory=args.mp3_directory, clear_old_file=False
        ).build()
        print(f"\nm4b_file: {forge.m4b_file}\n")

        loader = MetadataLoader(args.mp3_directory)
        metadata = loader.get_metadata_audiobook()

        parser = M4bParser(forge.m4b_file)
        print(parser.cover)

        split = M4bSplit(parser.path, parser.chapters)
        parts = split.run()

        tagger = M4bTagger(parts, metadata, parser.cover)
        m4b_files = tagger.run()

        M4bTaggerCustom(m4b_files, metadata).run()

        parser.cover_delete()

        M4bRenamer(m4b_files, metadata)
