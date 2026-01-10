from typing import Any
from mutagen.mp4 import MP4
from audiobook.metadata import MetadataAudiobook


class M4bTaggerCustom:
    def __init__(self, parts: list[str], metadata: MetadataAudiobook):
        self.parts = parts
        self.metadata = metadata

    def run(self) -> list[str]:
        files: list[str] = []

        for part in self.parts:
            self.__tag_file(part, self.metadata.tags_extra())

        return files

    def __tag_file(self, file_path: str, extra: dict[str, Any]):
        """
        Force l'écriture des atomes SERIES, SUBTITLE et LANGUAGE via Mutagen.
        C'est cette étape qui rend les tags "non-standards" visibles.
        """
        if not extra:
            return

        audio = MP4(file_path)

        for key, value in extra.items():
            if value:
                atom_key = f"----:com.apple.iTunes:{key}"
                audio[atom_key] = str(value).encode("utf-8")

        audio.save()  # type: ignore
