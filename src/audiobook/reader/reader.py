"""read audio file"""

from pathlib import Path
from .container import AudioContainer
from .properties import AudioProperties
from .tags import AudioTags
from .type import AudioType


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
