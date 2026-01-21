"""Write metadata into YML file"""

from pathlib import Path
from typing import Any
import yaml
from audiobook.audible import AudibleMetadata
import audiobook.utils as utils


class AudibleYml:
    """Write metadata into YML file"""

    def __init__(self, audiobook: AudibleMetadata):
        self._yml_path = utils.path_join(str(Path.home()), "Downloads")

        data: dict[Any, Any] = {
            "title": audiobook.title,
            "authors": audiobook.get_authors(),
            "description": audiobook.description,
            "lyrics": None,
            "copyright": None,
            "genres": None,
            "series": None,
            "volume": None,
            "language": audiobook.get_language(),
            "year": audiobook.get_year(),
            "publisher": audiobook.publisher,
            "subtitle": None,
            "isbn": None,
            "asin": audiobook.asin,
        }

        with open(
            utils.path_join(self._yml_path, "metadata.yml"),
            "w",
            encoding="utf-8",
        ) as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
