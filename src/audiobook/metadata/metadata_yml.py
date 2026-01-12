"""Load metadata.yml and inject data into MetadataAudiobook"""

import os
import logging
from typing import Dict, Any, cast
import json
import yaml
from .metadata_audiobook import MetadataAudiobook

logger = logging.getLogger("audiobook.metadata")


class MetadataYml:
    """Load metadata.yml and inject data into MetadataAudiobook"""

    def __init__(self, yml_path: str | None):
        if not yml_path or not os.path.exists(yml_path):
            logger.info("No metadata.yml found, using defaults.")
            if yml_path:
                self.default_title = self._handle_default_title(yml_path)
            else:
                self.default_title = "audiobook"
            return

        self.yml_path = yml_path
        self.yml_data: Dict[str, Any] = {}

        self._read()
        self.default_title = self._handle_default_title(yml_path)
        self.metadata = MetadataAudiobook(self.yml_data, self.default_title)

    def get_yml(self) -> MetadataAudiobook:
        """Return MetadataAudiobook"""
        return self.metadata

    def _handle_default_title(self, yml_path: str):
        return os.path.basename(yml_path.rstrip(os.sep))

    def _read(self):

        try:
            with open(self.yml_path, "r", encoding="utf-8") as f:
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
            f"  yml_path:  {self.yml_path}\n"
            f"  default_title:  {self.default_title}\n"
            f"  {json.dumps(self.yml_data, indent=4, ensure_ascii=False)}"
            f")"
        )
