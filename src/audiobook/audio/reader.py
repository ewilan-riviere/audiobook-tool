"""read audio file"""

from pathlib import Path
from .audio_reader import AudioContainer, AudioTags, AudioProperties, AudioType


class AudioReader:
    """read audio file"""

    def __init__(self, path: str | Path):
        self.container = AudioContainer(path)
        self.tags = AudioTags(self.container.path_str)
        self.properties = AudioProperties(self.container.path_str)

        if self.container.extension == "mp3":
            self.type = AudioType.MP3
        elif self.container.extension == "m4b":
            self.type = AudioType.M4B
        else:
            self.type = AudioType.UNKNOWN

    def __str__(self) -> str:
        details = (
            f"container: {self.container}\n"
            f"tags: {self.tags}\n"
            f"properties: {self.properties}\n"
        )
        return f"{details}"
