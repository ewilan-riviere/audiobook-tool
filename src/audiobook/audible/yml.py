import yaml
from pathlib import Path
from typing import Any
import audiobook.utils as utils


class AudibleYml:
    def __init__(self):
        self._yml_path = utils.path_join(str(Path.home()), "Downloads")

        data: dict[Any, Any] = {
            "config": {"version": 1.2, "debug": True, "langue": "français"},
            "users": ["Alice", "Bob", "Charlie"],
        }

        with open(
            utils.path_join(self._yml_path, "config.yaml"),
            "w",
            encoding="utf-8",
        ) as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
