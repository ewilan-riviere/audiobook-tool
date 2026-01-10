"""Load metadata.yml and inject data into MetadataAudiobook"""

import os
import logging
from typing import Dict, Any, cast
import json
import yaml
from .metadata_audiobook import MetadataAudiobook

logger = logging.getLogger("audiobook.metadata")


class MetadataLoader:
    """Load metadata.yml and inject data into MetadataAudiobook"""

    def __init__(self, mp3_directory: str):
        self.mp3_directory = mp3_directory
        self.yml_file: str = "metadata.yml"
        self.path = os.path.join(self.mp3_directory, self.yml_file)
        self.yml_data: Dict[str, Any] = {}

        self.__read()
        default_title = os.path.basename(self.mp3_directory.rstrip(os.sep))
        self.metadata = MetadataAudiobook(self.yml_data, default_title)

    def get_metadata_audiobook(self) -> MetadataAudiobook:
        """Return MetadataAudiobook"""
        return self.metadata

    def __read(self):
        if not os.path.exists(self.path):
            logger.info("No metadata.yml found, using defaults.")
            return self

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                if isinstance(content, dict):
                    logger.info("Successfully loaded metadata.yml")
                    self.yml_data = cast(Dict[str, Any], content)

                    return self
                return self
        except Exception as e:
            logger.warning(f"Could not parse metadata.yml: {e}")
            return self

    def __str__(self) -> str:
        return (
            f"MetadataLoader(\n"
            f"  YML file:  {self.path}\n"
            f"  {json.dumps(self.yml_data, indent=4, ensure_ascii=False)}"
            f")"
        )
