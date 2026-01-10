import subprocess
import json
from typing import List, Dict, Any
from .m4b_chapter import M4bChapter


class Tagger:
    def __init__(self, tags: list[str]) -> None:
        self.tags: list[str] = tags
        self.tags_ffmpeg: list[str] = []
        self.tags_custom: dict[str, Any] = {}

    def add_tag(self, key: str, value: Any):
        if value:
            self.tags_ffmpeg.extend(["-metadata", f"{key}={str(value)}"])

    def add_tag_custom(self, key: str, value: Any):
        if value:
            self.tags_custom[key] = value
