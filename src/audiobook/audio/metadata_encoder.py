import json
from mutagen.mp4 import MP4, MP4FreeForm


class MetadataEncoder(json.JSONEncoder):
    """Gère la sérialisation JSON des objets Mutagen complexes (bytes, FreeForm)."""

    def default(self, obj):
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode("utf-8", errors="ignore")
        if isinstance(obj, MP4FreeForm):
            try:
                return obj.decode("utf-8", errors="ignore")
            except:
                return str(obj)
        return super().default(obj)
