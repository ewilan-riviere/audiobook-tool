"""read audio file"""

from pathlib import Path
from .container import AudioContainer
from .tags import AudioTags
from .properties import AudioProperties


class AudioReader:
    """read audio file"""

    def __init__(self, path: str | Path):
        self.container = AudioContainer(path)
        self.tags = AudioTags(self.container.path_str)
        self.properties = AudioProperties(self.container.path_str)

    def __str__(self) -> str:
        details = (
            f"container: {self.container}\n"
            f"tags: {self.tags}\n"
            f"properties: {self.properties}\n"
        )
        return f"{details}"
