"""Update M4B files tags"""

from pathlib import Path
from audiobook.audio import AudioWriter, M4bAudiobook


class M4bTagger:
    """Update M4B files tags"""

    _m4b_files: list[Path]
    _tags: dict[str, str]
    _cover: Path | None = None

    def __init__(
        self,
        m4b_files: list[Path],
        audiobook: M4bAudiobook,
        cover: str | Path | None,
    ):
        self._m4b_files = m4b_files
        self._tags = audiobook.to_tags
        if cover:
            self._cover = Path(cover)

    def run(self):
        """Execute update"""
        i = 1
        for m4b_file in self._m4b_files:
            writer = AudioWriter(m4b_file)
            writer.set_tags(self._tags)
            writer.set_tag("track", str(i))
            if self._cover:
                writer.set_cover(self._cover)
            i = i + 1

        return self
