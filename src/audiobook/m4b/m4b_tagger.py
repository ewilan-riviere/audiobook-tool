from audiobook.metadata import MetadataFile
from audiobook.config import AudiobookConfig


class M4bTagger:
    def __init__(self, config: AudiobookConfig):
        self._config = config
        self._listing = self._config.m4b_split_paths

    def run(self):
        i = 1
        yml = self._config.metadata_yml
        for m4b_path in self._listing:
            file = MetadataFile(m4b_path)
            file.update_tags(yml.tags_standard(i))
            file.update_tags_custom(yml.tags_custom())
            if self._config.cover_path:
                file.update_cover(self._config.cover_path)
            i = i + 1

        return self
