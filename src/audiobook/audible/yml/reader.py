"""Read metadata from YML file"""

import os
import logging
from typing import Any, cast
from pathlib import Path
import yaml
from audiobook.common import AutoRepr
from audiobook.audio import M4bAudiobook


logger = logging.getLogger("audiobook.metadata")


class YmlReader(AutoRepr):
    """Read metadata from YML file"""

    def __init__(self, yml_path: str | None):
        self.yml_path = yml_path
        if not self.yml_path or not os.path.exists(self.yml_path):
            logger.info("No metadata.yml found, using defaults.")

        self.yml_data: dict[str, Any] = {}
        self.default_title = self._handle_default_title()

    @property
    def audiobook(self) -> M4bAudiobook:
        """Convert metadata.yml to M4bAudiobook"""
        m4b = M4bAudiobook()

        year = self.yml_data.get("year")
        volume = self.yml_data.get("volume")
        if volume:
            volume = int(volume)

        m4b.title = self.yml_data.get("title") or self.default_title
        m4b.album = self.yml_data.get("title") or self.default_title
        m4b.artist = self.yml_data.get("authors")
        m4b.album_artist = self.yml_data.get("authors")
        m4b.composer = self.yml_data.get("narrators")
        m4b.genre = self.yml_data.get("genres")
        m4b.date = str(year) if year else None
        m4b.copyright = self.yml_data.get("copyright")
        m4b.comment = None
        m4b.description = self.yml_data.get("description")
        m4b.synopsis = self.yml_data.get("description")
        m4b.compilation = None
        m4b.lyrics = self.yml_data.get("lyrics")
        m4b.publisher = self.yml_data.get("publisher")
        m4b.language = self.yml_data.get("language")
        m4b.series = self.yml_data.get("series")
        m4b.series_part = str(volume) if volume else None
        m4b.subtitle = self.yml_data.get("subtitle")
        m4b.isbn = None
        m4b.asin = self.yml_data.get("asin")

        return m4b

    def read(self):
        """Read metadata.yml to extract data as `dict`"""
        if not self.yml_path:
            return self

        try:
            with open(self.yml_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                if isinstance(content, dict):
                    self.yml_data = cast(dict[str, Any], content)
                else:
                    logger.warning(
                        "Metadata file %s is not a dictionary.", self.yml_path
                    )
        except (FileNotFoundError, PermissionError) as e:
            logger.warning("File access error for %s: %s", self.yml_path, e)
        except yaml.YAMLError as e:
            logger.warning("Failed to parse YAML in %s: %s", self.yml_path, e)

        return self

    def _handle_default_title(self) -> str:
        if not self.yml_path:
            return "audiobook"

        return Path(str(self.yml_path)).parent.name
