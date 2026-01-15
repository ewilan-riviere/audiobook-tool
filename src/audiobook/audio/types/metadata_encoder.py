import json
from typing import Any
from mutagen.mp4 import MP4FreeForm


class MetadataEncoder(json.JSONEncoder):
    """Gère la sérialisation JSON des objets Mutagen complexes (bytes, FreeForm)."""

    def default(self, o: Any) -> Any:
        if isinstance(o, (bytes, bytearray)):
            return o.decode("utf-8", errors="ignore")

        if isinstance(o, MP4FreeForm):
            try:
                return o.decode("utf-8", errors="ignore")
            except Exception:
                return str(o)

        return super().default(o)
