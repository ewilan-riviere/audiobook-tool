from pathlib import Path

from audiobook import utils
from audiobook.audio.reader.type import AudioType
from audiobook.common import AutoRepr
from audiobook.m4b import M4bExtractor, M4bChapterize
from audiobook.models import ContainerAudiobook


class Fusion(AutoRepr):
    def __init__(self, audiobook_path: Path, new_chapters_path: Path):
        self.audiobook_path: Path = Path(audiobook_path).resolve()
        self.new_chapters_path: Path = Path(new_chapters_path).resolve()

        self.container = ContainerAudiobook(self.audiobook_path)
        meta = self.container.save_metadata()
        self.yml = meta.get("yml")
        self.cover = meta.get("cover")

        self.audio_type: AudioType = AudioType.M4A
        self.new_chapter_files: list[Path] = utils.get_files(
            self.new_chapters_path, "mp3"
        )
        if len(self.new_chapter_files) == 0:
            self.chapter_files = utils.get_files(self.new_chapters_path, "m4a")

        if len(self.new_chapter_files) == 0:
            raise FileNotFoundError(f"No MP3 or M4A found at {self.new_chapters_path}")

        self.old_chapter_files: list[Path] = []

    def run(self):
        extractor = M4bExtractor(self.container).run(self.audio_type)
        self.old_chapter_files = utils.get_files(
            extractor.output_path,
            self.audio_type.value,
        )
        M4bChapterize(
            chapters_path=extractor.output_path,
            audio_type=self.audio_type,
            tags=self.container.audio_tags.to_dict(),
        ).run()

        utils.rprint_(self)

        return self
