"""Write metadata into YML file"""

import os
from pathlib import Path
from typing import Any
import yaml
from yaml import SafeDumper, ScalarNode
from ..audiobook import AudibleAudiobook


class BlockStyleDumper(SafeDumper):
    """Custom dumper to force block style on multi-line strings"""

    def represent_scalar(self, tag: str, value: Any, style: Any = None) -> ScalarNode:
        # If the value contains a line break, the '|' style is forced.
        if isinstance(value, str) and "\n" in value:
            style = "|"
        return super().represent_scalar(tag, value, style)  # type: ignore


class YmlWriter:
    """Write metadata into YML file"""

    def __init__(self, audiobook: AudibleAudiobook, save_path: str):
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        save_path = os.path.join(save_path, "metadata.yml")
        self.save_path = Path(save_path).resolve()

        self.data: dict[str, str | int | float | None] = {
            "title": audiobook.title,
            "authors": audiobook.authors_list,
            "narrators": audiobook.narrators_list,
            "description": audiobook.description,
            "lyrics": None,
            "copyright": audiobook.copyright,
            "genres": audiobook.genres_list,
            "series": audiobook.series,
            "volume": audiobook.volume,
            "language": audiobook.language,
            "year": audiobook.year,
            "publisher": audiobook.publisher,
            "subtitle": audiobook.subtitle,
            "isbn": None,
            "asin": audiobook.asin,
        }

    def write(self):
        """Write data into metadata.yml"""
        with open(
            self.save_path,
            "w",
            encoding="utf-8",
        ) as f:
            yaml.dump(
                self.data,
                f,
                Dumper=BlockStyleDumper,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
                width=1000,  # Prevents the dumper from cutting lines in the middle
            )

        print(f"Success: metadata.yml saved as `{self.save_path}`")
