"""Rename M4B with name from metadata"""

from pathlib import Path
from audiobook.metadata import MetadataAudiobook
from audiobook.utils import (
    get_files,
    move_files,
    rename_file,
    delete_directory,
    make_directory,
)


class M4bRenamer:
    """Rename M4B with name from metadata"""

    def __init__(
        self,
        m4b_files: list[str],
        metadata: MetadataAudiobook,
        temporary_directory: str,
        m4b_file: str,
    ):
        self.m4b_files = m4b_files
        self.metadata = metadata
        self.temporary_directory = temporary_directory

        base_directory = Path(m4b_file)
        self.base_directory = str(base_directory.parent)

    def rename_files(self):
        """Rename M4B splitted with metadata title"""
        i = 1
        for file in self.m4b_files:
            rename_file(file, f"{self.metadata.title}_Part{i:02d}")
            i = i + 1

    def handle_audiobook(self):
        m4b_files = get_files(self.temporary_directory, "m4b")

        output_path = make_directory(f"{self.base_directory}/{self.metadata.title}")
        delete_directory(output_path)

        move_files(m4b_files, str(output_path))
