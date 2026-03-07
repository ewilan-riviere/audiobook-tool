from pathlib import Path
from typing import Any
from audiobook import utils
from audiobook.audio import AudioFixer, AudioReader, AudioType, AudioWriter


class M4bChapterize:
    def __init__(
        self,
        chapters_path: Path,
        audio_type: AudioType,
        tags: dict[str, Any],
    ):
        self.chapters_path: Path = chapters_path
        self.audio_type: AudioType = audio_type
        self.tags: dict[str, Any] = tags

    def run(self):
        chapters = utils.get_files(self.chapters_path, self.audio_type.value)

        i = 0
        for chapter in chapters:
            i = i + 1
            reader = AudioReader(chapter)

            fixer = AudioFixer(chapter, strict=True)
            fixer.run(replace_original=True)

            writer = AudioWriter(chapter)
            writer.set_tags(self.tags)
            writer.set_tag("title", str(reader.tags.title))
            writer.set_tag("track", str(i))

        return self
