"""extract command of audiobook-tool"""

from pathlib import Path
from audiobook import utils
from audiobook.args import AudiobookArgs
from audiobook.audio.reader.main import AudioReader
from audiobook.audio.writer.main import AudioWriter
from audiobook.models import ContainerAudiobook
from audiobook.m4b import M4bExtractor


class CommandExtract:
    """extract command of audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        self.args = args

        if not args.m4b_directory:
            raise FileNotFoundError("M4B path not found!")

        if not args.audio_type:
            args.audio_type = "m4a"

        if args.audio_type not in ["m4a", "mp3"]:
            print(f"Audio type can only be `m4a` or `mp3`, not {args.audio_type}")
            args.audio_type = "m4a"

        m4b_path = Path(args.m4b_directory).resolve()

        container = ContainerAudiobook(m4b_path)
        output_path: Path | None = None
        if args.audio_type == "mp3":
            output_path = M4bExtractor(container).to_mp3()
        elif args.audio_type == "m4a":
            output_path = M4bExtractor(container).to_m4a()

        if not output_path:
            raise FileNotFoundError("Error on output path!")

        chapters = utils.get_files(output_path, args.audio_type)

        i = 0
        for chapter in chapters:
            i = i + 1
            reader = AudioReader(chapter)
            writer = AudioWriter(chapter)

            writer.set_tags(container.audio_tags.to_dict())
            writer.set_tag("title", str(reader.tags.title))
            writer.set_tag("track", str(i))
