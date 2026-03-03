"""forge command of audiobook-tool"""

from pathlib import Path
import tempfile
from audiobook.args import AudiobookArgs
from audiobook.forge import AudiobookForge


class CommandForge:
    """forge command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        if not args.source_directory:
            raise FileNotFoundError("Path of MP3 directory is needed!")

        # /path/to/audiobook_mp3
        source_path = Path(args.source_directory).resolve()
        # /path/to/output (optional)
        output_path = None
        if args.output_path:
            output_path = Path(args.output_path).resolve()
        temporary_directory = tempfile.TemporaryDirectory()

        forge = AudiobookForge(
            source_path=source_path,
            working_directory=Path(temporary_directory.name),
            clear=True,
        ).run(output_path)

        print(f"\nM4B: `{str(forge.output_path)}` ({forge.size_human})\n")
