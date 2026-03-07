"""extract command of audiobook-tool"""

from pathlib import Path
from audiobook.args import AudiobookArgs
from audiobook.audio import AudioType
from audiobook.m4b import M4bChapterize, M4bExtractor
from audiobook.models import ContainerAudiobook


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

        audio_type: AudioType = AudioType.from_extension(args.audio_type)
        m4b_path = Path(args.m4b_directory).resolve()

        container = ContainerAudiobook(m4b_path)
        container.save_metadata()

        output_path: Path | None = None
        if audio_type == AudioType.MP3:
            extractor = M4bExtractor(container).run(audio_type)
            output_path = extractor.output_path
        elif audio_type == AudioType.M4A:
            extractor = M4bExtractor(container).run(audio_type)
            output_path = extractor.output_path

        if not output_path:
            raise FileNotFoundError("Error on output path!")

        M4bChapterize(
            chapters_path=output_path,
            audio_type=audio_type,
            tags=container.audio_tags.to_dict(),
        ).run()
