"""Read metadata from YML file"""

import os
import logging
from audiobook.common import AutoRepr
from typing import Any, cast
import yaml
from ..audiobook import AudibleAudiobook

logger = logging.getLogger("audiobook.metadata")


class YmlReader(AutoRepr):
    """Read metadata from YML file"""

    def __init__(self, yml_path: str | None):
        if not yml_path or not os.path.exists(yml_path):
            logger.info("No metadata.yml found, using defaults.")

        self.yml_path = yml_path
        self.yml_data: dict[str, Any] = {}
        self.default_title = self._handle_default_title()

        self._read()
        # self.metadata = MetadataAudiobook(self.yml_data, self.default_title)

    @property
    def audiobook(self) -> AudibleAudiobook:
        audiobook = AudibleAudiobook(self.yml_data.get("asin"))

        audiobook.title = self.yml_data.get("title") or self.default_title

        return audiobook

    def _handle_default_title(self) -> str:
        if not self.yml_path:
            return "audiobook"

        return os.path.basename(self.yml_path.rstrip(os.sep))

    def _read(self):
        if not self.yml_path:
            return self

        try:
            with open(self.yml_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                if isinstance(content, dict):
                    self.yml_data = cast(dict[str, Any], content)
        except Exception as e:
            logger.warning("Could not parse metadata.yml: %s", e)

        return self
