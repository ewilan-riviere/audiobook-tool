"""Read metadata from YML file"""

from __future__ import annotations
import logging
from typing import Any, cast, TYPE_CHECKING
from pathlib import Path
import yaml
from audiobook.common import AutoRepr


if TYPE_CHECKING:
    from audiobook.models import MetadataAudiobook
    from audiobook.models import M4bAudiobook


logger = logging.getLogger("audiobook.metadata")


class YmlReader(AutoRepr):
    """Read metadata from YML file"""

    def __init__(self, yml_path: str | Path | None):
        if not yml_path:
            raise FileNotFoundError("`yml_path` have to be not empty")

        self.yml_path = Path(yml_path).resolve()
        if not self.yml_path.exists():
            logger.info("No metadata.yml found, using defaults.")

        self.yml_data: dict[str, Any] = {}
        self.default_title = self._handle_default_title()
        self.metadata: MetadataAudiobook | None = None

    def to_audiobook(self) -> M4bAudiobook:
        """Convert metadata.yml to M4bAudiobook"""
        # pylint: disable=import-outside-toplevel
        from audiobook.models import M4bAudiobook

        m4b = M4bAudiobook()
        m4b.title = self.default_title

        if not self.metadata:
            return m4b

        m4b.title = self.metadata.title
        m4b.album = self.metadata.title
        m4b.artist = self.metadata.authors
        m4b.album_artist = self.metadata.authors
        m4b.composer = self.metadata.narrators
        m4b.genre = self.metadata.genres
        m4b.date = str(self.metadata.year) if self.metadata.year else None
        m4b.copyright_ = self.metadata.copyright_
        m4b.comment = None
        m4b.description = self.metadata.description
        m4b.synopsis = self.metadata.description
        m4b.compilation = None
        m4b.lyrics = self.metadata.lyrics
        m4b.publisher = self.metadata.publisher
        m4b.language = self.metadata.language
        m4b.series = self.metadata.series
        m4b.series_part = str(self.metadata.volume) if self.metadata.volume else None
        m4b.subtitle = self.metadata.subtitle
        m4b.isbn = None
        m4b.asin = self.metadata.asin

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

        if self.yml_data:
            # pylint: disable=import-outside-toplevel
            from audiobook.models import MetadataAudiobook

            self.metadata = MetadataAudiobook(self.yml_data, self.default_title)

        return self

    def _handle_default_title(self) -> str:
        if not self.yml_path:
            return "audiobook"

        default_parent_name = self.yml_path.parent.name
        if default_parent_name == "":
            return "Unknown"

        return default_parent_name
