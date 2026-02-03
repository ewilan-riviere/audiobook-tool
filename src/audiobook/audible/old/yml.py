"""Write metadata into YML file"""

from pathlib import Path
from typing import Any
import yaml
from audiobook.audible import AudibleMetadata
import audiobook.utils as utils


class BlockStyleDumper(yaml.SafeDumper):
    """Dumper personnalisé pour forcer le style bloc sur les chaînes multilignes."""

    def represent_scalar(
        self, tag: str, value: Any, style: Any = None
    ) -> yaml.ScalarNode:
        # Si la valeur contient un saut de ligne, on FORCE le style '|'
        if isinstance(value, str) and "\n" in value:
            style = "|"
        return super().represent_scalar(tag, value, style)  # type: ignore


class AudibleYml:
    """Write metadata into YML file"""

    def __init__(self, audiobook: AudibleMetadata, output_path: str | None = None):
        if not output_path:
            self._yml_path = str(Path.cwd())
        else:
            self._yml_path = output_path

        data: dict[Any, Any] = {
            "title": audiobook.title,
            "authors": audiobook.get_authors(),
            "narrators": audiobook.get_narrators(),
            "description": audiobook.description,
            "lyrics": None,
            "copyright": audiobook.copyright,
            "genres": audiobook.get_genres(),
            "series": audiobook.series,
            "volume": audiobook.volume,
            "language": audiobook.get_language(),
            "year": audiobook.get_year(),
            "publisher": audiobook.publisher,
            "subtitle": audiobook.subtitle,
            "isbn": None,
            "asin": audiobook.asin,
        }

        with open(
            utils.path_join(self._yml_path, "metadata.yml"),
            "w",
            encoding="utf-8",
        ) as f:
            yaml.dump(
                data,
                f,
                Dumper=BlockStyleDumper,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
                width=1000,  # Empêche le dumper de couper les lignes au milieu
            )
