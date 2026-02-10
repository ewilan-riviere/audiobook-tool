"""Rename M4B files with name from metadata"""

from pathlib import Path
import audiobook.utils as utils


class M4bRenamer:
    """Rename M4B files with name from metadata"""

    _m4b_files: list[Path]
    _title: str | None = None

    def __init__(
        self,
        m4b_files: list[Path],
        title: str | None,
    ):
        self._m4b_files = m4b_files
        self._title = title

    def run(self) -> list[Path]:
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

        return m4b_paths
