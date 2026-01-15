import os
import subprocess
from typing import Any, Optional, List, Dict, Iterable
from mutagen.mp4 import MP4, MP4FreeForm, MP4Cover, MP4Tags
from audiobook.audio.types import AudioTags
from .audio_handler import AudioHandler


class M4BHandler(AudioHandler):
    def __init__(self, path: str) -> None:
        self.path: str = path

    def extract(self, data: AudioTags) -> None:
        audio = MP4(self.path)
        t: Optional[MP4Tags] = audio.tags
        if not t:
            return

        def get_m4b_str(keys: Iterable[str]) -> Optional[str]:
            for k in keys:
                if k in t:
                    # Les tags MP4 sont souvent des listes [valeur]
                    val: Any = (  # type: ignore
                        t[k][0] if isinstance(t[k], list) and len(t[k]) > 0 else t[k]  # type: ignore
                    )
                    if isinstance(val, (bytes, bytearray, MP4FreeForm)):
                        return val.decode("utf-8", errors="ignore")
                    return str(val)  # type: ignore
            return None

        # Fallbacks Description/Synopsis
        d_val: Optional[str] = get_m4b_str(["\xa9des"])
        s_val: Optional[str] = get_m4b_str(
            ["lp83", "desc", "----:com.apple.iTunes:SYNOPSIS"]
        )
        c_val: Optional[str] = get_m4b_str(["\xa9cmt"])

        if not s_val:
            s_val = d_val
        if not d_val and s_val:
            d_val = s_val[:250] + "..." if len(s_val) > 250 else s_val

        # On prépare le dictionnaire de mise à jour
        updates: Dict[str, Any] = {
            "title": get_m4b_str(["\xa9nam"]),
            "subtitle": get_m4b_str(["\xa9st3", "----:com.apple.iTunes:SUBTITLE"]),
            "artist": get_m4b_str(["\xa9ART"]),
            "album_artist": get_m4b_str(["aART"]),
            "album": get_m4b_str(["\xa9alb"]),
            "composer": get_m4b_str(["\xa9wrt"]),
            "genre": get_m4b_str(["\xa9gen"]),
            "year": get_m4b_str(["\xa9day"]),
            "comment": c_val,
            "description": d_val,
            "synopsis": s_val,
            "language": get_m4b_str(["\xa9lan", "----:com.apple.iTunes:LANGUAGE"]),
            "copyright": get_m4b_str(["cprt"]),
            "publisher": get_m4b_str(["\xa9pub"]),
            "compilation": self._get_cpil_safe(t),
        }
        data.update(updates)  # type: ignore

        # Deep Scan & Track/Disc
        # Utilisation de tuples pour le mapping
        meta_fields: List[tuple[str, str]] = [("track", "trkn"), ("disc", "disk")]
        for field, tag in meta_fields:
            if tag in t:
                v = t[tag][0]  # type: ignore
                if isinstance(v, tuple) and len(v) >= 2 and v[0] > 0:  # type: ignore
                    data[field] = f"{v[0]}/{v[1]}"

        for k in t.keys():  # type: ignore
            if k.startswith("----:com.apple.iTunes:"):  # type: ignore
                atom: str = k.split(":")[-1].upper()  # type: ignore
                val_str: Optional[str] = get_m4b_str([k])  # type: ignore
                if atom in ["SERIES", "WORK"]:
                    data["series"] = val_str
                elif atom in ["SERIES-PART", "MOVEMENT-NUMBER"]:
                    data["series_part"] = val_str
                elif atom == "ISBN":
                    data["isbn"] = val_str
                elif atom == "ASIN":
                    data["asin"] = val_str

    def _get_cpil_safe(self, t: MP4Tags) -> bool:
        if "cpil" in t:
            v: Any = t["cpil"]  # type: ignore
            return bool(v[0]) if isinstance(v, list) and v else bool(v)  # type: ignore
        return False

    def inject(self, d: AudioTags) -> None:
        meta_file: str = f"{self.path}.ffmeta"
        temp_file: str = f"{self.path}.tmp.m4b"
        try:
            # 1. FFmpeg (Chapitres)
            with open(meta_file, "w", encoding="utf-8") as f:
                f.write(";FFMETADATA1\n")
                chapters: List[Dict[str, Any]] = d.get("chapters", [])  # type: ignore
                for ch in chapters:
                    f.write(
                        f"\n[CHAPTER]\nTIMEBASE={ch['time_base']}\n"
                        f"START={ch['start']}\nEND={ch['end']}\ntitle={ch['title']}\n"
                    )

            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    self.path,
                    "-i",
                    meta_file,
                    "-map_metadata",
                    "1",
                    "-map_chapters",
                    "1",
                    "-c",
                    "copy",
                    temp_file,
                    "-y",
                ],
                capture_output=True,
                check=True,
            )
            os.replace(temp_file, self.path)

            # 2. Mutagen (Tous les Tags)
            audio = MP4(self.path)
            t: Optional[MP4Tags] = audio.tags
            if t is None:
                audio.add_tags()
                t = audio.tags

            # On force l'existence de t pour le linter après add_tags()
            assert t is not None

            # Tags standards (Castés en string pour éviter le type Unknown)
            t["\xa9nam"] = [str(d.get("title") or "")]
            t["\xa9ART"] = [str(d.get("artist") or "")]
            t["aART"] = [str(d.get("album_artist") or "")]
            t["\xa9alb"] = [str(d.get("album") or "")]
            t["\xa9wrt"] = [str(d.get("composer") or "")]
            t["\xa9gen"] = [str(d.get("genre") or "")]
            t["\xa9day"] = [str(d.get("year") or "")]
            t["\xa9cmt"] = [str(d.get("comment") or "")]
            t["cprt"] = [str(d.get("copyright") or "")]
            t["\xa9pub"] = [str(d.get("publisher") or "")]
            t["\xa9lan"] = [str(d.get("language") or "")]
            t["cpil"] = [bool(d.get("compilation"))]

            # Track / Disc
            track_mapping: List[tuple[str, str]] = [("track", "trkn"), ("disc", "disk")]
            for field, tag in track_mapping:
                val: Any = d.get(field)
                if val:
                    try:
                        str_val = str(val)
                        if "/" in str_val:
                            curr, tot = str_val.split("/")
                            t[tag] = [(int(curr), int(tot))]
                        else:
                            t[tag] = [(int(str_val), 0)]
                    except (ValueError, TypeError):
                        pass

            if d.get("subtitle"):
                sub: str = str(d["subtitle"])
                t["\xa9st3"] = [sub]
                t["----:com.apple.iTunes:SUBTITLE"] = [sub.encode()]

            if d.get("synopsis"):
                s: str = str(d["synopsis"])
                t["lp83"] = [s]
                t["desc"] = [s]
                t["\xa9des"] = [s[:250] + "..." if len(s) > 250 else s]

            for key in ["series", "series_part", "isbn", "asin"]:
                val_custom = d.get(key)
                if val_custom:
                    atom_key = f"----:com.apple.iTunes:{key.upper().replace('_', '-')}"
                    t[atom_key] = [str(val_custom).encode()]

            audio.save()  # type: ignore
        finally:
            for f_path in [meta_file, temp_file]:
                if os.path.exists(f_path):
                    os.remove(f_path)

    def extract_cover(self) -> Optional[bytes]:
        audio = MP4(self.path)
        if not audio.tags or "covr" not in audio.tags:
            return None
        # Retourne le binaire brut de la première image trouvée
        return bytes(audio.tags["covr"][0])  # type: ignore

    def inject_cover(self, img_data: bytes) -> bool:
        audio = MP4(self.path)
        t = audio.tags
        if t is None:
            audio.add_tags()
            t = audio.tags

        assert t is not None

        # Détection du format pour l'énumération MP4
        fmt = MP4Cover.FORMAT_JPEG
        if img_data.startswith(b"\x89PNG\r\n\x1a\n"):
            fmt = MP4Cover.FORMAT_PNG

        t["covr"] = [MP4Cover(img_data, imageformat=fmt)]
        audio.save()  # type: ignore
        return True

    def has_cover(self) -> bool:
        try:
            audio = MP4(self.path)
            return audio.tags is not None and "covr" in audio.tags
        except Exception:
            return False
