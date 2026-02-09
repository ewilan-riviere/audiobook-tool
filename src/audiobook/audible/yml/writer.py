"""Write metadata into YML file"""

import os
from pathlib import Path
import yaml
from ..audiobook import AudibleAudiobook
from .block_style import BlockStyleDumper


class YmlWriter:
    """Write metadata into YML file"""

    def __init__(self, audiobook: AudibleAudiobook, save_path: str):
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        save_path = os.path.join(save_path, "metadata.yml")
        real_path = Path(save_path).resolve()

        data: dict[str, str | int | float | None] = {
            "title": audiobook.title_clean,
            "authors": audiobook.authors_list,
            "narrators": audiobook.narrators_list,
            "description": audiobook.description,
            "lyrics": None,
            "copyright": audiobook.copyright,
            "genres": audiobook.genres_list,
            "series": audiobook.series_clean,
            "volume": audiobook.volume_clean,
            "language": audiobook.language,
            "year": audiobook.year,
            "publisher": audiobook.publisher,
            "subtitle": audiobook.subtitle,
            "isbn": None,
            "asin": audiobook.asin,
        }

        with open(
            real_path,
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

        print(f"Success: metadata.yml saved as `{real_path}`")

        self.save_path = real_path
