"""Rename M4B with name from metadata"""

from pathlib import Path
from audiobook.metadata import MetadataAudiobook
import audiobook.utils as utils


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
            utils.rename_file(file, f"{self.metadata.title}_Part{i:02d}")
            i = i + 1

    def handle_audiobook(self):
        """Move M4B files to base directory"""
        m4b_files = utils.get_files(self.temporary_directory, "m4b")

        output_path = utils.make_directory(
            f"{self.base_directory}/{self.metadata.title}"
        )
        utils.delete_directory(output_path)

        utils.move_files(m4b_files, str(output_path))
