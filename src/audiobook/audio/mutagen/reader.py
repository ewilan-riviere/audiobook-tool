"""Read audio file with mutagen"""

from pathlib import Path
from typing import Optional, Union, Any, cast, Dict, List
import mutagen
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4FreeForm
from .tags_mapping import TAGS_MAPPING
from .chapter import AudioChapter
from .chapter_reader import ChapterReader


class MutagenReader:
    """Read audio file with mutagen"""

    def __init__(self, file_path: Union[str, Path]):
        self.path = Path(file_path)
        self.tags_map = TAGS_MAPPING
        data = mutagen.File(str(self.path))  # type: ignore
        if data is None:
            raise ValueError(f"Unable to read : {self.path}")
        self.audio = cast(Union[MP3, MP4], data)

    @property
    def properties(self) -> Dict[str, str | None]:
        """Get audio file properties"""
        properties: Dict[str, str | None] = {}
        info = self.audio.info

        properties["length"] = getattr(info, "length", None)
        properties["bitrate"] = getattr(info, "bitrate", None)
        properties["sample_rate"] = getattr(info, "sample_rate", None)
        properties["channels"] = getattr(info, "channels", None)

        # Format et Codec
        if isinstance(self.audio, MP3):
            properties["codec"] = "mp3"
            properties["format_type"] = "mp3"
            properties["format_label"] = "MPEG audio layer 3"
        elif isinstance(self.audio, MP4):  # type: ignore
            properties["codec"] = "aac"
            properties["format_type"] = "mov,mp4,m4a,3gp"
            properties["format_label"] = "QuickTime / MOV"

        # Layout des canaux
        if properties["channels"] == 1:
            properties["channel_layout"] = "mono"
        elif properties["channels"] == 2:
            properties["channel_layout"] = "stereo"

        return properties

    @property
    def chapters(self) -> List[AudioChapter]:
        """Get M4B chapters"""
        reader = ChapterReader(str(self.path))

        return reader.chapters

    def _extract_value(self, val: Any) -> Optional[str]:
        if val is None:
            return None

        # List/Tuple Management (Recursion)
        if isinstance(val, (list, tuple)):
            if not val:
                return None
            item = val[0]  # type: ignore
            # Specific case M4B track/disk: [(1, 10)] -> "1/10"
            if isinstance(item, tuple):
                if len(item) >= 2 and item[1] > 0:  # type: ignore
                    return f"{item[0]}/{item[1]}"
                return str(item[0])  # type: ignore

            return self._extract_value(item)

        # Specific management MP4FreeForm
        if isinstance(val, MP4FreeForm):
            data = getattr(val, "data", val)
            if isinstance(data, (bytes, bytearray)):
                return data.decode("utf-8", errors="ignore")
            return str(data)

        # ID3 Management (Objects with .text attribute)
        if hasattr(val, "text"):
            t = val.text
            # Some ID3 objects (such as COMM) have .text, but it is a list.
            if isinstance(t, list) and t:
                return str(t[0])  # type: ignore
            return str(t)  # type: ignore

        # Boolean Management (Compilation)
        if isinstance(val, bool):
            return "1" if val else "0"

        # Raw bytes
        if isinstance(val, (bytes, bytearray)):
            return val.decode("utf-8", errors="ignore")

        return str(val)

    def get_tag(self, human_key: str) -> Optional[str]:
        """Récupère la valeur d'un tag avec gestion des variantes."""
        target_dict = self.tags_map.get(human_key)
        if not target_dict:
            return None

        # We retrieve the key(s) according to the format (MP3 or MP4).
        raw_keys = (
            target_dict["mp3"] if isinstance(self.audio, MP3) else target_dict["m4b"]
        )

        # We make sure that `keys` is always a list, even if there is only one string.
        keys = [raw_keys] if isinstance(raw_keys, str) else raw_keys

        # We test each variant
        for key in keys:
            # We use `self.audio.get(key)` because key is now necessarily a string.
            value = self.audio.get(key)  # type: ignore
            if value is not None:
                extracted = self._extract_value(value)
                if extracted and extracted.strip():  # Avoid empty strings or spaces
                    if extracted == "None":
                        return None
                    return extracted

        return None

    def get_all(self) -> Dict[str, str]:
        """Returns only tags that have a value."""
        return {k: v for k in self.tags_map if (v := self.get_tag(k))}

    def get_cover(self) -> Optional[bytes]:
        """Extract the bytes from the cover"""
        # For MP3: look for the first frame that starts with 'APIC'
        if isinstance(self.audio, MP3) and self.audio.tags:  # type: ignore
            for key, tag in self.audio.tags.items():  # type: ignore
                if key.startswith("APIC"):  # type: ignore
                    return tag.data  # type: ignore

        # For MP4/M4B: retrieve the ‘covr’ atom
        elif isinstance(self.audio, MP4):
            covers = self.audio.get("covr")  # type: ignore
            if covers:
                return bytes(covers[0])  # type: ignore

        return None

    @property
    def has_cover(self) -> bool:
        """Checks for the presence of a cover via `get_cover`"""
        return bool(self.get_cover())

    def save_cover(self, output_dir: Union[str, Path, None] = None) -> Optional[Path]:
        """Saves the detected cover"""
        if not (data := self.get_cover()):
            return None

        # Path and folder management
        out = Path(output_dir or self.path.parent).expanduser()
        out.mkdir(parents=True, exist_ok=True)

        # Detect the extension (Magic Numbers)
        # JPEG begins with \xff\xd8 | PNG begins with \x89PNG
        ext = ".png" if data.startswith(b"\x89PNG") else ".jpg"
        target = out / f"{self.path.stem}{ext}"

        target.write_bytes(data)  # Replaces open().write() and handles overwriting
        return target
