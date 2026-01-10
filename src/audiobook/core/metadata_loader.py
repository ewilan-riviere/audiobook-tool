import os
import logging
from typing import Dict, Any, cast
import yaml
from audiobook.models import AudiobookMetadata

logger = logging.getLogger("audiobook.metadata")


class MetadataLoader:
    def __init__(self, mp3_directory: str):
        self.mp3_directory = mp3_directory
        self.yml_file: str = "metadata.yml"
        self.path = os.path.join(self.mp3_directory, self.yml_file)
        self.yml: Dict[str, Any] = {}

        self.__read()
        default_title = os.path.basename(self.mp3_directory.rstrip(os.sep))
        self.metadata = AudiobookMetadata(self.yml, default_title)

    def __read(self):
        if not os.path.exists(self.path):
            logger.info("No metadata.yml found, using defaults.")
            return self

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                if isinstance(content, dict):
                    logger.info("Successfully loaded metadata.yml")
                    self.yml = cast(Dict[str, Any], content)

                    return self
                return self
        except Exception as e:
            logger.warning(f"Could not parse metadata.yml: {e}")
            return self
