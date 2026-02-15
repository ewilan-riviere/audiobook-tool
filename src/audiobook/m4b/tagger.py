"""Update M4B files"""

from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path
from audiobook.audio import AudioWriter
import audiobook.utils as utils
from audiobook.common import AutoRepr

if TYPE_CHECKING:
    from audiobook.models.m4b import M4bAudiobook


class M4bTagger(AutoRepr):
    """Update M4B files"""

    def __init__(
        self,
        m4b_files: list[Path],
        audiobook: M4bAudiobook,
        cover: str | Path | None,
        title: str | None,
        title_series: bool = True,
    ):
        self._m4b_files = m4b_files
        self._audiobook = audiobook
        self._tags = audiobook.to_tags
        self._cover = None
        if cover:
            self._cover = Path(cover).resolve()
        self._title = title
        self._title_series = title_series
        self.m4b_paths: list[Path] = []

    def _tagging(self):
        """Update tags on M4B"""
        i = 1
        for m4b_file in self._m4b_files:
            writer = AudioWriter(m4b_file)
            writer.set_tags(self._tags)
            writer.set_tag("track", str(i))

            if self._cover:
                writer.set_cover(self._cover)

            if (
                self._title_series
                and self._audiobook.series
                and self._audiobook.series_part
            ):
                series_part = int(float(self._audiobook.series_part))
                series_part = f"{series_part:02d}"
                album = f"{self._audiobook.series} {series_part}"
                if (
                    self._audiobook.language
                    and self._audiobook.language.lower() == "french"
                ):
                    album = f"{album} : {self._audiobook.title}"
                else:
                    album = f"{album}: {self._audiobook.title}"
                writer.set_tag("album", album)

            i = i + 1

        return self

    def _rename(self):
        """Rename M4B splitted with metadata title"""
        m4b_paths: list[Path] = []

        i = 1
        for m4b_file in self._m4b_files:
            new_name = m4b_file.stem
            if self._title:
                new_name = f"{self._title}_Part{i:02d}"

            m4b_path = utils.rename_file(m4b_file, new_name)
            m4b_paths.append(m4b_path)

            i = i + 1

        self.m4b_paths = m4b_paths

        return self

    def run(self):
        """Update tags and rename M4B"""
        self._tagging()
        self._rename()

        return self
