"""Rename M4B with name from metadata"""

from audiobook.config import AudiobookConfig
import audiobook.utils as utils


class M4bRenamer:
    """Rename M4B with name from metadata"""

    def __init__(self, config: AudiobookConfig):
        self._config = config
        self._metadata = config.metadata_yml
        self.m4b_split_paths = config.m4b_split_paths

    def run(self) -> list[str]:
        """Rename M4B splitted with metadata title"""
        new_paths: list[str] = []

        i = 1
        for file in self.m4b_split_paths:
            new_path = utils.rename_file(file, f"{self._metadata.title}_Part{i:02d}")
            new_paths.append(new_path)
            i = i + 1

        return new_paths
